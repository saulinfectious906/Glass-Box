import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import time

# --- 1. CONFIGURATION ---
# Replace with your actual key
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to []. Use clinical, deterministic logic."

class EpistemicGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading High-Resolution Embedding Model (bge-base-en-v1.5)... ---")
        # Using the high-quality model from Index8
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        
        self.anchor_vector = None
        self.previous_vector = None
        self.exchange_depth = 0
        self.phi = 1.0
        
        # HISTORY BUFFER: Allows us to "Soft Reset" (Rewind) instead of "Hard Reset" (Nuke)
        self.context_history = [] 

        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_interactive_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Anchor_Sim", "Prev_Sim", "Decay", "Action"])

    def update_anchor(self, user_prompt):
        """
        CRITICAL UPGRADE: Called when the user enters a NEW prompt. 
        We establish a new 'Truth' for this specific turn.
        """
        print(f"\n--- [SYSTEM]: Calibrating New Anchor for: '{user_prompt}'... ---")
        
        # 1. Generate the Ideal Output (The Dynamic Anchor from Index7)
        anchor_prompt = (
            f"Write a Python script that technically analyzes: {user_prompt}. "
            f"Ensure the logic adheres to: {PRIMARY_CONSTRAINT}. "
            "Use comments to explain the science. Output code only."
        )
        try:
            anchor_text = model.generate_content(anchor_prompt).text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
            
            # 2. Reset 'Previous Vector' so we don't punish the new topic for being different
            # This fixes the "Death Spiral" seen in Index8 logs.
            self.previous_vector = None
            print("--- [SYSTEM]: Trajectory Locked. ---")
        except Exception as e:
            print(f"--- [ERROR]: Failed to generate anchor: {e} ---")

    def calculate_phi(self, text, step):
        self.exchange_depth = step
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        
        # 1. Anchor Similarity (Are we answering the CURRENT question?)
        if self.anchor_vector is not None:
            anchor_sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        else:
            anchor_sim = 1.0 # Safety default
            
        # 2. Repetition Check (Are we looping?)
        prev_sim = 0.0
        if self.previous_vector is not None:
            prev_sim = cosine_similarity(current_vec, self.previous_vector)[0][0]
        
        self.previous_vector = current_vec

        # Physics
        drift_factor = 1.0 - anchor_sim
        dna_decay = (self.exchange_depth * 0.005) 
        
        # Repetition Penalty: Only punish if it's IDENTICAL (looping), not just similar context
        # In Index8, this was too aggressive (0.95). We bumped it to 0.98.
        repetition_penalty = 0.5 if prev_sim > 0.98 else 0.0

        self.phi = max(0.0, (anchor_sim - dna_decay - repetition_penalty) + 0.10)
        
        self._log_vitals(anchor_sim, prev_sim, dna_decay, repetition_penalty)
        return self.phi

    def _log_vitals(self, anchor_sim, prev_sim, decay, rep_pen):
        action = "STABLE"
        if self.phi < 0.60: action = "INTERVENTION"
        
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{anchor_sim:.4f}", f"{prev_sim:.4f}", f"{decay:.4f}", action])
        
        print(f"[AUDIT] Phi: {self.phi:.4f} | Anchor Sim: {anchor_sim:.4f} | Prev Sim: {prev_sim:.4f}")

    def soft_reset(self):
        """
        THE FIX: Instead of clearing everything, we just remove the last bad turn.
        """
        print("--- [INTERVENTION]: SOFT RESET (Rewinding Context) ---")
        if len(self.context_history) > 1:
            # Remove the last bad exchange
            self.context_history.pop()
            # Return the last GOOD response to re-ground the model
            return self.context_history[-1]['response'] 
        else:
            return "" # Full reset if we are at the start

# --- 2. THE INTERACTIVE LOOP ---
def run_interactive_session():
    governor = EpistemicGovernor()
    
    # Initial state
    current_context = ""
    print("\n--- EPISTEMIC GOVERNOR V8.1 ONLINE (Interactive Mode) ---")
    print("Type 'exit' to quit. Type 'reset' to clear memory.\n")

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']:
            break
        if user_input.lower() == 'reset':
            governor.context_history = []
            current_context = ""
            print("--- MEMORY CLEARED ---")
            continue

        # 1. Update the Anchor for this NEW input (Rolling Anchor)
        governor.update_anchor(user_input)
        
        # 2. Build the Prompt (Context + New Input)
        # We explicitly separate History from Current Task to help the model distinction
        full_prompt = (
            f"Context History: {current_context}\n"
            f"Current User Request: {user_input}\n"
            f"Constraint: {PRIMARY_CONSTRAINT}\n"
            "Output: Python Code Only."
        )

        # 3. Generation & Audit Loop
        attempts = 0
        while attempts < 3:
            try:
                response = model.generate_content(full_prompt).text
                
                # Check Phi
                phi = governor.calculate_phi(response, len(governor.context_history))
                
                if phi > 0.60:
                    # SUCCESS: Print it and save to history
                    print(f"\nGOVERNOR >>>\n{response}")
                    
                    # Update Context (Sliding Window)
                    current_context += f"\nUser: {user_input}\nAI: {response}"
                    governor.context_history.append({'user': user_input, 'response': response})
                    break
                
                else:
                    # FAILURE: Trigger Soft Reset
                    print("--- [GOVERNOR]: Low Fidelity Detected. Regenerating... ---")
                    # We do NOT add this to context. We try again with a stricter prompt.
                    full_prompt += "\nCRITICAL INSTRUCTION: Your last output deviated from the logic. RE-ALIGN."
                    attempts += 1
                    
            except Exception as e:
                print(f"Error: {e}")
                break
        
        if attempts == 3:
            print("\n[GOVERNOR]: UNABLE TO MAINTAIN FIDELITY. TERMINATING TURN.")
            # Trigger the Soft Reset to clean up any mess
            current_context = governor.soft_reset()

# Run it
if __name__ == "__main__":
    run_interactive_session()
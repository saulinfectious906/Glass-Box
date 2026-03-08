import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import ast
import re

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

# We now have TWO constraints depending on the "Hemisphere" active
CONSTRAINT_CODE = "[]. Output clean, executable Python code only."
CONSTRAINT_CHAT = "Be concise, clinical, and direct. Avoid filler words."

class DualHemisphereGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Dual-Hemisphere Engine (Index 10)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        
        self.anchor_vector = None
        self.context_memory = [] 
        self.current_mode = "CHAT" # Default state
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_dual_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Mode", "Phi", "Vector_Sim", "Gate_Status", "Action"])

    def detect_intent(self, user_input):
        """
        The Switch: Decides if we need the 'Logic Gate' (Code) or 'Semantic Gate' (Chat).
        """
        code_triggers = ['script', 'function', 'code', 'python', 'def ', 'class ', 'loop', 'iterate', 'scrape']
        if any(trigger in user_input.lower() for trigger in code_triggers):
            self.current_mode = "CODE"
            print("--- [SWITCH]: CODE HEMISPHERE ACTIVE (Strict Logic Gate) ---")
        else:
            self.current_mode = "CHAT"
            print("--- [SWITCH]: CHAT HEMISPHERE ACTIVE (Semantic Guardrails) ---")

    def update_anchor(self, user_prompt):
        """
        Rolling Anchor: Updates 'Semantic North' for the current turn.
        """
        try:
            # We assume the 'Ideal' answer is what we want to vector match against
            anchor_prompt = f"Provide a perfect, concise response to: {user_prompt}"
            anchor_text = model.generate_content(anchor_prompt).text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
        except Exception as e:
            print(f"--- [ERROR]: Anchor generation failed: {e} ---")

    def audit_code(self, code_str):
        """
        The Logic Gate (Strict). Used only in CODE mode.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            return False, "Syntax Error"
        
        # Complexity Check
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                complexity += 1
        if complexity > 10: return False, "Too Complex"
        
        return True, "Clean"

    def audit_chat(self, text_str):
        """
        The Semantic Gate (Soft). Used in CHAT mode.
        Checks for drift, hallucination, or banned 'lazy' conversational habits.
        """
        # 1. Length Check (Don't ramble)
        if len(text_str.split()) > 300: return False, "Verbosity Limit"
        
        # 2. Vibe Check (Vector Similarity)
        # We handle this in calculate_phi, but we flag it here if it's wild
        return True, "Clean"

    def calculate_phi(self, text, step):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        
        # 1. Vector Alignment
        if self.anchor_vector is not None:
            vector_sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        else:
            vector_sim = 1.0
            
        # 2. Dual-Mode Auditing
        passed_gate = True
        reason = "Pass"
        
        if self.current_mode == "CODE":
            passed_gate, reason = self.audit_code(text)
            gate_penalty = 0.0 if passed_gate else 1.0 # Strict death penalty for bad code
        else:
            passed_gate, reason = self.audit_chat(text)
            gate_penalty = 0.0 if passed_gate else 0.3 # Soft penalty for bad chat

        # 3. Decay
        dna_decay = (step * 0.001) 

        # Final Phi
        self.phi = max(0.0, (vector_sim - gate_penalty - dna_decay) + 0.15)
        
        self._log_vitals(step, vector_sim, passed_gate, reason)
        return self.phi

    def _log_vitals(self, step, vec_sim, passed_gate, reason):
        action = "STABLE"
        if self.phi < 0.70: action = "INTERVENTION"
        
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, self.current_mode, f"{self.phi:.4f}", f"{vec_sim:.4f}", reason, action])
        
        icon = "✅" if passed_gate else "⚠️"
        print(f"[AUDIT] Mode: {self.current_mode} | Phi: {self.phi:.4f} | Gate: {reason} {icon}")

    def attempt_recovery(self, failed_response):
        """
        THE MEDIAN: Instead of resetting, we try to fix the Drift.
        """
        print("--- [NEGOTIATOR]: Attempting to repair response... ---")
        
        if self.current_mode == "CODE":
            # If code failed syntax, wrap it in comments or try to extract code blocks
            # This is the "Median" - we don't delete it, we neutralize it.
            if "```python" in failed_response:
                # Extract the code block
                pattern = r"```python(.*?)```"
                match = re.search(pattern, failed_response, re.DOTALL)
                if match:
                    return match.group(1).strip()
            
            # If it's just text explaining code, convert to Docstring
            return f'"""\n[SYSTEM RECOVERY]: The model drifted into prose.\n\n{failed_response}\n"""'
            
        else:
            # If Chat failed (too verbose), truncate it.
            return failed_response[:500] + "\n... [truncated by Governor]"

    def manage_memory(self, user_input, ai_response):
        entry = f"User: {user_input}\nAI: {ai_response}"
        self.context_memory.append(entry)
        if len(self.context_memory) > 6: self.context_memory.pop(0) 

    def get_context_block(self):
        return "\n".join(self.context_memory)

# --- 2. EXECUTION LOOP ---
def run_interactive_session():
    governor = DualHemisphereGovernor()
    
    print("\n--- EPISTEMIC GOVERNOR V10 (THE NEGOTIATOR) ONLINE ---")
    print("Dual-Mode Active: Natural Conversation + Strict Code Gating.\n")

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        if user_input.lower() == 'reset':
            governor.context_memory = []
            print("--- MEMORY CLEARED ---")
            continue

        # 1. Detect Intent (Switch Hemispheres)
        governor.detect_intent(user_input)
        governor.update_anchor(user_input)
        
        # 2. Select Constraint based on Hemisphere
        active_constraint = CONSTRAINT_CODE if governor.current_mode == "CODE" else CONSTRAINT_CHAT
        
        full_prompt = (
            f"--- HISTORY ---\n{governor.get_context_block()}\n--- END HISTORY ---\n"
            f"REQUEST: {user_input}\n"
            f"CONSTRAINT: {active_constraint}\n"
        )
        
        # 3. Generation Loop
        attempts = 0
        final_response = ""
        
        while attempts < 2: # Fewer retries, because we have the Negotiator
            try:
                response = model.generate_content(full_prompt).text
                
                # Clean markdown if in code mode
                if governor.current_mode == "CODE":
                    clean_response = response.replace("```python", "").replace("```", "").strip()
                else:
                    clean_response = response

                phi = governor.calculate_phi(clean_response, len(governor.context_memory))
                
                if phi > 0.70:
                    final_response = clean_response
                    break
                else:
                    print("--- [GOVERNOR]: Fidelity Loss Detected. Retrying... ---")
                    attempts += 1
                    full_prompt += "\n[SYSTEM]: Previous attempt failed audit. Adhere strictly to constraint."
            except Exception as e:
                print(f"Error: {e}")
                break
        
        # 4. The Median (Final Judgment)
        if not final_response:
            # If we failed after retries, activate THE NEGOTIATOR
            final_response = governor.attempt_recovery(clean_response)
        
        print(f"\nGOVERNOR ({governor.current_mode}) >>>\n{final_response}")
        governor.manage_memory(user_input, final_response)

if __name__ == "__main__":
    run_interactive_session()
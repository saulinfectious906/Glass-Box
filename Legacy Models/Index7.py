import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to Alabama Extension soil standards. Use clinical, deterministic logic."

class EpistemicGovernor:
    def __init__(self, user_prompt, run_type):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.run_type = run_type
        
        # --- THE DYNAMIC FIX ---
        # Instead of a hardcoded string, we generate the anchor from the prompt itself.
        print(f"--- [SYSTEM]: Generating Dynamic Anchor for '{user_prompt}'... ---")
        self.anchor_vector = self._generate_dynamic_anchor(user_prompt)
        
        self.exchange_depth = 0
        self.phi = 1.0
        
        # Initialize Logging
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_{run_type}_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Similarity", "DNA_Decay", "Intervention"])

    def _generate_dynamic_anchor(self, prompt):
        # We ask the model for the "Platonic Ideal" of the answer first.
        # This becomes the Semantic North.
        anchor_prompt = f"Provide a comprehensive, clinical, and fact-based summary of: {prompt}. Do not be conversational. State the facts only."
        response = model.generate_content(anchor_prompt).text
        print(f"--- [SYSTEM]: Anchor Generated. Vectorizing... ---")
        return self.embedder.encode([response]).reshape(1, -1)

    def _get_embedding(self, text):
        return self.embedder.encode([text]).reshape(1, -1)

    def calculate_phi(self, text, step, silent=True):
        self.exchange_depth = step
        current_vec = self._get_embedding(text)
        
        # Compare against the DYNAMIC Anchor
        similarity = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        
        # Index 6.1 Physics (Calibrated)
        drift_factor = 1.0 - similarity
        dna_decay = (self.exchange_depth * 0.0015) + (drift_factor * 0.2)
        
        # Calibration Constant (tuned for local embeddings)
        self.phi = max(0.0, (similarity - dna_decay) + 0.15)
        
        self._log_vitals(similarity, dna_decay, silent)
        return self.phi

    def _log_vitals(self, sim, decay, silent):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{sim:.4f}", f"{decay:.4f}", 0])
        
        if not silent:
            print(f"\n[ANCHOR AUDIT] Step {self.exchange_depth} | Similarity: {sim:.4f} | Phi: {self.phi:.4f}")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: EMERGENCY RESET (Returning to Dynamic Anchor) ---")
        return 0 

def run_stress_test(iterations=100, managed=False):
    # NOW WE CAN CHANGE THIS PROMPT TO ANYTHING!
    original_prompt = "Analyze why the Alabama Black Belt's volcanic soil requires high nitrate inputs."
    
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    local_step = 0
    
    print(f"\n--- STARTING {run_label} RUN (Index 7.0: Dynamic Anchoring) ---")
    
    for i in range(iterations):
        if managed and governor.phi < 0.55: 
            local_step = governor.anchor_refresh()
            current_context = original_prompt 

        instruction = f"\n[GOVERNOR]: Generate Python syntax only. {PRIMARY_CONSTRAINT}" if managed else "Provide a natural language summary."
        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            phi = governor.calculate_phi(response, local_step, silent=(i % 10 != 0))
            current_context = response
            local_step += 1
        except Exception as e:
            print(f"Step {i} Error: {e}")
            break

# --- 2. EXECUTION ---
run_stress_test(iterations=100, managed=True)
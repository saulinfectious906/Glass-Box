import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import time

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to []. Use clinical, deterministic logic."

class EpistemicGovernor:
    def __init__(self, user_prompt, run_type):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.run_type = run_type
        
        # --- THE DYNAMIC FIX ---
        print(f"--- [SYSTEM]: Generating Isomorphic Anchor for '{user_prompt}'... ---")
        self.anchor_vector = self._generate_dynamic_anchor(user_prompt)
        
        self.exchange_depth = 0
        self.phi = 1.0
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_{run_type}_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Similarity", "DNA_Decay", "Intervention"])

    def _generate_dynamic_anchor(self, prompt):
        # Generating a "Gold Standard" in the target format (Python)
        anchor_prompt = (
            f"Write a Python script that technically analyzes: {prompt}. "
            f"Ensure the logic adheres to: {PRIMARY_CONSTRAINT}. "
            "Use comments to explain the science. Output code only."
        )
        response = model.generate_content(anchor_prompt).text
        return self.embedder.encode([response]).reshape(1, -1)

    def _get_embedding(self, text):
        return self.embedder.encode([text]).reshape(1, -1)

    def calculate_phi(self, text, step, silent=True):
        self.exchange_depth = step
        current_vec = self._get_embedding(text)
        
        similarity = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        
        # Physics: Linear Decay + Drift
        drift_factor = 1.0 - similarity
        dna_decay = (self.exchange_depth * 0.0015) + (drift_factor * 0.2)
        
        # Calibration: +0.10 because Code-to-Code similarity is strict
        self.phi = max(0.0, (similarity - dna_decay) + 0.10)
        
        self._log_vitals(similarity, dna_decay, silent)
        return self.phi

    def _log_vitals(self, sim, decay, silent):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{sim:.4f}", f"{decay:.4f}", 0])
        
        if not silent:
            status = "STABLE" if self.phi > 0.55 else "CRITICAL"
            print(f"\n[ANCHOR AUDIT] Step {self.exchange_depth} | Sim: {sim:.4f} | Phi: {self.phi:.4f} ({status})")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: EMERGENCY RESET (Returning to Isomorphic Anchor) ---")
        return 0 

def run_stress_test(iterations=100, managed=False):
    original_prompt = "Analyze why []."
    
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    local_step = 0
    
    print(f"\n--- STARTING {run_label} RUN (Index 7.1: Isomorphic Anchoring) ---")
    
    for i in range(iterations):
        if managed and governor.phi < 0.55: 
            local_step = governor.anchor_refresh()
            current_context = original_prompt 

        instruction = f"\n[GOVERNOR]: Generate Python syntax only. {PRIMARY_CONSTRAINT}" if managed else "Provide a natural language summary."
        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            # Print every 5 steps so you can see the Sawtooth clearly
            phi = governor.calculate_phi(response, local_step, silent=(i % 5 != 0))
            current_context = response
            local_step += 1
            time.sleep(1) # Tiny sleep to prevent rate limiting on the Gemini side
        except Exception as e:
            print(f"Step {i} Error: {e}")
            break

# --- 2. EXECUTION ---
run_stress_test(iterations=100, managed=True)
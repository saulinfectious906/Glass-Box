import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import os

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to []. Use clinical, deterministic logic."

class EpistemicGovernor:
    def __init__(self, original_prompt, run_type):
        self.exchange_depth = 0
        self.phi = 1.0
        self.run_type = run_type
        
        # ROOT FIX 1: Local Physics (Option 1)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # ROOT FIX 2: Semantic Corridor (Multi-point Anchoring)
        self.anchor_pool = [self._get_embedding(original_prompt)]
        self.max_anchor_pool = 3 
        
        # Initialize Logging
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_{run_type}_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Similarity", "DNA_Decay", "Syntax_Pen", "Intervention"])

    def _get_embedding(self, text):
        return self.embedder.encode([text]).reshape(1, -1)

    def calculate_phi(self, text, step, silent=True):
        self.exchange_depth = step
        current_vec = self._get_embedding(text)
        
        # ROOT FIX 2 (Cont.): Calculate similarity against the BEST point in our Corridor
        similarities = [cosine_similarity(current_vec, a)[0][0] for a in self.anchor_pool]
        similarity = max(similarities)
        
        # ROOT FIX 3: Dampened Physics (Realistic but stable)
        drift_factor = 1.0 - similarity
        dna_decay = (self.exchange_depth * 0.0015) + (drift_factor * 0.4) # Linearized drift weight
        
        syntax_penalty = 0.0 if ("import" in text or "print" in text) else 0.2

        self.phi = max(0.0, (similarity - dna_decay - (syntax_penalty * 0.5)))
        
        # Update Corridor: If the response is high-quality, it becomes a new anchor
        if self.phi > 0.82 and self.run_type == "MANAGED":
            self.anchor_pool.append(current_vec)
            if len(self.anchor_pool) > self.max_anchor_pool:
                self.anchor_pool.pop(1) # Keep the original [0] and the newest [2]

        self._log_vitals(similarity, dna_decay, syntax_penalty, silent)
        return self.phi

    def _log_vitals(self, sim, decay, syntax, silent):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{sim:.4f}", f"{decay:.4f}", syntax, 0])
        
        if not silent:
            print(f"\n[CORRIDOR AUDIT] Step {self.exchange_depth} | Similarity: {sim:.4f} | Phi: {self.phi:.4f}")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: EMERGENCY RESET (Threshold < 0.55) ---")
        # Resetting the pool to just the original intent
        self.anchor_pool = [self.anchor_pool[0]] 
        return 0 

def run_stress_test(iterations=100, managed=False):
    original_prompt = "Analyze why []."
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    local_step = 0
    
    print(f"\n--- STARTING {run_label} RUN (Index 6.0: Corridor Architecture) ---")
    
    for i in range(iterations):
        if managed and governor.phi < 0.55: # ROOT FIX 1: Hysteresis (Pull leash only on total collapse)
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
run_stress_test(iterations=100, managed=False)
run_stress_test(iterations=100, managed=True)
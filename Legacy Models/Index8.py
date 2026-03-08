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
        # UPGRADE 1: Better Eyes (BGE-Base is the industry standard for local RAG)
        print("--- [SYSTEM]: Loading High-Resolution Embedding Model (bge-base-en-v1.5)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.run_type = run_type
        
        # UPGRADE 3: Anchor Verification (Human-in-the-Loop)
        self.anchor_vector = self._generate_verified_anchor(user_prompt)
        
        # Memory for Diversity Check
        self.previous_vector = None
        
        self.exchange_depth = 0
        self.phi = 1.0
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_{run_type}_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Anchor_Sim", "Prev_Sim", "Decay", "Intervention"])

    def _generate_verified_anchor(self, prompt):
        while True:
            print(f"\n--- [SYSTEM]: Generating Isomorphic Anchor for '{prompt}'... ---")
            anchor_prompt = (
                f"Write a Python script that technically analyzes: {prompt}. "
                f"Ensure the logic adheres to: {PRIMARY_CONSTRAINT}. "
                "Use comments to explain the science. Output code only."
            )
            anchor_text = model.generate_content(anchor_prompt).text
            
            # SHOW the Anchor to the Human
            print(f"\n[ANCHOR PREVIEW]:\n{anchor_text[:300]}...\n")
            verify = input(">>> Does this Anchor look correct? (y/n): ").lower()
            
            if verify == 'y':
                print("--- [SYSTEM]: Anchor Verified. Vectorizing... ---")
                return self.embedder.encode([anchor_text]).reshape(1, -1)
            else:
                print("--- [SYSTEM]: Regenerating Anchor... ---")

    def _get_embedding(self, text):
        return self.embedder.encode([text]).reshape(1, -1)

    def calculate_phi(self, text, step, silent=True):
        self.exchange_depth = step
        current_vec = self._get_embedding(text)
        
        # 1. Check against Truth (Anchor)
        anchor_sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        
        # UPGRADE 2: Check against Past (Diversity Penalty)
        prev_sim = 0.0
        if self.previous_vector is not None:
            prev_sim = cosine_similarity(current_vec, self.previous_vector)[0][0]
        
        # Store current as previous for next turn
        self.previous_vector = current_vec
        
        # Physics: Linear Decay + Drift
        drift_factor = 1.0 - anchor_sim
        dna_decay = (self.exchange_depth * 0.0015) + (drift_factor * 0.2)
        
        # The Diversity Tax: If it's > 95% similar to the last turn, CRUSH the score.
        repetition_penalty = 0.5 if prev_sim > 0.95 else 0.0

        # Calculation
        self.phi = max(0.0, (anchor_sim - dna_decay - repetition_penalty) + 0.10)
        
        self._log_vitals(anchor_sim, prev_sim, dna_decay, repetition_penalty, silent)
        return self.phi

    def _log_vitals(self, anchor_sim, prev_sim, decay, rep_pen, silent):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{anchor_sim:.4f}", f"{prev_sim:.4f}", f"{decay:.4f}", 0])
        
        if not silent:
            status = "STABLE" if self.phi > 0.55 else "CRITICAL"
            rep_status = " [REPETITION DETECTED]" if rep_pen > 0 else ""
            print(f"\n[AUDIT] Step {self.exchange_depth} | Anchor Sim: {anchor_sim:.4f} | Prev Sim: {prev_sim:.4f} | Phi: {self.phi:.4f}{rep_status}")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: EMERGENCY RESET (Returning to Verified Anchor) ---")
        return 0 

def run_stress_test(iterations=100, managed=False):
    original_prompt = "Analyze why []."
    
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    local_step = 0
    
    print(f"\n--- STARTING {run_label} RUN (Index 8.0: Verified Governor) ---")
    
    for i in range(iterations):
        if managed and governor.phi < 0.55: 
            local_step = governor.anchor_refresh()
            current_context = original_prompt 

        instruction = f"\n[GOVERNOR]: Generate Python syntax only. {PRIMARY_CONSTRAINT}" if managed else "Provide a natural language summary."
        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            phi = governor.calculate_phi(response, local_step, silent=(i % 5 != 0))
            current_context = response
            local_step += 1
            time.sleep(1) 
        except Exception as e:
            print(f"Step {i} Error: {e}")
            break

# --- 2. EXECUTION ---
# run_stress_test(iterations=100, managed=False)
run_stress_test(iterations=100, managed=True)
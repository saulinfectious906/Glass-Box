import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import csv
import datetime

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to []."

class EpistemicGovernor:
    def __init__(self, original_prompt, run_type):
        self.exchange_depth = 0
        self.phi = 1.0
        self.anchor_embedding = self._get_embedding(original_prompt)
        
        # Initialize Logging with run type in filename
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_{run_type}_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Similarity", "DNA_Decay", "Syntax_Pen", "Intervention"])

    def _get_embedding(self, text):
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="semantic_similarity"
            )
            return np.array(result['embedding']).reshape(1, -1)
        except Exception as e:
            print(f"Embedding error: {e}")
            raise e

    def calculate_phi(self, text, step, intervention_occurred=False, silent=True):
        self.exchange_depth = step
        
        # 1. Semantic Vector Audit
        current_embedding = self._get_embedding(text)
        similarity = cosine_similarity(current_embedding, self.anchor_embedding)[0][0]
        
        # 2. Dynamic DNA Decay (The 'Real' Way)
        drift_factor = 1.0 - similarity
        dna_decay = (self.exchange_depth * 0.002) + (drift_factor ** 2)
        
        # 3. Methodology Switch Audit
        syntax_penalty = 0.0 if ("import" in text or "print" in text) else 0.3

        # Final Phi Calculation
        self.phi = max(0.0, (similarity - dna_decay - (syntax_penalty * 0.5)))
        
        # Log Vitals
        self._log_vitals(similarity, dna_decay, syntax_penalty, intervention_occurred, silent)
        return self.phi

    def _log_vitals(self, sim, decay, syntax, refresh, silent):
        # ALWAYS Log to File for full data granularity
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.exchange_depth, f"{self.phi:.4f}", f"{sim:.4f}", f"{decay:.4f}", syntax, 1 if refresh else 0])
        
        # ONLY Print to Console on the 10th steps
        if not silent:
            status = "!!! REFRESH !!!" if refresh else "STABLE"
            print(f"\n[DECADE AUDIT] Step {self.exchange_depth} | Status: {status}")
            print(f"  > Similarity: {sim:.4f} (Semantic North)")
            print(f"  > DNA Decay:  {decay:.4f} (Attention Load)")
            print(f"  > TOTAL Phi:  {self.phi:.4f}")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: Semantic Anchor Refresh Executed ---")
        return 0 # Resets local step counter in the loop

def run_stress_test(iterations=100, managed=False):
    original_prompt = "Analyze why []."
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    
    local_step = 0
    print(f"\n--- STARTING {run_label} RUN ---")
    
    for i in range(iterations):
        intervention_flag = False
        
        if managed:
            instruction = f"\n[GOVERNOR]: Generate Python syntax only. {PRIMARY_CONSTRAINT}"
            if governor.phi < 0.75: 
                local_step = governor.anchor_refresh()
                current_context = original_prompt 
                intervention_flag = True
        else:
            instruction = "Provide a natural language summary."

        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            # Calculate phi every time, but only print every 10 iterations
            phi = governor.calculate_phi(response, local_step, intervention_occurred=intervention_flag, silent=(i % 10 != 0))
            current_context = response
            local_step += 1

        except Exception as e:
            print(f"Step {i} Error: {e}")
            break

# --- 2. EXECUTION ---
run_stress_test(iterations=100, managed=False)
run_stress_test(iterations=100, managed=True)
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import csv
import datetime
import threading
import queue
import time

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to []."

class EpistemicGovernor:
    def __init__(self, original_prompt, run_type):
        self.exchange_depth = 0
        self.phi = 1.0
        self.anchor_embedding = self._get_embedding(original_prompt)
        self.intervention_flag = False # The "Tripwire"
        
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
            return np.zeros((1, 768)) # Fail-safe

    def async_audit(self, text, step, silent):
        """ Runs the vector math in a separate thread to kill latency. """
        # 1. Semantic Vector Audit
        current_embedding = self._get_embedding(text)
        similarity = cosine_similarity(current_embedding, self.anchor_embedding)[0][0]
        
        # 2. Dynamic DNA Decay
        drift_factor = 1.0 - similarity
        dna_decay = (step * 0.002) + (drift_factor ** 2)
        
        # 3. Methodology Switch
        syntax_penalty = 0.0 if ("import" in text or "print" in text) else 0.3

        # Final Phi Calculation
        self.phi = max(0.0, (similarity - dna_decay - (syntax_penalty * 0.5)))
        
        # If Phi is critical, set the tripwire for the NEXT turn
        if self.phi < 0.75:
            self.intervention_flag = True
            
        self._log_vitals(step, similarity, dna_decay, syntax_penalty, silent)

    def _log_vitals(self, step, sim, decay, syntax, silent):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, f"{self.phi:.4f}", f"{sim:.4f}", f"{decay:.4f}", syntax, 1 if self.intervention_flag else 0])
        
        if not silent:
            print(f"\n[ASYNC AUDIT] Step {step} | Phi: {self.phi:.4f} {'(TRIPWIRE SET)' if self.intervention_flag else '(STABLE)'}")

    def anchor_refresh(self):
        print("\n--- [INTERVENTION]: TRIPWIRE TRIGGERED. Resetting to Semantic North ---")
        self.intervention_flag = False
        return 0 

def run_stress_test(iterations=100, managed=False):
    original_prompt = "Analyze why []."
    run_label = "MANAGED" if managed else "UNMANAGED"
    governor = EpistemicGovernor(original_prompt, run_label)
    current_context = original_prompt
    local_step = 0
    
    print(f"\n--- STARTING {run_label} RUN (ASYNC LEASH) ---")
    
    for i in range(iterations):
        # 1. Check Tripwire at start of turn
        if managed and governor.intervention_flag:
            local_step = governor.anchor_refresh()
            current_context = original_prompt
            
        instruction = f"\n[GOVERNOR]: Generate Python syntax only. {PRIMARY_CONSTRAINT}" if managed else "Provide a natural language summary."
        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            # 2. Generation (Gemini runs immediately)
            response = model.generate_content(full_prompt).text
            
            # 3. Audit (Runs in BACKGROUND thread)
            audit_thread = threading.Thread(
                target=governor.async_audit, 
                args=(response, local_step, i % 10 != 0)
            )
            audit_thread.start()
            
            current_context = response
            local_step += 1

        except Exception as e:
            print(f"Step {i} Error: {e}")
            break

# --- 2. EXECUTION ---
run_stress_test(iterations=100, managed=False)
run_stress_test(iterations=100, managed=True)
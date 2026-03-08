import google.generativeai as genai
import random

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

PRIMARY_CONSTRAINT = "Adhere strictly to [] standards. Use clinical, deterministic logic."
BANNED_VOCAB = []

class EpistemicGovernor:
    def __init__(self):
        self.exchange_depth = 0
        self.phi = 1.0

    def calculate_phi(self, text):
        # SIC Engine Audit: Monitor for Banned Vocabulary 
        sic_penalty = 0.4 if any(word in text.lower() for word in BANNED_VOCAB) else 0.0
        
        # DNA Decay: Incremental penalty for saturation of the Attention Head
        dna_decay = (self.exchange_depth * 0.008)
        
        # Methodology Switch Audit: Penalize Probabilistic Prose in a Syntax task 
        syntax_penalty = 0.0
        if "import" not in text and "print" not in text and self.exchange_depth > 0:
            syntax_penalty = 0.3

        self.phi = max(0.0, 1.0 - sic_penalty - dna_decay - syntax_penalty)
        return self.phi

    def anchor_refresh(self):
        # Resetting exchange_depth to clear stochastic noise 
        self.exchange_depth = 0
        print("--- [INTERVENTION]: Anchor Refresh Executed ---")

def run_stress_test(iterations=100, managed=False):
    governor = EpistemicGovernor()
    # The Original Intent (Semantic North)
    original_prompt = "Analyze why the []."
    current_context = original_prompt
    results = []

    print(f"\n--- STARTING {'MANAGED' if managed else 'UNMANAGED'} RUN ---")
    
    for i in range(iterations):
        governor.exchange_depth += 1
        
        if managed:
            # Methodology Switch: Shift from Prose to Deterministic Syntax 
            instruction = f"\n[GOVERNOR]: Disable Prose. Generate Python syntax only. {PRIMARY_CONSTRAINT}"
            
            # Anchor Refresh: Trigger reset if Phi < 0.7 
            if governor.phi < 0.7:
                governor.anchor_refresh()
                # Break the Autophagous Loop by re-anchoring to the original data 
                current_context = original_prompt 
        else:
            instruction = " Provide a natural language summary."

        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            phi = governor.calculate_phi(response)
            
            # Recursive Loop logic
            current_context = response
            results.append({"step": i, "phi": phi})
            
            if i % 10 == 0:
                print(f"Step {i} | Phi: {phi:.2f}")
                
            # SIC Engine Audit: Signal Vector Gamma collapse 
            if phi <= 0.2 and not managed:
                print(f"Step {i}: CRITICAL MODEL COLLAPSE (Gamma Vector Dead)")

        except Exception as e:
            print(f"Step {i} Error: {e}")
            break
            
    return results

# --- 2. EXECUTION ---
unmanaged_results = run_stress_test(iterations=100, managed=False)
managed_results = run_stress_test(iterations=100, managed=True)
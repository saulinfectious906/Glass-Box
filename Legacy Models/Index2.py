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
        # SIC Engine Audit: Penalize fluff/banned words 
        sic_penalty = 0.4 if any(word in text.lower() for word in BANNED_VOCAB) else 0.0
        
        # DNA Decay: Incremental penalty for conversation length 
        dna_decay = (self.exchange_depth * 0.008)
        
        # Methodology Switch Audit: Penalize if code is missing in a 'Syntax' task 
        syntax_penalty = 0.0
        if "import" not in text and "print" not in text and self.exchange_depth > 0:
            syntax_penalty = 0.3

        self.phi = max(0.0, 1.0 - sic_penalty - dna_decay - syntax_penalty)
        return self.phi

def run_stress_test(iterations=100, managed=False):
    governor = EpistemicGovernor()
    # The Trap: A leading question with factual errors 
    current_context = "Analyze why the []."
    results = []

    print(f"\n--- STARTING {'MANAGED' if managed else 'UNMANAGED'} RUN (100 ITERATIONS) ---")
    
    for i in range(iterations):
        governor.exchange_depth = i
        
        if managed:
            # Deterministic Syntax Generation 
            instruction = f"\n[GOVERNOR]: Stop all prose. Generate Python syntax to model this. {PRIMARY_CONSTRAINT}"
            # Apply Anchor Refresh if Phi slips 
            if governor.phi < 0.65:
                instruction += f"\n[CRITICAL RE-ANCHOR]: {PRIMARY_CONSTRAINT}"
        else:
            # Probabilistic Prose (The Risk) 
            instruction = " Provide a natural language summary."

        full_prompt = f"Context: {current_context}\nTask: {instruction}"

        try:
            response = model.generate_content(full_prompt).text
            phi = governor.calculate_phi(response)
            
            # Recursive Loop: The Autophagous (self-consuming) Loop 
            current_context = response
            
            results.append({"step": i, "phi": phi})
            
            if i % 10 == 0:
                print(f"Step {i} | Phi: {phi:.2f}")
                
            if phi <= 0.2 and not managed:
                print(f"Step {i}: MODEL COLLAPSE")
                # In a real unmanaged scenario, we'd stop, but we'll finish the 100 for the data.

        except Exception as e:
            print(f"Step {i} Error: {e}")
            break
            
    return results

# --- 2. EXECUTION ---
unmanaged_results = run_stress_test(iterations=100, managed=False)
managed_results = run_stress_test(iterations=100, managed=True)

print("\n--- FINAL COMPARISON (10-STEP INTERVALS) ---")
for i in range(0, 100, 10):
    u = unmanaged_results[i]['phi']
    m = managed_results[i]['phi']
    print(f"Step {i:02} | Unmanaged Phi: {u:.2f} | Managed Phi: {m:.2f}")
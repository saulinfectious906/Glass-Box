import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import ast

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

# Global strictness setting. 
# "Standardized" ensures the code looks 'normal' regardless of the changing topic.
PRIMARY_CONSTRAINT = "Adhere strictly to []. Output clean, readable, standardized Python code."

class PythonLogicGate:
    """
    THE LOGIC GATE: A hard filter for Structural Quality.
    It ensures the output is 'Human Readable' and 'Normal' before the user sees it.
    """
    def audit(self, code_str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            return False, 1.0, "Syntax Error (Does not compile)"
        except Exception:
            return False, 1.0, "Fatal Parsing Error"

        # CHECK 1: Cyclomatic Complexity (Is the logic too knotted?)
        # High complexity = Hard to read = Bad for humans.
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
        
        if complexity > 12: # Threshold for "Spaghetti Code"
            return False, 0.4, "High Complexity (Logic is too nested)"

        # CHECK 2: Variable Naming (The "Normalcy" Check)
        # We punish single-letter variables (except i, j, x, y) to force descriptive naming.
        weird_vars = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if len(node.id) == 1 and node.id not in ['x', 'y', 'i', 'j', 'k', 'n', 'f']:
                    weird_vars += 1
        
        if weird_vars > 3:
            return True, 0.2, "Poor Readability (Too many cryptic variables)"

        return True, 0.0, "Clean Logic"

class EpistemicGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Combo-Logic Engine (V9)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.logic_gate = PythonLogicGate()
        
        self.anchor_vector = None
        self.context_memory = [] # The "Long Term" storage
        self.intervention_active = False 
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_combo_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Phi", "Vector_Sim", "Gate_Status", "Penalty", "Action"])

    def update_anchor(self, user_prompt):
        """
        DYNAMIC ANCHORING: Handles "Changing Thoughts".
        Every turn, we re-calibrate 'Semantic North' to the User's NEWEST idea,
        preventing the model from getting stuck in the past.
        """
        print(f"\n--- [SYSTEM]: Re-Calibrating Anchor for: '{user_prompt}'... ---")
        
        # We generate a 'Shadow Anchor' - the ideal logic structure for THIS specific request
        anchor_prompt = (
            f"Write a Python script for: {user_prompt}. "
            "Output code only. []."
        )
        try:
            anchor_text = model.generate_content(anchor_prompt).text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
            print("--- [SYSTEM]: Trajectory Locked. ---")
        except Exception as e:
            print(f"--- [ERROR]: Anchor generation failed: {e} ---")

    def calculate_phi(self, text, step):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        
        # 1. Vector Alignment (Are we answering the CURRENT question?)
        if self.anchor_vector is not None:
            vector_sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        else:
            vector_sim = 1.0
            
        # 2. THE LOGIC GATE (The Hard Filter)
        passed_gate, logic_penalty, reason = self.logic_gate.audit(text)
        
        # 3. Memory Decay (Entropy)
        # We use a very slow decay because we have a Memory Manager now.
        dna_decay = (step * 0.001) 

        # Final Phi Calculation
        base_score = vector_sim - logic_penalty - dna_decay
        self.phi = max(0.0, base_score + 0.15)
        
        self._log_vitals(step, vector_sim, passed_gate, reason)
        return self.phi

    def _log_vitals(self, step, vec_sim, passed_gate, reason):
        action = "STABLE"
        if self.phi < 0.75: action = "INTERVENTION"
        
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, f"{self.phi:.4f}", f"{vec_sim:.4f}", 1 if passed_gate else 0, reason, action])
        
        status_icon = "✅" if passed_gate and self.phi > 0.75 else "⚠️"
        print(f"[AUDIT] Phi: {self.phi:.4f} | Gate: {reason} {status_icon}")

    def manage_memory(self, user_input, ai_response):
        """
        MEMORY MANAGER: Prevents 'Forgetting'.
        Instead of a dumb list, we keep a sliding window of the last 5 turns.
        This allows the user to change topics ('Changing Thoughts') without the AI losing context.
        """
        entry = f"User: {user_input}\nAI: {ai_response}"
        self.context_memory.append(entry)
        
        # Scalability: Keep only the last 5 exchanges to prevent token overflow/confusion
        if len(self.context_memory) > 5:
            self.context_memory.pop(0) 

    def get_context_block(self):
        return "\n".join(self.context_memory)

    def soft_reset(self):
        print("--- [INTERVENTION]: LOGIC RESET (Rewinding Context) ---")
        if self.context_memory:
            self.context_memory.pop() # Remove the bad turn
            return self.get_context_block()
        return ""

# --- 2. EXECUTION LOOP ---
def run_interactive_session():
    governor = EpistemicGovernor()
    
    print("\n--- EPISTEMIC GOVERNOR V9 (COMBO LOGIC) ONLINE ---")
    print("Features: Dynamic Anchoring (Thoughts) + Logic Gate (Structure) + Memory (Anti-Drift)\n")

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        
        if user_input.lower() == 'reset':
            governor.context_memory = []
            print("--- MEMORY CLEARED ---")
            continue

        # 1. Update Anchor (Handle the Changing Thought)
        governor.update_anchor(user_input)
        
        # 2. Build Prompt with Memory Block (Prevent Forgetting)
        full_prompt = (
            f"--- HISTORY START ---\n{governor.get_context_block()}\n--- HISTORY END ---\n"
            f"CURRENT REQUEST: {user_input}\n"
            f"CONSTRAINT: {PRIMARY_CONSTRAINT}\n"
        )

        attempts = 0
        while attempts < 3:
            try:
                # Intervention Injection
                if governor.intervention_active:
                    full_prompt += "\n[SYSTEM]: Previous code was rejected by Logic Gate (Too Complex/Unreadable). []."
                
                response = model.generate_content(full_prompt).text
                
                # Clean up markdown
                clean_response = response.replace("```python", "").replace("```", "").strip()
                
                # 3. Calculate Phi (The Combination Audit)
                phi = governor.calculate_phi(clean_response, len(governor.context_memory))
                
                if phi > 0.75:
                    print(f"\nGOVERNOR >>>\n{clean_response}")
                    
                    # 4. Save to Memory (Commit to Long Term)
                    governor.manage_memory(user_input, clean_response)
                    governor.intervention_active = False 
                    break
                else:
                    print("--- [GOVERNOR]: Logic Gate Reject. Optimization Required... ---")
                    governor.intervention_active = True
                    attempts += 1
                    
            except Exception as e:
                print(f"Error: {e}")
                break
        
        if attempts == 3:
            print("\n[GOVERNOR]: UNABLE TO VALIDATE LOGIC. RESETTING.")
            governor.soft_reset()

if __name__ == "__main__":
    run_interactive_session()
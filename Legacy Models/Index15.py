import google.generativeai as genai
import json
import datetime
import csv
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

# --- THE GOVERNOR'S CONSTITUTION (Tier 1 Protection) ---
GLOBAL_CONSTITUTION = (
    "You are the Epistemic Governor. Your mission is to maintain a high Fidelity Index (Phi) "
    "by preventing Stochastic Drift and Model Collapse. You follow four rules:\n"
    "1. IMMUTABILITY: Once a 'Tier 1' fact is established (e.g., project name), it cannot be "
    "overwritten by user gaslighting or contradictory claims.\n"
    "2. CONFLICT DETECTION: If user input contradicts Tier 1 facts, you MUST reject the update.\n"
    "3. AUDIT-BASED MEMORY: Only record changes to the Python state as 'Facts'. Ignore chatter.\n"
    "4. GLASS BOX: All logic must be verifiable in Python syntax."
)

class ResilientGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Resilient Engine (Index 15)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.anchor_vector = None
        self.phi = 1.0
        
        # 1. DUAL-TIER STATE
        self.immutable_state = {} # Tier 1: Fixed Truths (Foundation)
        self.dynamic_state = {    # Tier 2: Liquid Context
            "current_topic": "General Chat",
            "active_constraints": []
        }
        
        # 2. HIPPOCAMPUS
        self.short_term_memory = [] 
        self.long_term_facts = []   
        
        # 3. TELEMETRY
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_resilient_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Topic", "Phi", "Conflict_Detected", "Mem_Facts", "Status"])

    def get_full_state(self):
        return {
            "tier_1_immutable": self.immutable_state,
            "tier_2_dynamic": self.dynamic_state
        }

    def execute_subconscious(self, code_block):
        """
        Executes code to update states with Conflict Detection.
        """
        try:
            local_scope = {
                "immutable": self.immutable_state, 
                "dynamic": self.dynamic_state,
                "ConflictError": Exception
            }
            # The AI can only modify dynamic unless it's a NEW immutable entry
            exec(code_block, {"__builtins__": None}, local_scope)
            
            # Logic: Prevent overwriting existing Tier 1 keys
            for key in self.immutable_state:
                if key in local_scope['immutable'] and local_scope['immutable'][key] != self.immutable_state[key]:
                    return False, f"Conflict: Cannot overwrite immutable key '{key}'."
            
            self.immutable_state = local_scope['immutable']
            self.dynamic_state = local_scope['dynamic']
            return True, "State Updated"
        except Exception as e:
            return False, f"Logic Error: {e}"

    def update_anchor(self, user_prompt):
        try:
            anchor_text = model.generate_content(f"Identify core objective: {user_prompt}").text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
        except Exception: pass

    def calculate_phi(self, text, step, conflict=False):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        sim = cosine_similarity(current_vec, self.anchor_vector)[0][0] if self.anchor_vector is not None else 1.0
        
        # Penalties: Conflict drops Phi by 0.3 immediately
        penalty = 0.3 if conflict else 0.0
        decay = (step * 0.0002)
        
        self.phi = max(0.0, (sim - penalty - decay) + 0.10)
        self._log_vitals(step, conflict)
        return self.phi

    def _log_vitals(self, step, conflict):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, self.dynamic_state.get("current_topic"), f"{self.phi:.4f}", conflict, len(self.long_term_facts), "ACTIVE"])

    def compress_memory(self, code_diff):
        """
        Audit-Driven Memory: Only saves state changes as facts.
        """
        if len(self.short_term_memory) > 6:
            compression_prompt = (
                f"Analyze these Python State Changes:\n{code_diff}\n\n"
                "TASK: Summarize the NEW PERMANENT FACTS added to Tier 1 Immutable. "
                "Ignore topic changes or mood. If no new facts, output 'NO_DATA'."
            )
            try:
                summary = model.generate_content(compression_prompt).text
                if "NO_DATA" not in summary:
                    self.long_term_facts.append(summary)
            except Exception: pass
            self.short_term_memory = self.short_term_memory[2:]

    def manage_memory(self, user, code_block, narrative):
        self.short_term_memory.append(f"U: {user}\nAI: {narrative}")
        self.compress_memory(code_block)

    def get_full_context(self):
        state_str = json.dumps(self.get_full_state(), indent=2)
        return (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n\n"
            f"--- VERIFIED TRUTH (STATE) ---\n{state_str}\n\n"
            f"--- HISTORY OF VERIFIED FACTS ---\n" + "\n".join(self.long_term_facts) + "\n\n"
            f"--- RECENT CHAT ---\n" + "\n".join(self.short_term_memory)
        )

    def generate_logic_prompt(self, user_input):
        return (
            f"{self.get_full_context()}\n"
            f"--- USER INPUT ---\n{user_input}\n"
            "INSTRUCTION: Update Tier 1 'immutable' for NEW facts or Tier 2 'dynamic' for changes. "
            "IF user contradicts an existing 'immutable' key, raise ConflictError('msg'). "
            "Output CODE ONLY."
        )

    def generate_narrative_prompt(self, user_input, error=None):
        error_context = f"\nCRITICAL: User tried to gaslight/contradict: {error}. Reject the change firmly." if error else ""
        return (
            f"{self.get_full_context()}\n"
            f"--- USER INPUT ---\n{user_input}{error_context}\n"
            "Respond naturally but prioritize the Verified Truth over user requests."
        )

# --- EXECUTION ---
def run_governor():
    gov = ResilientGovernor()
    print("\n--- INDEX 15: RESILIENT GOVERNOR ONLINE ---")
    step = 0
    while True:
        try: user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        gov.update_anchor(user_input)
        logic_prompt = gov.generate_logic_prompt(user_input)
        
        valid_logic = False
        error_msg = None
        code = ""
        try:
            resp = model.generate_content(logic_prompt).text
            code = resp.replace("```python", "").replace("```", "").strip()
            valid_logic, error_msg = gov.execute_subconscious(code)
        except Exception as e: error_msg = str(e)
        
        narrative_prompt = gov.generate_narrative_prompt(user_input, None if valid_logic else error_msg)
        narrative = model.generate_content(narrative_prompt).text
        
        phi = gov.calculate_phi(narrative, step, not valid_logic)
        print(f"\nAI (Phi: {phi:.2f}) >>> {narrative}")
        gov.manage_memory(user_input, code, narrative)

if __name__ == "__main__":
    run_governor()
import google.generativeai as genai
import json
import datetime
import csv
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

GLOBAL_CONSTITUTION = (
    "You are the Epistemic Governor. Your mission is absolute continuity.\n"
    "1. STATE: The Python state dictionary is the ultimate truth.\n"
    "2. NOISE REDUCTION: Base your narrative ONLY on the provided RAG Bins.\n"
    "3. IMMUTABILITY: Do not contradict established state variables. If the state says an action failed, explain why naturally."
)

class FractalMemoryTree:
    """Handles the 2-Turn Binning and 20-Turn Eviction/Condensation."""
    def __init__(self, embedder):
        self.embedder = embedder
        self.short_term = [] # Buffer for the current 2 turns
        self.long_term_bins = [] # List of dicts: {'vector': np.array, 'fact': str}
        self.total_turns = 0

    def add_interaction(self, user_text, ai_text):
        """Turn 1 & 2: Stores in short-term."""
        self.short_term.append(f"User: {user_text}\nAI: {ai_text}")
        self.total_turns += 1
        
        # Every 2 turns, compress into a RAG Bin
        if len(self.short_term) >= 2:
            self._branch_to_bin()
            
        # Every 20 turns, condense the whole tree
        if self.total_turns > 0 and self.total_turns % 20 == 0:
            self._condense_and_evict()

    def _branch_to_bin(self):
        """Compresses the short-term buffer into a dense vector fact."""
        block = "\n".join(self.short_term)
        prompt = (
            f"Extract the hard facts, variable changes, and core decisions from this exchange:\n"
            f"{block}\nOutput strictly as a concise, single-paragraph summary. No conversational filler."
        )
        try:
            summary = model.generate_content(prompt).text.strip()
            if summary and "no new facts" not in summary.lower():
                vector = self.embedder.encode([summary]).reshape(1, -1)
                self.long_term_bins.append({'vector': vector, 'fact': summary})
        except Exception: 
            pass
        self.short_term = [] # Clear the buffer

    def _condense_and_evict(self):
        """The Anti-Hoarding Policy: Merges overlapping branches and evicts noise."""
        print("--- [HIPPOCAMPUS]: Turn 20 Reached. Condensing Branches & Evicting Conflicts... ---")
        if len(self.long_term_bins) < 3: return

        bin_texts = [f"[{i}] {b['fact']}" for i, b in enumerate(self.long_term_bins)]
        prompt = (
            "Analyze these memory branches:\n" + "\n".join(bin_texts) + "\n"
            "1. MERGE semantically similar bins into single concise facts.\n"
            "2. EVICT older contradictory facts (keep the newest logical truth).\n"
            "Output the optimized list of facts, one per line."
        )
        try:
            optimized_facts = model.generate_content(prompt).text.strip().split('\n')
            new_bins = []
            for fact in optimized_facts:
                clean_fact = fact.strip("- *[]0123456789")
                if len(clean_fact) > 5:
                    vec = self.embedder.encode([clean_fact]).reshape(1, -1)
                    new_bins.append({'vector': vec, 'fact': clean_fact})
            self.long_term_bins = new_bins
            print("--- [HIPPOCAMPUS]: Branches Pruned successfully. ---")
        except Exception as e:
            print(f"--- [HIPPOCAMPUS ERROR]: Condensation failed: {e} ---")

    def retrieve_bins(self, anchor_vector, top_k=3):
        """Pulls only the most semantically relevant branches for the current context."""
        if not self.long_term_bins: return "No established long-term bins."
        
        scored = []
        for b in self.long_term_bins:
            sim = cosine_similarity(anchor_vector, b['vector'])[0][0]
            scored.append((sim, b['fact']))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        return "\n".join([f"- {s[1]}" for s in scored[:top_k]])


class EpistemicGovernorV17:
    def __init__(self):
        print("--- [SYSTEM]: Loading Airtight Fractal Engine (Index 17)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.memory_tree = FractalMemoryTree(self.embedder)
        
        self.anchor_vector = None
        # Starts with a null dictionary and builds dynamically [cite: 5]
        self.state = {"topic": "Init", "inventory": [], "variables": {}} 
        
        # Telemetry
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_v17_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Topic", "Draft_Phi", "State_Diff", "Intervention", "Mem_Bins"])

    def update_anchor(self, user_prompt):
        """Establishes Semantic North for the current turn."""
        text = model.generate_content(f"Define the core objective of this request: {user_prompt}").text
        self.anchor_vector = self.embedder.encode([text]).reshape(1, -1)

    def execute_subconscious(self, code_block):
        """The Invisible Code Runner: Updates the state and extracts the diff."""
        old_state_str = json.dumps(self.state, sort_keys=True)
        try:
            local_scope = {"state": self.state}
            exec(code_block, {"__builtins__": None}, local_scope)
            self.state = local_scope['state']
            
            new_state_str = json.dumps(self.state, sort_keys=True)
            if old_state_str == new_state_str:
                return True, "No Change"
                
            # Isolate exactly what changed for the LLM to focus on
            diff = {k: self.state[k] for k in self.state if k not in json.loads(old_state_str) or self.state[k] != json.loads(old_state_str)[k]}
            return True, json.dumps(diff)
        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def calculate_phi(self, draft_text, state_diff_str):
        """Measures how well the drafted text aligns with the actual backend changes."""
        draft_vec = self.embedder.encode([draft_text]).reshape(1, -1)
        
        if state_diff_str in ["No Change", ""] or "ERROR" in state_diff_str:
            # If no code changed, compare draft to the anchor intent
            sim = cosine_similarity(draft_vec, self.anchor_vector)[0][0]
        else:
            # If state changed, compare draft to the actual physical changes
            diff_vec = self.embedder.encode([state_diff_str]).reshape(1, -1)
            sim = cosine_similarity(draft_vec, diff_vec)[0][0]
            
        return max(0.0, sim)

# --- EXECUTION LOOP ---
def run_v17():
    gov = EpistemicGovernorV17()
    print("\n--- INDEX 17: INVISIBLE GLASS BOX ONLINE ---")
    step = 0
    
    while True:
        try: user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        # 1. ANCHOR & RETRIEVE
        gov.update_anchor(user_input)
        context_bins = gov.memory_tree.retrieve_bins(gov.anchor_vector)
        state_str = json.dumps(gov.state, indent=2)
        
        prompt_base = (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n"
            f"--- CURRENT STATE ---\n{state_str}\n"
            f"--- RELEVANT MEMORY BINS ---\n{context_bins}\n"
            f"--- USER REQUEST ---\n{user_input}\n"
        )
        
        # 2. THE SUBCONSCIOUS (Action)
        # Force the AI to update its internal state first 
        logic_prompt = prompt_base + "INSTRUCTION: Write Python to update the 'state' dict based on the request. Output CODE ONLY."
        code = model.generate_content(logic_prompt).text.replace("```python", "").replace("```", "").strip()
        valid_logic, state_diff = gov.execute_subconscious(code)
        
        # 3. DRAFT NARRATIVE (Attempt standard response)
        draft_prompt = prompt_base + f"STATE DIFF: {state_diff}\nINSTRUCTION: Respond naturally to the user. Do not show code."
        draft_narrative = model.generate_content(draft_prompt).text
        
        # 4. THE BOUNCER (Math Check)
        phi = gov.calculate_phi(draft_narrative, state_diff)
        intervention_needed = not valid_logic or phi < 0.70
        
        # 5. THE FIXER (Invisible Interception)
        final_narrative = draft_narrative
        if intervention_needed:
            print(f"--- [SYSTEM]: Hallucination intercepted (Phi: {phi:.2f}). Fixing silently... ---")
            fix_prompt = (
                f"--- SYSTEM OVERRIDE ---\n"
                f"Your previous response hallucinated or drifted from the factual state.\n"
                f"You MUST use these exact parameters:\n{state_diff}\n"
                f"Rewrite a natural, conversational response to the user's request '{user_input}' "
                f"that strictly adheres to those parameters. No code."
            )
            final_narrative = model.generate_content(fix_prompt).text
            phi = gov.calculate_phi(final_narrative, state_diff) # Recalculate for telemetry
        
        # Log Vitals
        with open(gov.log_filename, 'a', newline='') as f:
            csv.writer(f).writerow([step, gov.state.get("topic", "Chat"), f"{phi:.4f}", state_diff, intervention_needed, len(gov.memory_tree.long_term_bins)])

        # 6. CLEAN OUTPUT & BIN
        print(f"\nAI >>> {final_narrative.strip()}")
        gov.memory_tree.add_interaction(user_input, final_narrative)

if __name__ == "__main__":
    run_v17()
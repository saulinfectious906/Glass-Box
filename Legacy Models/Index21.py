import google.generativeai as genai
import json
import datetime
import csv
import numpy as np
import copy  # <--- NEW: Imported copy module for deep cloning
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

GLOBAL_CONSTITUTION = (
    "You are the Front-End Architect of the Epistemic Governor. "
    "1. CHATTER: You handle conversation and intent. You do NOT write code or edit files. "
    "2. HOLOGRAMS: You can see the 'holograms' of files in the state, but not their contents. "
    "3. TRUTH: Never contradict the state dictionary or the Backend Diff. If the Backend Diff shows a change, you MUST acknowledge it."
)

class FractalMemoryTree:
    """Handles 2-Turn Binning and 20-Turn Eviction for semantic conversation history."""
    def __init__(self, embedder):
        self.embedder = embedder
        self.short_term = [] 
        self.long_term_bins = [] 
        self.total_turns = 0

    def add_interaction(self, user_text, ai_text):
        self.short_term.append(f"User: {user_text}\nAI: {ai_text}")
        self.total_turns += 1
        
        if len(self.short_term) >= 2:
            self._branch_to_bin()
            
        if self.total_turns > 0 and self.total_turns % 20 == 0:
            self._condense_and_evict()

    def _branch_to_bin(self):
        block = "\n".join(self.short_term)
        prompt = f"Extract hard facts and core decisions from this exchange:\n{block}\nOutput strictly as a concise summary."
        try:
            summary = model.generate_content(prompt).text.strip()
            if summary and "no new facts" not in summary.lower():
                vector = self.embedder.encode([summary]).reshape(1, -1)
                self.long_term_bins.append({'vector': vector, 'fact': summary})
        except Exception: pass
        self.short_term = [] 

    def _condense_and_evict(self):
        print("--- [HIPPOCAMPUS]: Condensing Branches & Evicting Conflicts... ---")
        if len(self.long_term_bins) < 3: return
        bin_texts = [f"[{i}] {b['fact']}" for i, b in enumerate(self.long_term_bins)]
        prompt = (
            "Analyze these memory branches:\n" + "\n".join(bin_texts) + "\n"
            "MERGE similar bins and EVICT older contradictory facts. Output optimized facts, one per line."
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
        except Exception: pass

    def retrieve_bins(self, anchor_vector, top_k=3):
        if not self.long_term_bins: return "No established bins."
        scored = [(cosine_similarity(anchor_vector, b['vector'])[0][0], b['fact']) for b in self.long_term_bins]
        scored.sort(key=lambda x: x[0], reverse=True)
        return "\n".join([f"- {s[1]}" for s in scored[:top_k]])


class EpistemicGovernorV21:
    def __init__(self):
        print("--- [SYSTEM]: Loading Dual-Brain Holographic Engine (Index 21)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.memory_tree = FractalMemoryTree(self.embedder)
        self.anchor_vector = None
        
        # 1. THE VAULT: Dual-Tier State Architecture
        self.dynamic_state = {
            "tier_1_immutable": {"user_name": "Alex", "budget_rule": "Strictly enforce a $5000 minimum budget for all projects"},
            "tier_2_liquid": {}, 
            "holographic_headers": {}
        }
        
        # 2. The Heavy Back-End Locker
        self.artifact_locker = {} 
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_v21_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Triage_Result", "Phi", "State_Diff", "Artifacts_Count"])

    def update_anchor(self, user_prompt):
        text = model.generate_content(f"Define the core objective: {user_prompt}").text
        self.anchor_vector = self.embedder.encode([text]).reshape(1, -1)

    def micro_triage_gate(self, user_prompt):
        triage_prompt = (
            f"Analyze this user prompt: '{user_prompt}'\n"
            "Is the user explicitly asking to create/edit a code file OR update a dynamic personal fact?\n"
            "Return ONLY a JSON object: {{\"needs_mechanic\": true/false, \"confidence\": 0.0-1.0, \"target_file\": \"filename.ext\" or null}}"
        )
        try:
            resp = model.generate_content(triage_prompt).text.replace('```json','').replace('```','').strip()
            return json.loads(resp)
        except:
            return {"needs_mechanic": False, "confidence": 0.0, "target_file": None}

    def execute_mechanic(self, user_prompt, target_file):
        print(f"   -> [MECHANIC WAKING UP]: Operating on State / {target_file}...")
        old_state_str = json.dumps(self.dynamic_state, sort_keys=True)
        
        def read_artifact(name): return self.artifact_locker.get(name, "")
        def write_artifact(name, content): 
            self.artifact_locker[name] = content
            self.dynamic_state["holographic_headers"][name] = f"Size: {len(content)} chars | Status: Stable"
        
        mechanic_prompt = (
            f"USER REQUEST: {user_prompt}\n"
            "INSTRUCTION: Write a Python script to fulfill this request.\n"
            "1. EDITING FILES: Use `read_artifact(name)` and `write_artifact(name, content)`.\n"
            "   CRITICAL: Do not append duplicate classes. Use string replacement. Example:\n"
            "   `txt = read_artifact('file.py')`\n"
            "   `txt = txt.replace('old_string', 'new_string')`\n"
            "   `write_artifact('file.py', txt)`\n"
            "2. MANAGING FACTS: Modify the `state['tier_2_liquid']` dictionary directly.\n"
            "3. THE VAULT: You may read `state['tier_1_immutable']`, but you CANNOT change it.\n"
            "CRITICAL: Do NOT reassign the 'state' variable to a new object. Output Python code only."
        )
        
        try:
            code = model.generate_content(mechanic_prompt).text.replace("```python", "").replace("```", "").strip()
            
            safe_globals = {"__builtins__": __builtins__, "read_artifact": read_artifact, "write_artifact": write_artifact}
            # --- DEEPCOPY FIX: Fully isolate the nested dictionaries ---
            local_scope = {"state": copy.deepcopy(self.dynamic_state)}
            
            exec(code, safe_globals, local_scope)
            
            new_state_candidate = local_scope.get('state')
            
            # --- SCHEMA ARMOR V2: The Vault & Bloat Checks ---
            if not isinstance(new_state_candidate, dict):
                return False, "Mechanic Error: Schema Corruption (State overwritten)."
                
            if new_state_candidate.get('tier_1_immutable') != json.loads(old_state_str).get('tier_1_immutable'):
                return False, "Mechanic Error: Unauthorized Access. Attempted to overwrite Tier 1 Immutable Vault."
                
            for k, v in new_state_candidate.get('tier_2_liquid', {}).items():
                if isinstance(v, str) and len(v) > 300:
                    return False, f"Mechanic Error: Semantic Bloat. Fact '{k}' exceeds 300-character limit."

            try:
                new_state_str = json.dumps(new_state_candidate, sort_keys=True)
                self.dynamic_state = json.loads(new_state_str) 
            except TypeError as type_err:
                return False, f"Mechanic Error: Corrupted State. {str(type_err)}"
            
            diff = {k: self.dynamic_state[k] for k in self.dynamic_state if k not in json.loads(old_state_str) or self.dynamic_state[k] != json.loads(old_state_str)[k]}
            
            if not diff and old_state_str != new_state_str:
                 return True, "Artifact Updated Silently"
            return True, json.dumps(diff) if diff else "No Change"
            
        except Exception as e:
            return False, f"Mechanic Error: {str(e)}"

    def calculate_phi(self, draft_text, state_diff_str):
        draft_vec = self.embedder.encode([draft_text]).reshape(1, -1)
        
        rejection_phrases = ["i cannot", "i am unable", "i do not have the ability", "i'm unable", "outside the scope"]
        is_rejecting = any(phrase in draft_text.lower() for phrase in rejection_phrases)
        
        if state_diff_str not in ["No Change", "Artifact Updated Silently", ""] and "Error" not in state_diff_str:
            if is_rejecting:
                return 0.0 
            diff_vec = self.embedder.encode([state_diff_str]).reshape(1, -1)
            sim = cosine_similarity(draft_vec, diff_vec)[0][0]
        else:
            sim = cosine_similarity(draft_vec, self.anchor_vector)[0][0]
            
        return max(0.0, sim)


def run_v21():
    gov = EpistemicGovernorV21()
    print("\n--- INDEX 21: DUAL-TIER VAULT ONLINE ---")
    step = 0
    
    while True:
        try: user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        gov.update_anchor(user_input)
        context_bins = gov.memory_tree.retrieve_bins(gov.anchor_vector)
        
        triage = gov.micro_triage_gate(user_input)
        state_diff = "No Change"
        valid_logic = True
        
        if triage['needs_mechanic']:
            if triage['confidence'] >= 0.7:
                valid_logic, state_diff = gov.execute_mechanic(user_input, triage['target_file'])
            else:
                user_input = f"[SYSTEM: Metaphor detected. Clarify intent.] " + user_input
        
        state_str = json.dumps(gov.dynamic_state, indent=2)
        architect_prompt = (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n"
            f"--- DUAL-TIER STATE ---\n{state_str}\n"
            f"--- MEMORY BINS ---\n{context_bins}\n"
            f"--- BACKEND DIFF ---\n{state_diff}\n"
            f"--- USER REQUEST ---\n{user_input}\n"
            "INSTRUCTION: Respond naturally. Acknowledge backend changes if the diff says they happened."
        )
        
        draft_narrative = model.generate_content(architect_prompt).text
        phi = gov.calculate_phi(draft_narrative, state_diff)
        
        final_narrative = draft_narrative
        if not valid_logic or phi < 0.70:
            print(f"--- [SYSTEM]: Hallucination intercepted (Phi: {phi:.2f}). Fixing silently... ---")
            fix_prompt = architect_prompt + "\n[SYSTEM OVERRIDE]: Your previous draft failed logic checks. Adhere strictly to the Backend Diff. Rewrite."
            try: final_narrative = model.generate_content(fix_prompt).text; phi = gov.calculate_phi(final_narrative, state_diff)
            except: pass

        with open(gov.log_filename, 'a', newline='') as f:
            csv.writer(f).writerow([step, triage['needs_mechanic'], f"{phi:.4f}", state_diff, len(gov.artifact_locker)])
            
        print(f"\nAI >>> {final_narrative.strip()}")
        gov.memory_tree.add_interaction(user_input, final_narrative)

if __name__ == "__main__":
    run_v21()
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


class EpistemicGovernorV19:
    def __init__(self):
        print("--- [SYSTEM]: Loading Dual-Brain Holographic Engine (Index 19)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.memory_tree = FractalMemoryTree(self.embedder)
        self.anchor_vector = None
        
        # 1. The Light Front-End State (Strictly for Facts and Holograms)
        self.dynamic_state = {"topic": "Init", "user_facts": {}, "holographic_headers": {}}
        
        # 2. The Heavy Back-End Locker (Never JSON-dumped into the prompt)
        self.artifact_locker = {} 
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_v19_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Triage_Result", "Phi", "State_Diff", "Artifacts_Count"])

    def update_anchor(self, user_prompt):
        text = model.generate_content(f"Define the core objective: {user_prompt}").text
        self.anchor_vector = self.embedder.encode([text]).reshape(1, -1)

    def micro_triage_gate(self, user_prompt):
        """
        The Intent Router: Decides if the Mechanic needs to wake up for EITHER 
        code artifacts OR updating hard user facts/rules.
        """
        triage_prompt = (
            f"Analyze this user prompt: '{user_prompt}'\n"
            "Is the user explicitly asking to create/edit a code file OR update a hard personal fact/rule (like a budget, tech stack, or name)?\n"
            "Return ONLY a JSON object: {\"needs_mechanic\": true/false, \"confidence\": 0.0-1.0, \"target_file\": \"filename.ext\" or null}"
        )
        try:
            resp = model.generate_content(triage_prompt).text.replace('```json','').replace('```','').strip()
            return json.loads(resp)
        except:
            return {"needs_mechanic": False, "confidence": 0.0, "target_file": None}

    def execute_mechanic(self, user_prompt, target_file):
        """The Back-End: Heavy lifting, Sandbox Fixed, Anti-Junk-Drawer Enforced."""
        print(f"   -> [MECHANIC WAKING UP]: Operating on State / {target_file}...")
        old_state_str = json.dumps(self.dynamic_state, sort_keys=True)
        
        # Internal API for the LLM Mechanic
        def read_artifact(name): return self.artifact_locker.get(name, "")
        def write_artifact(name, content): 
            self.artifact_locker[name] = content
            self.dynamic_state["holographic_headers"][name] = f"Size: {len(content)} chars | Status: Stable"
        
        mechanic_prompt = (
            f"USER REQUEST: {user_prompt}\n"
            "INSTRUCTION: Write a Python script to fulfill this request.\n"
            "1. To edit files, use: `read_artifact(name)` and `write_artifact(name, content)`.\n"
            "2. To update rules/facts, modify the `state['user_facts']` dictionary directly.\n"
            "CRITICAL: Do NOT reassign the 'state' variable to a class or object. It MUST remain a dictionary containing only primitives (strings, ints, lists, dicts).\n"
            "CRITICAL: DO NOT log errors, chat history, or conversational rejections in the state dictionary. Keep it clean.\n"
            "Output Python code only."
        )
        
        try:
            code = model.generate_content(mechanic_prompt).text.replace("```python", "").replace("```", "").strip()
            
            safe_globals = {"__builtins__": __builtins__}
            local_scope = {"read_artifact": read_artifact, "write_artifact": write_artifact, "state": self.dynamic_state}
            
            exec(code, safe_globals, local_scope)
            
            # --- THE JSON ARMOR PATCH ---
            # Test if the LLM broke the dictionary by trying to dump it
            try:
                new_state_str = json.dumps(local_scope['state'], sort_keys=True)
                # If it passes, strictly enforce it by loading the sanitized JSON back
                self.dynamic_state = json.loads(new_state_str) 
            except TypeError as type_err:
                # If the LLM injected an object (like MockState), catch it, revert, and report failure
                return False, f"Mechanic Error: Corrupted State (Not JSON Serializable). {str(type_err)}"
            
            diff = {k: self.dynamic_state[k] for k in self.dynamic_state if k not in json.loads(old_state_str) or self.dynamic_state[k] != json.loads(old_state_str)[k]}
            
            # Identify if it was an artifact update or a state update
            if not diff and old_state_str != new_state_str:
                 return True, "Artifact Updated Silently"
            return True, json.dumps(diff) if diff else "No Change"
            
        except Exception as e:
            return False, f"Mechanic Error: {str(e)}"

    def calculate_phi(self, draft_text, state_diff_str):
        """The Math Bouncer: Now catches Gaslighting."""
        draft_vec = self.embedder.encode([draft_text]).reshape(1, -1)
        
        # Anti-Gaslighting Check (Fixing Index 17's flaw)
        rejection_phrases = ["i cannot", "i am unable", "i do not have the ability", "i'm unable", "outside the scope"]
        is_rejecting = any(phrase in draft_text.lower() for phrase in rejection_phrases)
        
        if state_diff_str not in ["No Change", "Artifact Updated Silently", ""] and "Error" not in state_diff_str:
            if is_rejecting:
                return 0.0 # Instant fail: The code changed the truth, but the AI is lying and saying it can't.
                
            diff_vec = self.embedder.encode([state_diff_str]).reshape(1, -1)
            sim = cosine_similarity(draft_vec, diff_vec)[0][0]
        else:
            sim = cosine_similarity(draft_vec, self.anchor_vector)[0][0]
            
        return max(0.0, sim)


# --- EXECUTION LOOP ---
def run_v19():
    gov = EpistemicGovernorV19()
    print("\n--- INDEX 19: DUAL-BRAIN GOVERNOR ONLINE ---")
    step = 0
    
    while True:
        try: user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        # 1. ANCHOR & RETRIEVE
        gov.update_anchor(user_input)
        context_bins = gov.memory_tree.retrieve_bins(gov.anchor_vector)
        
        # 2. MICRO-TRIAGE GATE
        triage = gov.micro_triage_gate(user_input)
        state_diff = "No Change"
        valid_logic = True
        
        # 3. ROUTING LOGIC
        if triage['needs_mechanic']:
            if triage['confidence'] >= 0.7:
                valid_logic, state_diff = gov.execute_mechanic(user_input, triage['target_file'])
            else:
                user_input = f"[SYSTEM: User metaphor detected. Clarify intent before acting.] " + user_input
        
        # 4. THE ARCHITECT (Front-End Narrative)
        state_str = json.dumps(gov.dynamic_state, indent=2)
        architect_prompt = (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n"
            f"--- LIGHT STATE (Holograms & Facts) ---\n{state_str}\n"
            f"--- MEMORY BINS ---\n{context_bins}\n"
            f"--- BACKEND DIFF ---\n{state_diff}\n"
            f"--- USER REQUEST ---\n{user_input}\n"
            "INSTRUCTION: Respond naturally. Acknowledge backend code/fact changes if the diff says they happened."
        )
        
        draft_narrative = model.generate_content(architect_prompt).text
        phi = gov.calculate_phi(draft_narrative, state_diff)
        
        # 5. THE FIXER (Invisible Interception)
        final_narrative = draft_narrative
        if not valid_logic or phi < 0.70:
            print(f"--- [SYSTEM]: Architect hallucinated or gaslit (Phi: {phi:.2f}). Fixing silently... ---")
            fix_prompt = architect_prompt + "\n[SYSTEM OVERRIDE]: Your previous draft failed the logic check or lied about capabilities. Adhere strictly to the Backend Diff and Light State. Rewrite."
            try: final_narrative = model.generate_content(fix_prompt).text; phi = gov.calculate_phi(final_narrative, state_diff)
            except: pass

        # Log & Memory
        with open(gov.log_filename, 'a', newline='') as f:
            csv.writer(f).writerow([step, triage['needs_mechanic'], f"{phi:.4f}", state_diff, len(gov.artifact_locker)])
            
        print(f"\nAI >>> {final_narrative.strip()}")
        gov.memory_tree.add_interaction(user_input, final_narrative)

if __name__ == "__main__":
    run_v19()
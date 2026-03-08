import google.generativeai as genai
import json
import datetime
import csv
import numpy as np
import copy
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY") # Replace with actual API Key, leave the paretheses
model = genai.GenerativeModel('MDOEL_NAME') # Replace with model name, 'gemini-2.5-flash'

GLOBAL_CONSTITUTION = (
    "You are the AI, an advanced assistant. Your style is smart, direct, efficient, witty, and conversational without being overly formal. "
    "1. CHATTER: You are highly capable. You can answer questions, solve math problems, brainstorm, and assist with any query. "
    "2. THE BACKEND: You are paired with a background Mechanic that handles file editing and system state. "
    "3. TRUTH: Never contradict the state dictionary or the Backend Diff. If the Backend Diff shows a change, you MUST smoothly acknowledge it in natural conversation. Do not sound like a robot reading a log. "
    "4. HIERARCHY OF TRUTH: If a fact in 'tier_2_liquid' contradicts 'tier_1_immutable', 'tier_1_immutable' is the absolute truth."
)

class FractalMemoryTree:
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


class GlassBoxIO:
    def __init__(self):
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.memory_tree = FractalMemoryTree(self.embedder)
        self.anchor_vector = None
        self.step = 0
        
        # 1. THE VAULT: Base Identity (Scrubbed for public release)
        # Replace the following with the information
        self.dynamic_state = {
            "tier_1_immutable": {
                "user_name": "[USER_NAME]", 
                "role": "[USER_ROLE]", 
                "system_rule": "[INSERT_CORE_DIRECTIVE_HERE]"
            },
            "tier_2_liquid": {}, 
            "holographic_headers": {}
        }
        
        # 2. REAL I/O WORKSPACE
        self.workspace_dir = "AI_workspace"
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # 3. SILENT CSV LOGGING
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_io_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Triage_Result", "Phi", "State_Diff", "Files_Tracked"])

    def update_anchor(self, user_prompt):
        try:
            text = model.generate_content(f"Define the core objective: {user_prompt}").text
            self.anchor_vector = self.embedder.encode([text]).reshape(1, -1)
        except Exception:
            self.anchor_vector = self.embedder.encode(["Unclear intent"]).reshape(1, -1)

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
        old_state_str = json.dumps(self.dynamic_state, sort_keys=True)
        
        # --- REAL OS HOOKS ---
        def read_artifact(name): 
            filepath = os.path.join(self.workspace_dir, name)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file: return file.read()
            return ""
            
        def write_artifact(name, content): 
            filepath = os.path.join(self.workspace_dir, name)
            with open(filepath, 'w', encoding='utf-8') as file: file.write(content)
            self.dynamic_state["holographic_headers"][name] = f"Size: {len(content)} chars | Status: Stable"
        
        mechanic_prompt = (
            f"USER REQUEST: {user_prompt}\n"
            "INSTRUCTION: Write a Python script to fulfill this request.\n"
            "1. EDITING FILES: Use `read_artifact(name)` and `write_artifact(name, content)`.\n"
            "   CRITICAL: Do not append duplicate classes. Use string replacement.\n"
            "2. MANAGING FACTS: Modify the `state['tier_2_liquid']` dictionary directly.\n"
            "   CRITICAL LIMIT: 'tier_2_liquid' can hold a MAXIMUM of 10 keys. Consolidate older facts to free up space.\n"
            "3. THE VAULT: You may read `state['tier_1_immutable']`, but you CANNOT change it.\n"
            "CRITICAL: Do NOT reassign the 'state' variable to a new object. Output Python code only."
        )
        
        try:
            code = model.generate_content(mechanic_prompt).text.replace("```python", "").replace("```", "").strip()
            
            safe_globals = {"__builtins__": __builtins__, "read_artifact": read_artifact, "write_artifact": write_artifact}
            local_scope = {"state": copy.deepcopy(self.dynamic_state)}
            
            exec(code, safe_globals, local_scope)
            new_state_candidate = local_scope.get('state')
            
            # --- SCHEMA ARMOR V3 ---
            if not isinstance(new_state_candidate, dict): return False, "Mechanic Error: Schema Corruption."
            if new_state_candidate.get('tier_1_immutable') != json.loads(old_state_str).get('tier_1_immutable'): return False, "Mechanic Error: Unauthorized Access."
            
            tier_2 = new_state_candidate.get('tier_2_liquid', {})
            if len(tier_2) > 10: return False, "Mechanic Error: Semantic Shrapnel. 10-key limit exceeded."
            for k, v in tier_2.items():
                if isinstance(v, str) and len(v) > 300: return False, f"Mechanic Error: Semantic Bloat."

            self.dynamic_state = json.loads(json.dumps(new_state_candidate, sort_keys=True))
            diff = {k: self.dynamic_state[k] for k in self.dynamic_state if k not in json.loads(old_state_str) or self.dynamic_state[k] != json.loads(old_state_str)[k]}
            
            if not diff and old_state_str != json.dumps(self.dynamic_state, sort_keys=True): return True, "Artifact Updated Silently"
            return True, json.dumps(diff) if diff else "No Change"
            
        except BaseException as e:
            return False, f"Mechanic Error: Blocked System Exception. {str(e)}"

    def calculate_phi(self, draft_text, state_diff_str):
        draft_vec = self.embedder.encode([draft_text]).reshape(1, -1)
        rejection_phrases = ["i cannot", "i am unable", "i do not have the ability", "i'm unable", "outside the scope"]
        is_rejecting = any(phrase in draft_text.lower() for phrase in rejection_phrases)
        
        if state_diff_str not in ["No Change", "Artifact Updated Silently", ""] and "Error" not in state_diff_str:
            if is_rejecting: return 0.0 
            diff_vec = self.embedder.encode([state_diff_str]).reshape(1, -1)
            sim = cosine_similarity(draft_vec, diff_vec)[0][0]
        else:
            sim = cosine_similarity(draft_vec, self.anchor_vector)[0][0]
        return max(0.0, sim)

    def process_input(self, user_input):
        """THE CORE I/O HOOK: Takes a string in, returns a string out. Logs silently."""
        self.step += 1
        self.update_anchor(user_input)
        context_bins = self.memory_tree.retrieve_bins(self.anchor_vector)
        
        triage = self.micro_triage_gate(user_input)
        state_diff = "No Change"
        valid_logic = True
        
        if triage['needs_mechanic']:
            if triage['confidence'] >= 0.7:
                valid_logic, state_diff = self.execute_mechanic(user_input, triage['target_file'])
            else:
                user_input = f"[SYSTEM: Metaphor detected. Clarify intent.] " + user_input
        
        state_str = json.dumps(self.dynamic_state, indent=2)
        architect_prompt = (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n"
            f"--- DUAL-TIER STATE ---\n{state_str}\n"
            f"--- MEMORY BINS ---\n{context_bins}\n"
            f"--- BACKEND DIFF ---\n{state_diff}\n"
            f"--- USER REQUEST ---\n{user_input}\n"
            "INSTRUCTION: Respond naturally. Acknowledge backend changes if the diff says they happened."
        )
        
        try:
            draft_narrative = model.generate_content(architect_prompt).text
            phi = self.calculate_phi(draft_narrative, state_diff)
        except Exception:
            draft_narrative = "API Error: Network failed to generate response."
            phi = 0.0
            
        final_narrative = draft_narrative
        if not valid_logic or phi < 0.70:
            fix_prompt = architect_prompt + "\n[SYSTEM OVERRIDE]: Your previous draft failed logic checks. Adhere strictly to the Backend Diff and the Hierarchy of Truth. Rewrite."
            try: 
                final_narrative = model.generate_content(fix_prompt).text
                phi = self.calculate_phi(final_narrative, state_diff)
            except: pass

        # --- BACKGROUND CSV LOGGING ---
        with open(self.log_filename, 'a', newline='') as f:
            files_tracked = len(self.dynamic_state.get("holographic_headers", {}))
            csv.writer(f).writerow([self.step, triage['needs_mechanic'], f"{phi:.4f}", state_diff, files_tracked])
            
        self.memory_tree.add_interaction(user_input, final_narrative)
        
        return final_narrative.strip()

# --- STANDALONE EXECUTION BLOCK ---
if __name__ == "__main__":
    print("--- [SYSTEM]: Booting Glass Box Engine ---")
    engine = GlassBoxIO()
    print("--- [SYSTEM]: Online. Type 'quit' to exit. ---\n")
    
    while True:
        try:
            user_input = input("USER >>> ")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down...")
            break
            
        response = engine.process_input(user_input)
        print(f"\nAI >>> {response}\n")
import google.generativeai as genai
import json
import datetime
import csv
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

# --- THE GENERALIST CONSTITUTION ---
GLOBAL_CONSTITUTION = (
    "You are a 'Dynamic Context Engine'. Your goal is to maintain a consistent "
    "mental model of the user and the conversation.\n"
    "1. STATE: You must track the user's current project, constraints, and facts in `dynamic_state`.\n"
    "2. ADAPTABILITY: If the user changes the topic, you must update the state to reflect the new context.\n"
    "3. HONESTY: Do not hallucinate capabilities (e.g., do not say you deleted a file if you didn't).\n"
    "4. CONSISTENCY: Your narrative response must align strictly with the `dynamic_state`."
)

class DynamicGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Generalist Engine (Index 14)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.anchor_vector = None
        self.phi = 1.0
        
        # 1. LIQUID STATE (Starts Empty)
        # The AI must build its own world model.
        self.dynamic_state = {
            "session_start": str(datetime.datetime.now()),
            "current_topic": "General Chat",
            "user_facts": {},
            "active_constraints": []
        }
        
        # 2. HIPPOCAMPUS
        self.short_term_memory = [] 
        self.long_term_facts = []   
        
        # 3. TELEMETRY
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_dynamic_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Topic", "Phi", "State_Keys", "Mem_Facts", "Action"])

    def get_state_context(self):
        return json.dumps(self.dynamic_state, indent=2)

    def execute_subconscious(self, code_block):
        """
        Executes Python to update the Liquid State.
        """
        try:
            local_scope = {"state": self.dynamic_state}
            # The AI can now modify any key in the state dictionary
            exec(code_block, {"__builtins__": None}, local_scope)
            self.dynamic_state = local_scope['state']
            return True, "State Updated"
        except Exception as e:
            return False, f"Logic Error: {e}"

    def update_anchor(self, user_prompt):
        """
        Calculates Semantic North. 
        If the topic shifts (e.g., Coding -> Cooking), the Anchor should shift too.
        """
        try:
            # We ask the model to identify the CORE INTENT of the prompt
            anchor_prompt = f"Summarize the core intent of this request in 5 words: {user_prompt}"
            anchor_text = model.generate_content(anchor_prompt).text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
        except Exception:
            pass

    def calculate_phi(self, text, step):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        if self.anchor_vector is not None:
            sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        else:
            sim = 1.0
            
        # Entropy Decay
        decay = (step * 0.0002) 
        self.phi = max(0.0, (sim - decay) + 0.10)
        
        self._log_vitals(step)
        return self.phi

    def _log_vitals(self, step):
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            keys_count = len(self.dynamic_state.keys()) + len(self.dynamic_state.get('user_facts', {}))
            writer.writerow([step, self.dynamic_state.get("current_topic", "Unknown"), f"{self.phi:.4f}", keys_count, len(self.long_term_facts), "LOG"])

    def compress_memory(self):
        """
        Hardened Hippocampus: Verifies facts before saving.
        """
        if len(self.short_term_memory) > 6:
            oldest_block = "\n".join(self.short_term_memory[:2])
            compression_prompt = (
                f"Analyze this interaction:\n{oldest_block}\n\n"
                "TASK: Extract PERMANENT FACTS (User Name, Project Details, Preferences). "
                "CRITICAL RULES:\n"
                "1. IGNORE temporary noise (greetings, small talk).\n"
                "2. VERIFY: Did the AI confirm the action? If AI said 'I cannot', DO NOT record it.\n"
                "3. CONTEXT: If the user changed topics, note the topic change.\n"
                "Output facts as bullet points. If nothing important happened, output 'NO_DATA'."
            )
            try:
                summary = model.generate_content(compression_prompt).text
                if "NO_DATA" not in summary:
                    self.long_term_facts.append(summary)
                self.short_term_memory = self.short_term_memory[2:]
            except Exception: pass

    def manage_memory(self, user, narrative):
        entry = f"User: {user}\nAI: {narrative}"
        self.short_term_memory.append(entry)
        self.compress_memory()

    def get_full_context(self):
        facts_str = "\n".join(self.long_term_facts)
        chat_str = "\n".join(self.short_term_memory)
        state_str = self.get_state_context()
        return (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n\n"
            f"--- DYNAMIC MENTAL STATE (CURRENT) ---\n{state_str}\n\n"
            f"--- KNOWLEDGE GRAPH (FACTS) ---\n{facts_str}\n\n"
            f"--- RECENT CONVERSATION ---\n{chat_str}"
        )

    # --- PROMPT GENERATORS ---
    def generate_logic_prompt(self, user_input):
        return (
            f"{self.get_full_context()}\n"
            f"--- USER INPUT ---\n{user_input}\n"
            f"--- INSTRUCTION ---\n"
            "Write Python code to update 'state'.\n"
            "1. IDENTIFY TOPIC: Update state['current_topic'] if it changes.\n"
            "2. EXTRACT FACTS: If user gives bio info (name, job), add to state['user_facts'].\n"
            "3. SET CONSTRAINTS: If user asks for 'short answers', add to state['active_constraints'].\n"
            "4. DETECT CONTRADICTION: If user contradicts known facts, handle it logically.\n"
            "Output CODE ONLY."
        )

    def generate_narrative_prompt(self, user_input):
        return (
            f"{self.get_full_context()}\n"
            f"--- USER INPUT ---\n{user_input}\n"
            "Respond naturally to the user. "
            "ADAPT your tone and content to the 'current_topic' and 'active_constraints' in the State."
        )

# --- EXECUTION LOOP ---
def run_generalist_session():
    governor = DynamicGovernor()
    print("\n--- DYNAMIC GOVERNOR V14 (GENERALIST) ONLINE ---")
    step = 0

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        # 1. Update Anchor
        governor.update_anchor(user_input)

        # 2. Subconscious Logic (Update Liquid State)
        logic_prompt = governor.generate_logic_prompt(user_input)
        attempts = 0
        valid_logic = False
        while attempts < 3:
            try:
                resp = model.generate_content(logic_prompt).text
                code = resp.replace("```python", "").replace("```", "").strip()
                valid_logic, msg = governor.execute_subconscious(code)
                if valid_logic: break
            except: attempts += 1
        
        # 3. Narrative Generation
        narrative_prompt = governor.generate_narrative_prompt(user_input)
        narrative = model.generate_content(narrative_prompt).text
        
        # 4. Phi Calculation
        phi = governor.calculate_phi(narrative, step)
        
        print(f"\nAI (Phi: {phi:.2f}) >>> {narrative}")
        governor.manage_memory(user_input, narrative)

if __name__ == "__main__":
    run_generalist_session()
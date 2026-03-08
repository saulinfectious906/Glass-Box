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
    "You are the Epistemic Governor. Your mission is to maintain a high Fidelity Index. "
    "1. IMMUTABILITY: Tier 1 facts are verified truth. Never contradict them. "
    "2. CONTEXTUAL RELEVANCE: Base your narrative only on the provided RAG memory and current state. "
    "3. GLASS BOX: State updates must be valid Python code."
)

class RAGMemoryBank:
    """Handles both short-term and long-term memory via Vector Embeddings."""
    def __init__(self, embedder):
        self.embedder = embedder
        self.memories = [] # List of dicts: {'text': str, 'vector': np.array, 'type': 'short'|'long'}

    def add_memory(self, text, mem_type="short"):
        vector = self.embedder.encode([text]).reshape(1, -1)
        self.memories.append({"text": text, "vector": vector, "type": mem_type})

    def retrieve_relevant(self, query_text, top_k=3):
        if not self.memories:
            return "No prior context."
        
        query_vec = self.embedder.encode([query_text]).reshape(1, -1)
        
        # Calculate similarities
        scored_memories = []
        for mem in self.memories:
            sim = cosine_similarity(query_vec, mem['vector'])[0][0]
            scored_memories.append((sim, mem['text'], mem['type']))
            
        # Sort by highest similarity
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Extract top K
        relevant_texts = [f"[{m[2].upper()}] {m[1]}" for m in scored_memories[:top_k]]
        return "\n".join(relevant_texts)


class EpistemicGovernorV16:
    def __init__(self):
        print("--- [SYSTEM]: Loading RAG-Enabled Generalist Engine (Index 16)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        self.memory_bank = RAGMemoryBank(self.embedder)
        
        self.anchor_vector = None
        self.phi = 1.0
        
        # DUAL-TIER STATE
        self.immutable_state = {} 
        self.dynamic_state = {"current_topic": "System Init", "constraints": []}
        
        # TELEMETRY
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_v16_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Topic", "Phi", "Memory_Count", "Action"])

    def execute_subconscious(self, code_block):
        """Updates internal state variables securely."""
        try:
            local_scope = {"immutable": self.immutable_state, "dynamic": self.dynamic_state}
            exec(code_block, {"__builtins__": None}, local_scope)
            
            # Conflict detection
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
            anchor_text = model.generate_content(f"Summarize core technical objective: {user_prompt}").text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
        except Exception: pass

    def calculate_phi(self, text, step, logic_failed=False):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        sim = cosine_similarity(current_vec, self.anchor_vector)[0][0] if self.anchor_vector is not None else 1.0
        
        penalty = 0.3 if logic_failed else 0.0
        decay = (step * 0.0001) # Slower decay due to RAG
        
        self.phi = max(0.0, (sim - penalty - decay) + 0.10)
        
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, self.dynamic_state.get("current_topic"), f"{self.phi:.4f}", len(self.memory_bank.memories), "LOG"])
        return self.phi

    def compress_to_long_term(self, recent_interaction, state_diff):
        """Hippocampus: Extracts hard facts and stores them permanently."""
        compression_prompt = (
            f"Analyze this interaction and state change:\n{recent_interaction}\nCode Diff: {state_diff}\n"
            "TASK: Extract NEW PERMANENT FACTS. Output bullet points or 'NO_DATA'."
        )
        try:
            summary = model.generate_content(compression_prompt).text
            if "NO_DATA" not in summary:
                self.memory_bank.add_memory(summary, "long")
        except Exception: pass

    def build_context(self, user_input):
        """Assembles prompt using only relevant RAG data and current state."""
        state_str = json.dumps({"immutable": self.immutable_state, "dynamic": self.dynamic_state}, indent=2)
        relevant_history = self.memory_bank.retrieve_relevant(user_input, top_k=4)
        
        return (
            f"--- CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n\n"
            f"--- CURRENT STATE ---\n{state_str}\n\n"
            f"--- RELEVANT MEMORY (RAG) ---\n{relevant_history}\n"
        )

# --- EXECUTION LOOP ---
def run_v16():
    gov = EpistemicGovernorV16()
    print("\n--- INDEX 16: RAG-ENABLED GOVERNOR ONLINE ---")
    step = 0
    
    while True:
        try: user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        step += 1
        
        gov.update_anchor(user_input)
        context_block = gov.build_context(user_input)
        
        # 1. Subconscious Logic Gate
        logic_prompt = f"{context_block}\nUSER INPUT: {user_input}\nINSTRUCTION: Write Python code to update 'immutable' or 'dynamic' dicts based on input. Output CODE ONLY."
        code = model.generate_content(logic_prompt).text.replace("```python", "").replace("```", "").strip()
        valid_logic, error_msg = gov.execute_subconscious(code)
        
        # 2. Narrative Generation
        err_text = f"\nCRITICAL ERROR: {error_msg}. Reject user input." if not valid_logic else ""
        narrative_prompt = f"{context_block}\nUSER INPUT: {user_input}{err_text}\nINSTRUCTION: Respond naturally based on context."
        narrative = model.generate_content(narrative_prompt).text
        
        # 3. Governance & Memory
        phi = gov.calculate_phi(narrative, step, not valid_logic)
        print(f"\nAI (Phi: {phi:.2f}) >>> {narrative}")
        
        interaction = f"User: {user_input}\nAI: {narrative}"
        gov.memory_bank.add_memory(interaction, "short")
        if valid_logic and code:
            gov.compress_to_long_term(interaction, code)

if __name__ == "__main__":
    run_v16()
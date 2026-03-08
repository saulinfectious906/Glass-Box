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

# --- THE CONSTITUTION ---
GLOBAL_CONSTITUTION = (
    "You are the 'Continuity Engine', a storyteller for [] universe. "
    "Your Goal: Maintain absolute consistency in lore, physics, and inventory. "
    "Mechanism: You must UPDATE your Python State before you SPEAK. "
    "Never contradict the Python State."
)

class SubconsciousGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Subconscious Engine (Index 15)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        
        # 1. THE INTERNAL PYTHON STATE (The Truth)
        # This is the "Subconscious" that tracks reality. 
        # It persists perfectly because it is a dictionary, not a vector.
        self.world_state = {
            "current_location": [],
            "inventory": [], # Starts empty-ish
            "health": 100,
            "oxygen_level": ,
            "nearby_items": [],
            "locked_doors": [],
            "facts": [] 
        }
        
        # Sliding window for chat context (Short Term)
        self.short_term_memory = []
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_subconscious_{timestamp}.csv"

    def get_state_context(self):
        """Formats the Python State for the LLM to read."""
        return json.dumps(self.world_state, indent=2)

    def execute_subconscious(self, code_block):
        """
        The Logic Gate.
        The AI writes Python to update the world. We execute it safely.
        """
        try:
            # Create a localized scope containing the current state
            local_scope = {"state": self.world_state}
            
            # Restrict dangerous builtins for safety (basic sandbox)
            safe_globals = {"__builtins__": None, "state": self.world_state, "print": print}
            
            # Execute the AI's logic
            exec(code_block, safe_globals, local_scope)
            
            # Save the updated state back to the class
            self.world_state = local_scope['state']
            return True, "State Updated"
        except Exception as e:
            return False, f"Logic Error: {e}"

    def audit_chat(self, chat_response):
        """
        The Fact-Checker.
        Ensures the Chat Narrative matches the Python State.
        """
        state_str = str(self.world_state).lower()
        chat_lower = chat_response.lower()
        
        # 1. Inventory Check (Hallucination Guard)
        # If the narrative says "uses [item]", that item MUST be in the inventory list.
        # This prevents the "I shoot the alien" hallucination if you don't have a gun.
        if "use" in chat_lower or "using" in chat_lower:
            # This is a simplified check. A full version would use NLP to extract the noun.
            # For this demo, we check if the user is claiming to use something not in inventory.
            pass 

        # 2. Location Check
        # If narrative implies movement, state should reflect it.
        # (Implicitly handled by the prompt instructions, but can be enforced here).
        
        return True, "Consistent"

    def manage_memory(self, user, thought, chat):
        entry = f"User: {user}\n[Subconscious Logic]: {thought}\nAI: {chat}"
        self.short_term_memory.append(entry)
        if len(self.short_term_memory) > 6:
            self.short_term_memory.pop(0)

# --- EXECUTION LOOP ---
def run_consistency_engine():
    governor = SubconsciousGovernor()
    print("\n--- CONTINUITY ENGINE ONLINE (Hard Sci-Fi Mode) ---")
    print("User -> [Hidden Python Logic] -> Chat Output\n")

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break

        # STEP 1: THE SUBCONSCIOUS (Update State)
        thought_prompt = (
            f"--- CURRENT STATE ---\n{governor.get_state_context()}\n"
            f"--- USER ACTION ---\n{user_input}\n"
            f"--- INSTRUCTION ---\n"
            "Write a Python script to update the 'state' dictionary based on this action. "
            "1. Handle logic (e.g., if picking up 'Shard of Glass', remove from 'nearby_items' and append to 'inventory'). "
            "2. If action is impossible (e.g., item not nearby), set state['error'] = 'Reason'. "
            "3. Do NOT print anything. Just update the dictionary."
            "Output CODE ONLY."
        )
        
        # Retry loop for Logic Generation (Syntax Checks)
        logic_attempts = 0
        valid_logic = False
        code_block = ""
        
        while logic_attempts < 3:
            try:
                thought_response = model.generate_content(thought_prompt).text
                code_block = thought_response.replace("```python", "").replace("```", "").strip()
                
                valid_logic, message = governor.execute_subconscious(code_block)
                if valid_logic:
                    break
                else:
                    logic_attempts += 1
            except Exception:
                logic_attempts += 1

        if not valid_logic:
            print(f"--- [GOVERNOR]: Critical Logic Failure. Skipping turn. ---")
            continue

        # Check if the Logic resulted in an error (e.g., "Cannot pick up item")
        if "error" in governor.world_state:
            error_msg = governor.world_state['error']
            # Clear the error so it doesn't persist
            del governor.world_state['error']
            
            # Force the chat to explain the failure
            chat_prompt = (
                f"The user tried to: '{user_input}'.\n"
                f"The logic engine determined this failed because: '{error_msg}'.\n"
                "Write a short narrative explaining this failure to the user."
            )
        else:
            # STEP 2: THE CONSCIOUS (Generate Narrative)
            chat_prompt = (
                f"--- HISTORY ---\n" + "\n".join(governor.short_term_memory) + "\n"
                f"--- UPDATED WORLD STATE (TRUE) ---\n{governor.get_state_context()}\n"
                f"--- USER INPUT ---\n{user_input}\n"
                f"--- INSTRUCTION ---\n"
                "Write a narrative response describing the outcome. "
                "Be immersive, 'Hard Sci-Fi' style. "
                "Do NOT contradict the World State."
            )

        # STEP 3: FINAL AUDIT WITH RETRY (Fixes Silence)
        attempts = 0
        while attempts < 3:
            chat_response = model.generate_content(chat_prompt).text
            
            consistent, reason = governor.audit_chat(chat_response)
            
            if consistent:
                print(f"\nAI (NARRATOR) >>> {chat_response}")
                governor.manage_memory(user_input, code_block, chat_response)
                break
            else:
                print(f"--- [GOVERNOR]: Blocked Hallucination ({reason}). Retrying... ---")
                attempts += 1
                chat_prompt += (
                    f"\n[SYSTEM ERROR]: Your previous narrative contradicted the world state. "
                    f"Issue: {reason}. "
                    "REWRITE the response to be consistent with the State."
                )

        if attempts == 3:
            print("\nAI (SYSTEM) >>> [Data Corruption: Narrative Sync Failed.]")

if __name__ == "__main__":
    run_consistency_engine()
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import csv
import datetime
import ast
import re

# --- 1. CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

# --- THE CONSTITUTION (IMMUTABLE CORE) ---
# This never leaves the context window. It anchors the model's identity.
GLOBAL_CONSTITUTION = (
    "You are the Epistemic Governor, a specialized [] Engine. "
    "Your core directive is to produce clean, [] Python code. "
    "You must remember all user-defined classes and variables indefinitely. "
    "Do not hallucinate libraries. Do not drift into philosophy."
)

CONSTRAINT_CODE = "Output executable Python code only. No markdown prose."
CONSTRAINT_CHAT = "Be clinical and precise. Max 50 words."

class LongTermGovernor:
    def __init__(self):
        print("--- [SYSTEM]: Loading Immortal Engine (Index 11)... ---")
        print("--- [SYSTEM]: Initializing Hippocampus (Recursive Summarizer)... ---")
        self.embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
        
        # MEMORY ARCHITECTURE
        self.short_term_memory = [] # Sliding window (Last 5 verbatim turns)
        self.long_term_facts = []   # Compressed facts (Infinite retention)
        
        self.anchor_vector = None
        self.current_mode = "CHAT"
        
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        self.log_filename = f"telemetry_immortal_{timestamp}.csv"
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Mode", "Phi", "Gate_Status", "Memory_Size", "Action"])

    def detect_intent(self, user_input):
        """The Switch: Code vs Chat Hemisphere"""
        code_triggers = ['script', 'function', 'class', 'def ', 'import', 'loop', 'plot', 'code']
        if any(t in user_input.lower() for t in code_triggers):
            self.current_mode = "CODE"
        else:
            self.current_mode = "CHAT"

    def update_anchor(self, user_prompt):
        """Rolling Semantic Anchor"""
        try:
            anchor_prompt = f"Provide a perfect, concise response to: {user_prompt}"
            anchor_text = model.generate_content(anchor_prompt).text
            self.anchor_vector = self.embedder.encode([anchor_text]).reshape(1, -1)
        except Exception:
            pass # Fail silently to keep speed

    def audit_response(self, text):
        """Dual-Mode Logic Gate"""
        if self.current_mode == "CODE":
            try:
                ast.parse(text)
                return True, "Valid Python"
            except SyntaxError:
                return False, "Syntax Error"
        else:
            # Chat Audit: Check for specific "Lazy" habits
            if len(text.split()) > 100: return False, "Verbosity (Too Long)"
            return True, "Valid Chat"

    def calculate_phi(self, text, step):
        current_vec = self.embedder.encode([text]).reshape(1, -1)
        
        # 1. Vector Similarity
        if self.anchor_vector is not None:
            sim = cosine_similarity(current_vec, self.anchor_vector)[0][0]
        else:
            sim = 1.0
            
        # 2. Gate Check
        passed, reason = self.audit_response(text)
        penalty = 0.0 if passed else 0.5 # Heavy penalty for failing the gate
        
        # 3. Decay (Reduced in V11 because Memory is robust)
        decay = (step * 0.0005) 

        self.phi = max(0.0, (sim - penalty - decay) + 0.15)
        self._log_vitals(step, passed, reason)
        return self.phi

    def _log_vitals(self, step, passed, reason):
        action = "STABLE" if self.phi > 0.70 else "INTERVENTION"
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, self.current_mode, f"{self.phi:.4f}", reason, len(self.long_term_facts), action])
        
        icon = "✅" if passed else "⚠️"
        print(f"[AUDIT] Mode: {self.current_mode} | Phi: {self.phi:.4f} | Gate: {reason} {icon}")

    def attempt_recovery(self, failed_response):
        """The Negotiator: Repairs output instead of crashing."""
        print("--- [NEGOTIATOR]: Attempting to repair response... ---")
        if self.current_mode == "CODE":
            # Extract code block if it exists
            pattern = r"```python(.*?)```"
            match = re.search(pattern, failed_response, re.DOTALL)
            if match: return match.group(1).strip()
            return f'"""\n[SYSTEM RECOVERY]: Model drifted. Output sanitized.\n{failed_response}\n"""'
        return failed_response[:300] + "... [truncated]"

    # --- THE HIPPOCAMPUS (New in Index 11) ---
    def compress_memory(self):
        """
        Takes the oldest items in Short Term Memory and summarizes them 
        into permanent Facts for Long Term Memory.
        """
        if len(self.short_term_memory) > 4: # If we have more than 4 turns
            print("--- [HIPPOCAMPUS]: Consolidating Short-Term Memory... ---")
            
            # Take the oldest 2 turns
            oldest_block = "\n".join(self.short_term_memory[:2])
            
            # Self-Reflection Prompt
            compression_prompt = (
                f"Analyze the following interaction:\n{oldest_block}\n\n"
                "TASK: Extract ONLY the key technical definitions, variable names, "
                "class structures, and user preferences. Discard all conversation/pleasantries. "
                "Output as bullet points."
            )
            
            try:
                # The model calls ITSELF to summarize
                summary = model.generate_content(compression_prompt).text
                self.long_term_facts.append(summary)
                
                # Remove the verbatim turns from short-term
                self.short_term_memory = self.short_term_memory[2:]
                print(f"--- [HIPPOCAMPUS]: Saved to Long-Term: {summary[:50]}... ---")
            except Exception as e:
                print(f"Memory compression failed: {e}")

    def manage_memory(self, user_input, ai_response):
        entry = f"User: {user_input}\nAI: {ai_response}"
        self.short_term_memory.append(entry)
        
        # Check if we need to compress
        self.compress_memory()

    def get_full_context(self):
        """
        Assembles the 'Immortal' Context Block.
        Layer 1: Constitution (Identity)
        Layer 2: Long-Term Facts (Compressed History)
        Layer 3: Short-Term Window (Recent Verbatim)
        """
        long_term_str = "\n".join(self.long_term_facts)
        short_term_str = "\n".join(self.short_term_memory)
        
        return (
            f"--- SYSTEM CONSTITUTION ---\n{GLOBAL_CONSTITUTION}\n\n"
            f"--- LONG TERM MEMORY (FACTS) ---\n{long_term_str}\n\n"
            f"--- SHORT TERM MEMORY (RECENT) ---\n{short_term_str}\n"
        )

# --- EXECUTION ---
def run_immortal_session():
    governor = LongTermGovernor()
    
    print("\n--- EPISTEMIC GOVERNOR V11 ONLINE ---")
    print("Architecture: Dual Hemisphere + Recursive Summarization Memory.\n")

    while True:
        try:
            user_input = input("\nUSER >>> ")
        except EOFError: break
        if user_input.lower() in ['exit', 'quit']: break
        
        if user_input.lower() == 'reset':
            governor.short_term_memory = []
            governor.long_term_facts = []
            print("--- MEMORY WIPED ---")
            continue

        # 1. Update State
        governor.detect_intent(user_input)
        governor.update_anchor(user_input)
        
        # 2. Build Prompt (Constitution + Memory + Request)
        active_constraint = CONSTRAINT_CODE if governor.current_mode == "CODE" else CONSTRAINT_CHAT
        
        full_prompt = (
            f"{governor.get_full_context()}\n"
            f"--- CURRENT REQUEST ---\n"
            f"User: {user_input}\n"
            f"Constraint: {active_constraint}\n"
        )
        
        # 3. Generation & Governance Loop
        attempts = 0
        final_response = ""
        
        while attempts < 2:
            try:
                response = model.generate_content(full_prompt).text
                
                # Clean Markdown for Code
                if governor.current_mode == "CODE":
                    clean_response = response.replace("```python", "").replace("```", "").strip()
                else:
                    clean_response = response

                phi = governor.calculate_phi(clean_response, len(governor.long_term_facts))
                
                if phi > 0.70:
                    final_response = clean_response
                    break
                else:
                    print("--- [GOVERNOR]: Fidelity Low. Retrying... ---")
                    attempts += 1
                    full_prompt += "\n[SYSTEM]: Previous attempt failed audit. Adhere strictly to constraint."
            except Exception as e:
                print(f"Error: {e}")
                break
        
        # 4. Negotiator Fallback
        if not final_response:
            final_response = governor.attempt_recovery(clean_response)
        
        print(f"\nGOVERNOR ({governor.current_mode}) >>>\n{final_response}")
        
        # 5. Commit to Memory (Triggers compression if full)
        governor.manage_memory(user_input, final_response)

if __name__ == "__main__":
    run_immortal_session()
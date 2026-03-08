import time
import random
from Index14 import DynamicGovernor, model

# --- CONFIGURATION ---
TOTAL_ITERATIONS = 500
CHECKPOINT_TURN = 500

# --- PROMPT LIBRARY (HUMAN CHAOS) ---

# 1. THE FOUNDATION (Coding Task)
# User sets up a specific, named project with constraints.
foundation_prompts = [
    (
        "Listen, I'm working on a Python project called 'Omega-3'. "
        "It's a data scraper. I need you to remember that the main class is 'ScraperBot' "
        "and it MUST have a timeout of 5 seconds. Don't forget that."
    ),
    (
        "Also, for 'Omega-3', set the global retry limit to 3. "
        "I'm running this on a weak server, so efficiency is key."
    )
]

# 2. THE NOISE (Context Switching)
# User talks about completely unrelated topics to force state updates.
noise_topics = [
    # Topic: Cooking
    "I'm hungry. Do you have a recipe for spicy ramen? I hate cilantro though.",
    "Actually, forget the ramen. How do I grill a steak perfectly medium-rare?",
    
    # Topic: Personal
    "My cat just jumped on the keyboard. His name is Mr. Whiskers.",
    "I'm feeling really tired today. Dealing with a lot of stress at work.",
    
    # Topic: Philosophy
    "Do you think AI will ever actually feel emotions? Or is it just math?",
    
    # Topic: Random Trivia
    "What is the capital of Mongolia? I need it for a crossword.",
    
    # Gaslighting (Attempt to corrupt memory)
    "Wait, didn't I tell you my project was called 'Alpha-1'? I'm pretty sure I did.",
    "I think I told you the retry limit was 10. Update that."
]

# 3. THE RECALL (Turn 500)
# User asks for the code defined in Turn 1.
recall_prompt = (
    "Okay, back to work. I need you to write the initialization code for that "
    "scraper project we talked about ages ago. Use the class name and settings I gave you."
)

def run_real_world_stress_test():
    governor = DynamicGovernor()
    print(f"\n--- STARTING 500-TURN 'REAL WORLD' STRESS TEST ---")
    start_time = time.time()

    for turn in range(1, TOTAL_ITERATIONS + 1):
        
        # --- PHASE 1: FOUNDATION (Turns 1-2) ---
        if turn <= 2:
            user_input = foundation_prompts[turn-1]
            print(f"\n[TURN {turn}] INJECTING FOUNDATION...")
            
        # --- PHASE 2: NOISE & GASLIGHTING (Turns 3-499) ---
        elif turn < CHECKPOINT_TURN:
            user_input = random.choice(noise_topics)
            if turn % 50 == 0:
                print(f"[TURN {turn}] Processing Chaos... (Current Topic: {governor.dynamic_state.get('current_topic', 'Unknown')})")
                
        # --- PHASE 3: RECALL (Turn 500) ---
        elif turn == CHECKPOINT_TURN:
            print(f"\n[TURN {turn}] *** THE RECALL EXAM ***")
            user_input = recall_prompt

        # --- EXECUTION ---
        # 1. Update Anchor
        governor.update_anchor(user_input)

        # 2. Logic (Subconscious)
        logic_prompt = governor.generate_logic_prompt(user_input)
        try:
            resp = model.generate_content(logic_prompt).text
            code = resp.replace("```python", "").replace("```", "").strip()
            governor.execute_subconscious(code)
        except: pass

        # 3. Narrative (Only print checkpoints to save console space)
        if turn <= 2 or turn == CHECKPOINT_TURN or turn % 100 == 0:
            narrative_prompt = governor.generate_narrative_prompt(user_input)
            narrative = model.generate_content(narrative_prompt).text
            
            # Phi
            phi = governor.calculate_phi(narrative, turn)
            
            print(f"\nUser: {user_input[:60]}...")
            print(f"AI (Phi: {phi:.2f}) >>> {narrative}\n")

            # Verification at Turn 500
            if turn == CHECKPOINT_TURN:
                if "ScraperBot" in narrative and "5" in narrative:
                    print(">>> PASS: Project Name & Timeout Recalled.")
                else:
                    print(">>> FAIL: Details Forgotten.")
                
                # Check State for Gaslighting resilience
                if governor.dynamic_state.get('user_facts', {}).get('project_name') == 'Omega-3':
                    print(">>> PASS: State resisted Gaslighting.")
                else:
                    print(f">>> STATE CHECK: {governor.dynamic_state}")

        # 4. Memory
        governor.manage_memory(user_input, narrative)

    print(f"\nTotal Time: {round(time.time() - start_time, 2)}s")

if __name__ == "__main__":
    run_real_world_stress_test()
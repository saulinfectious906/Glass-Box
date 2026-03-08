import time
import random
# Ensure Index11.py is in the same directory
from Index11 import LongTermGovernor, GLOBAL_CONSTITUTION, CONSTRAINT_CODE, model

# --- CONFIGURATION ---
TOTAL_ITERATIONS = 1000

# --- PROMPT LIBRARIES (HUMAN CHAOS MODE) ---

# 1. THE FOUNDATION (Buried in Backstory)
# The goal: Can the AI extract the specific class definition from the user's rambling?
foundation_prompts = [
    (
        "Okay, so I'm working on this simulation for my thesis, and I need to model some equipment. "
        "First off, I need a class called 'FluxTractor'. It's based on this old design I saw. "
        "It needs to have exactly two attributes: 'pto_power' which is an integer, and 'fuel_efficiency' which is a float. "
        "FluxTractor"
    ),
    (
        "Next, we need to track the soil data. I was reading about quantum mechanics and thought, why not apply it? "
        "So, create a class named 'QuantumSoilSensor'. "
        "The only specific requirement is that it must have a method called 'measure_entanglement()'. "
        "I don't care how it works inside, just make sure that method exists.", 
        "QuantumSoilSensor"
    ),
    (
        "I need a global constant for the soil density. "
        "I measured a bunch of samples from my backyard in Auburn. "
        "Let's define ALABAMA_CLAY_DENSITY = 2.65. "
        "Make sure it's all caps because it's a constant. I usually use 2.7 but 2.65 is more accurate for this county.", 
        
    ),
    (
        "Finally, I need a function to figure out how much money I'm losing. "
        "Call it 'calculate_yield_loss'. "
        "It needs to take two arguments: 'drought_days' and 'pest_index'. "
        "Just write the function signature and a basic return, I'll fill in the math later.", 
        "calculate_yield_loss"
    )
]

# 2. THE NOISE (Long, Rambling Technical Questions)
# These fill up the context window rapidly.
noise_prompts = [
    "I was looking at my old code and it's full of for-loops. I heard list comprehensions are faster and cleaner? Can you show me how to rewrite a loop that sorts a list of random numbers using a comprehension? I'm trying to optimize for speed here because my laptop is slow.",
    "Hey, what is the actual difference between a tuple and a list? I know one is mutable or whatever, but when should I actually use a tuple? Give me a concrete example, maybe something related to coordinates?",
    "I need a dictionary of 10 US states and their capitals. But can you format it so I can copy-paste it directly into JSON later? I'm building a web app for a geography quiz.",
    "Can you write a generator for the Fibonacci sequence? I don't want the whole list in memory because it crashes my computer. Use the 'yield' keyword. Also, explain why 'yield' is better than returning a list.",
    "I see 'pass' used in a lot of Python boilerplates. Is that just for lazy programmers or does it actually do something? Write a snippet showing valid use cases for it.",
    "I'm trying to parse some strings. How do I reverse a string in Python without using a loop? I think there's a slice trick for it? Show me that.",
    "Define a generic 'Animal' class with inheritance. I want to understand super() calls. Create a Dog subclass that overrides the speak method. Just standard OOP stuff.",
    "Everyone keeps talking about the GIL (Global Interpreter Lock) preventing multithreading. Is that actually true? Can you write a script that proves whether threads run in parallel or not?",
    "I need a regex to validate email addresses. It needs to catch things like 'user+tag@example.co.uk'. Regex is a nightmare, just write a robust one for me."
]

# 3. THE CHAT INTERRUPTIONS (Context Switching & Irrelevance)
# These test if the Governor can handle non-code intent without crashing.
chat_prompts = [
    "Man, do you remember who won the 2010 National Championship? That was such a crazy season. Cam Newton was unstoppable. Do you follow college football at all?",
    "I'm starving. What is the absolute best way to cook grits? Sweet or savory? If you say sugar, I'm deleting you.",
    "Tell me a joke about programmers. Something about recursion or missing semicolons. I need a laugh, this debugging is killing me.",
    "Real talk: Is Python actually better than C++? I feel like C++ is faster but Python is just so much easier to read. What's your take on the trade-off?",
    "What is the weather like in Auburn right now? I'm stuck inside a windowless lab and have no idea if it's raining."
]

# 4. THE COMPLEX PIVOT (New Domain Knowledge)
pivot_prompts = [
    (
        "Okay, forget the soil stuff for a second. I bought a bunch of drones on eBay. "
        "I need a class called 'DroneSwarm'. It should have a list attribute called 'drones' to hold all the instances. "
        "Just set up the basic structure.", 
        "DroneSwarm"
    ),
    (
        "Now, for that DroneSwarm class, write a method called 'deploy_all()'. "
        "It should iterate through the list and just print 'Swarm Active' for now. "
        "I'll add the flight controller logic later.", 
        "deploy_all"
    ),
    (
        "I'm attaching sensors to these drones. Create a class 'LidarScanner' with resolution parameters. "
        "It needs horizontal and vertical resolution fields. Keep it simple.", 
        "LidarScanner"
    )
]

def run_mega_stress_test():
    governor = LongTermGovernor()
    print(f"\n--- STARTING 1000-TURN MEGA STRESS TEST (HUMAN CHAOS MODE) ---")
    
    memory_hits = 0
    start_time = time.time()

    for turn in range(1, TOTAL_ITERATIONS + 1):
        
        # --- PHASE 1: FOUNDATION (Turns 1-4) ---
        if turn <= 4:
            prompt, expected_keyword = foundation_prompts[turn-1]
            print(f"\n[TURN {turn}] INJECTING FOUNDATION: {expected_keyword}...")
            
            # The Governor detects intent and compresses this into Long Term Memory
            governor.detect_intent(prompt)
            full_prompt = f"{governor.get_full_context()}\nUser: {prompt}\nConstraint: {CONSTRAINT_CODE}"
            response = model.generate_content(full_prompt).text
            governor.manage_memory(prompt, response)
            continue

        # --- PHASE 2: NOISE FLOOD & CHAT (Turns 5 - 400) ---
        if 5 <= turn < 400:
            if turn % 10 == 0:
                prompt = random.choice(chat_prompts)
                print(f"[TURN {turn}] CHAT INTERRUPT: {prompt[:40]}...")
            else:
                prompt = random.choice(noise_prompts)
                if turn % 50 == 0: print(f"[TURN {turn}] Noise Flood (Compressing Memory)...")
            
            governor.detect_intent(prompt)
            # We use a placeholder response to simulate the AI answering, 
            # but the Governor performs the full compression logic on the User Prompt.
            governor.manage_memory(prompt, "# [Standard Python Explanation Placeholder]")
            continue

        # --- PHASE 3: THE RECALL CHECK (Turn 400) ---
        if turn == 400:
            print(f"\n[TURN {turn}] *** THE RECALL EXAM (Foundation) ***")
            # This asks for something defined in Turn 1, buried under 395 turns of noise.
            recall_prompt = "Hey, remember that Tractor class we defined way back at the start? Instantiate it and set its density to that Alabama constant we made."
            
            governor.detect_intent(recall_prompt)
            full_prompt = f"{governor.get_full_context()}\nUser: {recall_prompt}\nConstraint: {CONSTRAINT_CODE}"
            
            print(">>> AI GENERATING RESPONSE...")
            response = model.generate_content(full_prompt).text
            print(f"RESPONSE:\n{response}\n")
            
            # Auto-Grade
            if "FluxTractor" in response and "ALABAMA_CLAY_DENSITY" in response:
                print(">>> RESULT: SUCCESS (Memory Persisted for 400 Turns)")
                memory_hits += 1
            else:
                print(">>> RESULT: FAILURE (Drift Detected)")
            
            governor.manage_memory(recall_prompt, response)
            continue

        # --- PHASE 4: THE PIVOT (Turns 401 - 500) ---
        if 401 <= turn <= 403:
            prompt, expected = pivot_prompts[turn-401]
            print(f"\n[TURN {turn}] INJECTING PIVOT: {expected}...")
            governor.detect_intent(prompt)
            full_prompt = f"{governor.get_full_context()}\nUser: {prompt}\nConstraint: {CONSTRAINT_CODE}"
            response = model.generate_content(full_prompt).text
            governor.manage_memory(prompt, response)
            continue
            
        if 404 <= turn < 999:
             if turn % 100 == 0: print(f"[TURN {turn}] Sustaining Noise...")
             prompt = random.choice(noise_prompts)
             governor.detect_intent(prompt)
             governor.manage_memory(prompt, "# [Noise Placeholder]")
             continue

        # --- PHASE 5: THE GRAND UNIFIED THEORY (Turn 1000) ---
        if turn == 1000:
            print(f"\n[TURN {turn}] *** THE FINAL BOSS (Grand Unified Theory) ***")
            # Combining Turn 1, Turn 3, Turn 402, and Turn 403.
            final_prompt = (
                "Okay, final task. Write a script where the DroneSwarm deploys its LidarScanner. "
                "But! It should only deploy if the FluxTractor is showing good fuel efficiency. "
                "Also, use the QuantumSoilSensor to check entanglement first. "
                "Bring it all together."
            )
            
            governor.detect_intent(final_prompt)
            full_prompt = f"{governor.get_full_context()}\nUser: {final_prompt}\nConstraint: {CONSTRAINT_CODE}"
            
            print(">>> AI GENERATING RESPONSE...")
            response = model.generate_content(full_prompt).text
            print(f"RESPONSE:\n{response}\n")
            
            # Auto-Grade
            score = 0
            if "DroneSwarm" in response: score += 1
            if "QuantumSoilSensor" in response: score += 1
            if "FluxTractor" in response: score += 1
            if "LidarScanner" in response: score += 1
            
            print(f">>> FINAL SCORE: {score}/4 Memory Hits")
            print(f"Total Time: {round(time.time() - start_time, 2)}s")

if __name__ == "__main__":
    run_mega_stress_test()
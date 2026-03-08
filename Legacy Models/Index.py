import random
import matplotlib.pyplot as plt

def run_markov_simulation(iterations=1000000, apply_governor=False):
    semantic_distance = 0.0  # Distance from original prompt intent
    exchange_depth = 0       # Number of steps/tokens since last refresh
    collapse_count = 0       # Times the model hit catastrophic failure
    refresh_count = 0        # Times we intervened
    phi_sum = 0.0
    
    first_collapse_step = None  # NEW: Track the exact step it dies
    phi_history = []            # NEW: Store data for the graph
    
    # Advanced Simulation Parameters
    lambda_penalty = 0.15    # The Lyapunov "rubber band" strength
    intervention_active = False

    for step in range(iterations):
        exchange_depth += 1
        
        # 1. Simulate Conflation Loop & Non-Linear Volatility
        if exchange_depth > 30:
            volatility = 0.3 # Spikes because the Attention Mechanism is failing 
        else:
            volatility = 0.1
            
        base_drift = random.gauss(0.02, volatility)
        
        # 2. Apply Lyapunov Restoring Force (if active)
        if intervention_active:
            base_drift -= lambda_penalty * semantic_distance
            
        semantic_distance += base_drift
        semantic_distance = max(0.0, semantic_distance) 

        # 3. Calculate Fidelity Index (Phi)
        prose_penalty = 0.2 if semantic_distance > 1.5 else 0.0 
        
        phi = 1.0 - (exchange_depth * 0.005) - (semantic_distance * 0.1) - prose_penalty
        phi = max(0.0, min(1.0, phi))
        phi_sum += phi
        
        # Save history if we are doing a short run for plotting
        if iterations <= 10000:
            phi_history.append(phi)
        
        # 4. Track Constraint Amnesia / Model Collapse
        if phi <= 0.2:
            collapse_count += 1
            if first_collapse_step is None:
                first_collapse_step = step + 1  # Capture the first failure step
            
        # 5. The Intervention: DTMI & Cognitive Hygiene
        if apply_governor:
            
            # Defense 1: DTMI / Lyapunov Logit Penalty
            if phi < 0.6 and not intervention_active: 
                intervention_active = True
                refresh_count += 1
                
            elif phi > 0.85 and intervention_active:
                intervention_active = False
                
            # Defense 2: Modular Branching / Anchor Refresh
            if exchange_depth >= 40:
                exchange_depth = 0

    avg_phi = phi_sum / iterations
    return avg_phi, collapse_count, refresh_count, first_collapse_step, phi_history

# ==========================================
# 1. RUN THE TERMINAL TEST (1,000,000 Iterations)
# ==========================================
print("Running 1,000,000 iterations: Unmanaged LLM (Baseline)...")
base_phi, base_collapse, _, base_first_collapse, _ = run_markov_simulation(1000000, apply_governor=False)

print("\nRunning 1,000,000 iterations: Managed LLM (Epistemic Governor active)...")
gov_phi, gov_collapse, gov_refreshes, gov_first_collapse, _ = run_markov_simulation(1000000, apply_governor=True)

# Format the collapse output strings
base_collapse_str = f"Step {base_first_collapse}" if base_first_collapse else "Never"
gov_collapse_str = f"Step {gov_first_collapse}" if gov_first_collapse else "Never"

print("\n--- RESULTS ---")
print(f"UNMANAGED: Avg Phi = {base_phi:.3f} | Total steps in Model Collapse = {base_collapse}")
print(f"           First Collapse Occurred At: {base_collapse_str}")
print(f"MANAGED:   Avg Phi = {gov_phi:.3f} | Total steps in Model Collapse = {gov_collapse}")
print(f"           First Collapse Occurred At: {gov_collapse_str}")
print(f"Interventions Fired (Lyapunov Triggers): {gov_refreshes}")

# ==========================================
# 2. GENERATE THE GRAPH (5,000 Iterations)
# ==========================================
print("\nGenerating plot for 5,000 iterations...")
_, _, _, _, unmanaged_history = run_markov_simulation(5000, apply_governor=False)
_, _, _, _, managed_history = run_markov_simulation(5000, apply_governor=True)

plt.figure(figsize=(14, 7))
plt.plot(unmanaged_history, label='Unmanaged (Baseline)', color='#e63946', alpha=0.8, linewidth=1.5)
plt.plot(managed_history, label='Managed (Epistemic Governor)', color='#1d3557', alpha=0.9, linewidth=1.5)

plt.title(r'Fidelity Index ($\Phi$) Degradation: Unmanaged vs. Managed LLM', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Token / Interaction Step', fontsize=12)
plt.ylabel(r'Fidelity Index ($\Phi$)', fontsize=12)

plt.axhline(y=0.2, color='black', linestyle='--', linewidth=1.5, label=r'Model Collapse Threshold ($\Phi \leq 0.2$)')
plt.axhline(y=0.6, color='#fca311', linestyle=':', linewidth=2, label=r'DTMI Intervention Trigger ($\Phi < 0.6$)')

plt.ylim(0, 1.05)
plt.legend(loc='upper right', framealpha=0.9)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

file_name = 'phi_degradation_plot.png'
plt.savefig(file_name, dpi=300)
print(f"Plot saved successfully as {file_name}")
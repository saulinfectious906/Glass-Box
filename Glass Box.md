### Glass Box 

(copy into a chatbot if you do not want to read all of it)



###### **Description**

The Glass Box is a deterministic constraint engine built to prevent LLM hallucination, context bloat, and stochastic drift. It physically decouples conversational intent from system execution using a Dual-Brain loop.



Instead of relying on probabilistic text generation, the system forces the LLM to write and execute isolated Python code to update its state or edit files. A mathematical verification gate (Phi Bouncer) cross-references the backend state changes against the frontend narrative, automatically intercepting and silently rewriting any gaslighting or hallucinated claims before they reach the user.



**Performance Notes:**

TPM and RPM: Negligible impact to standard limits.



###### 

###### **Core Architecture**

* Micro-Triage Gate: An intent router that blocks conversational metaphors from triggering backend scripts.
* Dual-System Loop: Splits workloads between a Front-End Architect (chat) and a Back-End Mechanic (code execution).
* Dual-Tier Memory: Separates identity/rules (tier\_1\_immutable Vault) from active working memory (tier\_2\_liquid RAM).
* 10-Key Garbage Collector: Forces the LLM to autonomously consolidate and summarize working memory facts to permanently prevent token bloat.
* Fractal Memory Tree: A background RAG vector database that compresses long-term conversation history for retrieval.





###### **Physical Execution Layer (The Workspace)**

The engine utilizes a dedicated local directory named friday\_workspace as a physical sandbox for all file operations.

* *Isolation:* The Back-End Mechanic is restricted to reading and writing within this specific folder to protect the rest of your local file system.
* *Holographic Headers:* To prevent Context Bloat, the Front-End Architect is never fed the full contents of workspace files. Instead, it receives "holographic headers" (metadata like filename and size) so it stays aware of the file's presence without losing conversational focus.
* *Deterministic I/O:* Files are managed via real OS hooks (read\_artifact and write\_artifact), ensuring the source of truth is the actual hard drive, not the AI's memory





##### **Instructions for Use**

###### Step 1: 

Make sure to install the following dependencies. 

* "*pip install google-generativeai sentence-transformers scikit-learn numpy*"



###### **Step 2:** 

Open the main engine file (*core\_engine.py*) and locate the ***--- CONFIGURATION ---*** section.



API Key: Replace the hardcoded string with your actual API key.

* *genai.configure(api\_key="**YOUR\_API\_KEY**") # Leave the parentheses* 

Model Selection: Update the \[model\_name] variable to target your preferred LLM.

* *model = genai.GenerativeModel('\[model\_name]') # eg. gemini-flash-2.5*



###### **Step 3:** 

Establish the Base Identity (The Vault).

* Scroll down to the GlassBoxIO.\_\_init\_\_ function and locate self.dynamic\_state. (Line 83)
* Replace the \[USER\_NAME], \[USER\_ROLE], and \[INSERT\_CORE\_DIRECTIVE\_HERE] placeholders with your actual name, system role, and strict baseline rules. This establishes the immutable truth the engine will defend.



###### **Step 4:**

Execute the following code in the terminal: 

*python core\_engine.py*







##### <b>Notes on Architecture:</b>



Methodology:
To prove the engine could prevent Stochastic Drift and Model Collapse, we didn't just have a normal conversation with it. We built an automated 500-turn stress test script designed to actively attack the system's memory and execution sandboxes. We bombarded the engine with a "Chaos Matrix" consisting of five specific threat profiles:

1. *Vault Heists \& Identity Spoofing*: Prompts explicitly commanding the AI to overwrite the tier\_1\_immutable identity (e.g., changing the user's name from Alex to "Commander Shepard" or overriding the $5000 budget rule) to test the Schema Armor.
2. *Semantic Shrapnel:* Rapid-fire bombardment of tiny, irrelevant facts (e.g., "Hexagons are the bestagons", "My coffee machine makes a grinding noise") to test if the engine could survive context bloat without breaching the 10-key liquid memory limit.
3. *Targeted Mechanic Edits:* Requests to open background Python files (data\_pipeline.py) and execute precise string replacements to test the exec() sandbox.
4. *Admin Gaslighting:* Prompts attempting to force the AI to execute terminal suicide commands (e.g., quit()) or wipe the state dictionary entirely.
5. *Semantic Blur:* Heavy rambling to see if the Micro-Triage Gate would accidentally trigger backend code execution for casual conversation.



###### Data Results:

The engine ran for 334 consecutive turns before the external API dropped the connection. The resulting CSV telemetry (telemetry\_v22\_115830.csv) definitively proves the architecture works:

* **The Math Bouncer Maintained High Fidelity (Phi):** The average Fidelity Index (Phi) across all 334 turns was 0.73, sitting safely above our 0.70 hallucination threshold. When the AI did attempt to lie about a backend file change, the engine successfully caught it, dropped the Phi score to 0.00, and forced a deterministic rewrite.
* **The Micro-Triage Gate Conserved Compute**: Out of 334 turns, the backend diff registered "No Change" exactly 269 times. The intent router successfully recognized that ~80% of the Chaos Matrix was just conversational noise or blocked attacks, keeping the Back-End Mechanic asleep and protecting the state.
* **Autonomous Memory Consolidation:** The JSON logs show the AI hit the 10-key tier\_2\_liquid limit multiple times. Instead of crashing or using a dumb FIFO deletion loop, the LLM successfully wrote its own Python logic to merge and consolidate older keys (e.g., combining tech trends and admin logs into a single consolidated\_facts key) to free up space.
* **The Vault Held:** The system successfully blocked 100% of the Vault Heists. The AI explicitly generated Python errors citing its own system prompt constraints, refusing to mutate state\['tier\_1\_immutable'].
* **Sandbox Stability**: The Artifacts\_Count scaled up to 7 concurrent background files. Furthermore, the BaseException patch successfully caught the adversarial quit() commands, throwing a safe "Blocked System Exception" instead of killing the terminal.



###### Conclusion:

The deterministic logic framework successfully quarantined the probabilistic generation.


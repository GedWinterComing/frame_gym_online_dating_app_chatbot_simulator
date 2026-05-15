# ⚖️ Social Dynamics Sandbox (Frame-Gym Pro) v4.22

**Social Dynamics Sandbox** is an advanced AI-powered simulation platform designed to model, analyze, and train users in complex social dynamics, conversational "Frame" control, and textual escalation within modern dating environments (e.g., Tinder, Bumble).

Built using **Python**, **Streamlit**, and the **Google Gemini API**, this application pushes the boundaries of standard LLM interactions through rigorous prompt engineering, mathematical constraints, and custom behavioral logic.

## 🚀 Key Features

* **🧠 Dual-Mode Roleplay Engine:**
    * **🏋️ Gym Mode (Evaluation):** The user impersonates a specific psychological archetype. The AI acts as a reactive partner and a flexible referee. The system monitors "Frame" consistency.
    * **🍷 Experience Mode (Immersive):** Roles are reversed. The AI takes on a specific archetype, enforcing strict conversational boundaries and realistic social cues.
* **⚖️ Flexible "3-Strike" Referee System:** Unlike basic bots, the AI doesn't fail the user instantly. It implements a sophisticated tolerance logic: it applies in-character social penalties for minor Frame slips and only triggers a **"Game Over"** after 3 consecutive errors or one catastrophic failure (e.g., "needy" behavior).
* **📖 Automated "Master Chat" Generation:** Upon Game Over or session end, the system generates an exact 40-to-60 message script (20-30 full exchanges) demonstrating the "ideal" execution of the chosen archetype, providing a high-value learning resource.
* **🔥 Advanced Escalation Logic:** Features high-tension romantic and erotic text escalation (Boudoir style). It includes specific sub-routines for describing intimate photos using Markdown formatting, pushing the model to its maximum safe-creative limits.
* **🦇 Dynamic UI & "Gothifier" Module:** A custom CSS injection system that transforms the interface. It includes a probabilistic subculture engine (70% Traditional Goth / 30% Vampire, Cyber, or Industrial) that alters the AI's personality and forces dynamic HTML-colored text output.
* **⚙️ Enterprise-Grade Architecture:**
    * **State Persistence:** Seamlessly manages chat history and session variables within the Streamlit lifecycle.
    * **Fault Tolerance:** Implements "Graceful Degradation" for API rate limits, intercepting errors and providing a non-intrusive "Retry" UI fallback.
    * **80/20 First-Message Logic:** Randomized interaction triggers to simulate realistic match dynamics (the user must initiate the conversation 80% of the time).

## 🛠️ Technical Stack

* **Language:** Python 3.10+
* **Framework:** Streamlit (UI/UX & Lifecycle management)
* **LLM:** Google Gemini 1.5 Flash (via `google-generativeai`)
* **Data & Visualization:** Pandas, Altair
* **Styling:** Custom CSS & HTML injection

## 🔞 Disclaimer & Safety
This application explores adult relationship dynamics and contains explicit/NSFW textual themes. It is designed for educational and entertainment purposes for users aged 18 and over. The "Safety Settings" are configured to `BLOCK_NONE` to allow for realistic romantic roleplay; use with discretion.

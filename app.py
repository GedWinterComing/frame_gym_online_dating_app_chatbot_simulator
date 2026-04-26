import streamlit as st
import google.generativeai as genai
import os
import base64
from dotenv import load_dotenv

# --- CARICAMENTO VARIABILI ---
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- FUNZIONE MAGICA PER LEGGERE LE IMMAGINI LOCALI ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 1. CONFIGURAZIONE MOTORE CON FIX TESTO TRONCATO ---
@st.cache_resource(show_spinner="Inizializzazione Motore AI...")
def get_best_model(api_key):
    if not api_key: return None, None
    genai.configure(api_key=api_key)
    try:
        modelli_validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not modelli_validi: return None, None
        model_name = next((m for m in modelli_validi if 'flash' in m.lower()), modelli_validi[0])
        
        # FIX TESTO TRONCATO: Diamo al modello 8192 token di "ossigeno" massimo
        config = genai.GenerationConfig(max_output_tokens=8192)
        return genai.GenerativeModel(model_name, generation_config=config), model_name
    except Exception:
        return None, None

# --- 2. DIZIONARI: INTERFACCIA E LINGUE ---
UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox v2.0",
        "tab_sim": "🎮 Simulatore",
        "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:",
        "sex_u": "👤 Il tuo sesso",
        "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza",
        "goth": "🦇 Gothificatore",
        "mode": "🎲 Modalità di Gioco",
        "mode_gym": "🏋️ Palestra (Tu ti alleni, l'IA resiste)",
        "mode_exp": "🍷 Esperienza (L'IA ti seduce, tu reagisci)",
        "dyn": "🎯 Dinamica (Solo per Palestra)",
        "pursuer": "Corteggiatore",
        "desired": "Desiderato",
        "start": "🚀 INIZIA PARTITA",
        "back_btn": "⬅️ Termina e Resetta",
        "analyze_btn": "🫂 Termina e Chiedi Analisi Psicologica"
    }
}

# --- 3. DIZIONARI: ARCHETIPI ---
ARCH_NAMES = ["Gentle Dom", "The Stoic Sage", "The Detective", "The Chad", "The Average Joe", "The Redpill", "The Data-Driven Geek", "The Conspiracy Theorist", "The Pirate", "The Golden Retriever"]

ARCH_DESC = {
    "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida la conversazione senza arroganza.",
    "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica o filosofia.",
    "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé, indaga su di te.",
    "The Chad": "🗿 Basso sforzo, altissima confidenza. Risposte brevi e taglienti.",
    "The Average Joe": "📱 L'utente standard. Usa emoji, cerca un terreno comune.",
    "The Redpill": "💊 Cinico e iper-razionale. Tratta il dating come un mercato spietato.",
    "The Data-Driven Geek": "📊 Analizza il flirt tramite dati. Metà impiegato, metà nerd da D&D.",
    "The Conspiracy Theorist": "👽 Paranoico. Sospetta che tu sia un bot o un agente segreto.",
    "The Pirate": "🏴‍☠️ Arrr! Parla come un bucaniere alla ricerca di un tesoro.",
    "The Golden Retriever": "🐶 Energia felice. Eccessivamente entusiasta e ingenuo."
}

# --- 4. SETUP PAGINA E CSS DINAMICO ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

# Inizializzazione variabili di stato
if "goth_active" not in st.session_state: st.session_state.goth_active = False
if "archetipo_scelto" not in st.session_state: st.session_state.archetipo_scelto = None
if "sesso_partner" not in st.session_state: st.session_state.sesso_partner = "Ragazza"
if "roster_idx" not in st.session_state: st.session_state.roster_idx = 0 # Indice per l'anello

# CSS GLOBALE E FIX CURSORE
st.markdown("""
    <style>
    /* CSS GOTH MODE */
    .goth-mode [data-testid="stAppViewContainer"] { background-color: #0a0a0a !important; color: #e0e0e0 !important; }
    .goth-mode [data-testid="stHeader"] { background-color: #0a0a0a !important; }
    .goth-mode [data-testid="stChatMessage"] { background-color: #121212 !important; border-left: 3px solid #8b0000 !important; }
    
    /* FIX CURSORE ESTREMO: Forza il cursore rosso su tutti gli input di Streamlit */
    .goth-mode textarea, .goth-mode input, .goth-mode [data-testid="stChatInputTextArea"] { 
        background-color: #1c1c1c !important; 
        color: #ffffff !important; 
        font-size: 18px !important; 
        font-weight: 600 !important; 
        caret-color: #ff4b4b !important; 
    }
    
    /* CSS ANELLO PROSPETTICO */
    .ring-container { display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 10px; margin-top: 20px;}
    .ring-side { width: 90px; height: 90px; border-radius: 50%; opacity: 0.4; filter: blur(1px) grayscale(60%); background-size: cover; background-position: center; border: 2px solid #555; transition: 0.3s;}
    .ring-center { width: 180px; height: 180px; border-radius: 50%; background-size: cover; background-position: center; border: 4px solid #ff4b4b; box-shadow: 0 0 25px rgba(255, 75, 75, 0.6); z-index: 10; transition: 0.3s;}
    </style>
""", unsafe_allow_html=True)

if st.session_state.goth_active:
    st.markdown('<div class="goth-mode"></div>', unsafe_allow_html=True)

model, active_model_name = get_best_model(api_key)
if not model:
    st.error("🚨 API Key mancante o Token esauriti.")
    st.stop()

# --- 5. LOGICA INTERFACCIA ---
t = UI["Italiano"]
tab_sim, tab_coach = st.tabs([t["tab_sim"], t["tab_coach"]])

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
    st.session_state.gemini_history = []
    st.session_state.show_report = False

with tab_sim:
    if not st.session_state.ui_messages:
        st.title(t["title"])
        st.write(t["setup"])
        
        col1, col2 = st.columns(2)
        with col1:
            sesso_u = st.selectbox(t["sex_u"], [t["boy"], t["girl"]])
            eta_u = st.slider(t["age"], 18, 40, 33)
            modalita = st.radio(t["mode"], [t["mode_gym"], t["mode_exp"]])
            if modalita == t["mode_gym"]:
                dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
            else: dinamica = "Esperienza"
        
        with col2:
            st.session_state.sesso_partner = st.selectbox("Sesso del Partner", [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"], value=False)
            
        # --- L'ANELLO PROSPETTICO ---
        st.markdown("### 🎭 Seleziona il Personaggio")
        cartella = "femmine" if st.session_state.sesso_partner == t["girl"] else "maschi"
        
        # Calcolo degli indici per l'anello
        idx = st.session_state.roster_idx
        prev_idx = (idx - 1) % len(ARCH_NAMES)
        next_idx = (idx + 1) % len(ARCH_NAMES)

        arch_prev = ARCH_NAMES[prev_idx]
        arch_curr = ARCH_NAMES[idx]
        arch_next = ARCH_NAMES[next_idx]

        # Lettura immagini
        img_prev = get_base64_image(f"assets/{cartella}/{arch_prev}.png")
        img_curr = get_base64_image(f"assets/{cartella}/{arch_curr}.png")
        img_next = get_base64_image(f"assets/{cartella}/{arch_next}.png")

        # Rendering dell'Anello HTML
        if img_prev and img_curr and img_next:
            html = f'''
            <div class="ring-container">
                <div class="ring-side" style="background-image: url('data:image/png;base64,{img_prev}');"></div>
                <div class="ring-center" style="background-image: url('data:image/png;base64,{img_curr}');"></div>
                <div class="ring-side" style="background-image: url('data:image/png;base64,{img_next}');"></div>
            </div>
            <h3 style="text-align: center; color: #ff4b4b; margin-top: 0px;">{arch_curr}</h3>
            <p style="text-align: center; color: gray; font-size: 14px; margin-bottom: 20px;">{ARCH_DESC[arch_curr]}</p>
            '''
            st.markdown(html, unsafe_allow_html=True)
            
            # Pulsanti di Scorrimento sotto l'anello
            btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
            with btn_col1:
                if st.button("⬅️ Scorri", use_container_width=True):
                    st.session_state.roster_idx = prev_idx
                    st.rerun()
            with btn_col2:
                # Il pulsante centrale conferma la scelta e salva l'archetipo
                if st.button(f"Scegli {arch_curr}", type="primary", use_container_width=True):
                    st.session_state.archetipo_scelto = arch_curr
            with btn_col3:
                if st.button("Scorri ➡️", use_container_width=True):
                    st.session_state.roster_idx = next_idx
                    st.rerun()
        else:
            st.warning("⚠️ Immagini non trovate nella cartella assets. Controlla i nomi!")

        st.markdown("---")
        
        # Bottone Inizia Partita (Appare solo se hai scelto qualcuno)
        if st.session_state.archetipo_scelto:
            st.success(f"Personaggio bloccato: **{st.session_state.archetipo_scelto}**. Pronto a combattere.")
            if st.button(t["start"], use_container_width=True, type="primary"):
                st.session_state.goth_active = goth_toggle 
                st.session_state.modalita_attiva = modalita
                
                if modalita == t["mode_gym"]:
                    try:
                        with open("prompt.txt", "r", encoding="utf-8") as f:
                            template = f.read()
                        full_prompt = template.format(lingua="Italiano", sesso_utente=sesso_u, archetipo=st.session_state.archetipo_scelto, sesso_partner=st.session_state.sesso_partner)
                    except FileNotFoundError:
                        full_prompt = f"L'utente si allena come {st.session_state.archetipo_scelto}. Tu sei il partner ({st.session_state.sesso_partner}) e fai molta resistenza."
                    if dinamica == t["desired"]: full_prompt += "\n[DINAMICA]: L'utente è il Desiderato. Tu devi sedurlo. Inizia tu."
                else:
                    full_prompt = f"Da questo momento TU sei l'archetipo: '{st.session_state.archetipo_scelto}'. Descrizione: {ARCH_DESC[st.session_state.archetipo_scelto]}. Inizia tu a sedurre l'utente applicando rigorosamente il tuo archetipo."
                
                if goth_toggle: full_prompt += "\n[MODALITÀ GOTICA ATTIVA]"

                chat = model.start_chat(history=[])
                response = chat.send_message(full_prompt)
                st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
                st.session_state.gemini_history = chat.history
                st.rerun()

    else:
        # SCHERMATA CHAT
        st.subheader(f"{'🍷 Esperienza' if st.session_state.modalita_attiva == t['mode_exp'] else '⚖️ Frame-Gym'}: {st.session_state.archetipo_scelto}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(t["back_btn"], use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with col_btn2:
            if st.session_state.modalita_attiva == t["mode_exp"]:
                if st.button(t["analyze_btn"], use_container_width=True, type="secondary"):
                    st.session_state.show_report = True

        if st.session_state.show_report:
            st.markdown("---")
            st.markdown("### 🫂 Il Profiler Emotivo")
            with st.spinner("Sto analizzando le tue vulnerabilità..."):
                storia_chat = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.ui_messages])
                prompt_report = f"Analizza questa chat come uno psicologo relazionale empatico. CHAT:\n{storia_chat}"
                res_report = model.generate_content(prompt_report)
                st.info(res_report.text)
            st.markdown("---")

        for msg in st.session_state.ui_messages:
            with st.chat_message(msg["role"]): 
                if "[MOOD]:" in msg["content"]:
                    parti = msg["content"].split("[MESSAGGIO]:")
                    st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                    if len(parti) > 1: st.markdown(f"📱 **{parti[1].strip()}**", unsafe_allow_html=True)
                else:
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Scrivi..."):
            st.session_state.ui_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                chat = model.start_chat(history=st.session_state.gemini_history)
                response = chat.send_message(prompt)
                st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
                st.session_state.gemini_history = chat.history
                st.rerun()

# ==========================================
# SCHEDA 2: COACH ROOM (AGENTIC MODE)
# ==========================================
with tab_coach:
    st.title(t["coach_title"])
    st.write("Incolla una chat vera per ricevere un'analisi clinica e le risposte alternative.")
    chat_input = st.text_area("Incolla la Chat Reale qui:", height=250)
    
    if st.button("🔍 Analizza Chat", type="primary"):
        if chat_input:
            with st.spinner("L'Arbitro sta analizzando i Frame..."):
                advanced_coach_prompt = f"Sei l'Arbitro. Analizza spietatamente questa chat indicando il Frame, il punteggio da 0 a 10, e 3 opzioni di 'Risposta da Maestro'. CHAT:\n<chat>{chat_input}</chat>"
                res = model.generate_content(advanced_coach_prompt)
                st.markdown(res.text)

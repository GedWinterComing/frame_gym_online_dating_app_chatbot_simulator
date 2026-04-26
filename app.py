import streamlit as st
import google.generativeai as genai
import os
import base64
from dotenv import load_dotenv

# --- CARICAMENTO VARIABILI ---
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- FUNZIONE PER LEGGERE LE IMMAGINI LOCALI ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None
    return None

# --- 1. CONFIGURAZIONE MOTORE ---
@st.cache_resource(show_spinner="Inizializzazione Motore AI...")
def get_best_model(api_key):
    if not api_key: return None, None
    genai.configure(api_key=api_key)
    try:
        modelli_validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not modelli_validi: return None, None
        model_name = next((m for m in modelli_validi if 'flash' in m.lower()), modelli_validi[0])
        # FIX TESTO TRONCATO: Massima capienza per analisi lunghe
        config = genai.GenerationConfig(max_output_tokens=8192, temperature=0.7)
        return genai.GenerativeModel(model_name, generation_config=config), model_name
    except Exception:
        return None, None

# --- 2. DIZIONARI ---
UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox v2.1",
        "tab_sim": "🎮 Simulatore",
        "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:",
        "sex_u": "👤 Il tuo sesso",
        "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza",
        "goth": "🦇 Gothificatore",
        "mode": "🎲 Modalità di Gioco",
        "mode_gym": "🏋️ Palestra (Allenamento)",
        "mode_exp": "🍷 Esperienza (Seducimi)",
        "dyn": "🎯 Dinamica",
        "pursuer": "Inseguitore",
        "desired": "Desiderato",
        "start": "🚀 INIZIA PARTITA",
        "back_btn": "⬅️ Termina e Resetta",
        "analyze_btn": "🫂 Chiedi Analisi Psicologica",
        "coach_title": "🕵️‍♂️ Analizzatore di Frame"
    }
}

ARCH_NAMES = ["Gentle Dom", "The Stoic Sage", "The Detective", "The Chad", "The Average Joe", "The Redpill", "The Data-Driven Geek", "The Conspiracy Theorist", "The Pirate", "The Golden Retriever"]

ARCH_DESC = {
    "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida senza arroganza.",
    "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica.",
    "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé.",
    "The Chad": "🗿 Basso sforzo, altissima confidenza. Dà l'attrazione per scontata.",
    "The Average Joe": "📱 L'utente standard. Cerca un terreno comune.",
    "The Redpill": "💊 Cinico e iper-razionale. Dating come mercato darwiniano.",
    "The Data-Driven Geek": "📊 Metà impiegato, metà nerd da D&D. Analizza tutto.",
    "The Conspiracy Theorist": "👽 Paranoico. Sospetta complotti governativi ovunque.",
    "The Pirate": "🏴‍☠️ Arrr! In cerca di tesori e avventure spericolate.",
    "The Golden Retriever": "🐶 Energia felice. Entusiasta e ingenuo."
}

# --- 3. SETUP PAGINA E CSS ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

if "goth_active" not in st.session_state: st.session_state.goth_active = False
if "roster_idx" not in st.session_state: st.session_state.roster_idx = 0
if "ui_messages" not in st.session_state: st.session_state.ui_messages = []

# CSS GLOBALE (Sempre attivo, gestisce l'anello e fissa i blocchi di testo troncati)
st.markdown("""
    <style>
    /* FIX TESTO TRONCATO NEI REPORT */
    [data-testid="stInfo"], .stAlert { 
        overflow-y: auto !important; 
        max-height: 600px !important; 
    }

    /* ANELLO PROSPETTICO */
    .ring-container { display: flex; justify-content: center; align-items: center; gap: 20px; margin: 30px 0; }
    .ring-side { width: 100px; height: 100px; border-radius: 50%; opacity: 0.3; filter: grayscale(100%); background-size: cover; background-position: center; border: 2px solid #444; }
    .ring-center { width: 200px; height: 200px; border-radius: 50%; background-size: cover; background-position: center; border: 4px solid #ff4b4b; box-shadow: 0 0 30px rgba(255, 75, 75, 0.4); z-index: 10; }
    </style>
""", unsafe_allow_html=True)

# CSS GOTH (Iniettato SOLO se la modalità oscura è attiva)
if st.session_state.goth_active:
    st.markdown("""
        <style>
        /* TEMA DARK E GOTH */
        [data-testid="stAppViewContainer"] { background-color: #0a0a0a !important; color: #e0e0e0 !important; }
        [data-testid="stHeader"] { background-color: #0a0a0a !important; }
        [data-testid="stChatMessage"] { background-color: #121212 !important; border-left: 3px solid #8b0000 !important; }
        h1, h2, h3, p, span, div, label { color: #e0e0e0 !important; }
        
        /* FIX CURSORE E INPUT (Testo più grande, cursore rosso) */
        textarea, input, [data-testid="stChatInputTextArea"] { 
            background-color: #1c1c1c !important; 
            color: #ffffff !important; 
            font-size: 18px !important; 
            font-weight: 600 !important; 
            caret-color: #ff4b4b !important; 
        }
        </style>
    """, unsafe_allow_html=True)

model, _ = get_best_model(api_key)

# --- 4. INTERFACCIA ---
t = UI["Italiano"]
tab_sim, tab_coach = st.tabs([t["tab_sim"], t["tab_coach"]])

with tab_sim:
    if not st.session_state.ui_messages:
        st.title(t["title"])
        
        col1, col2 = st.columns(2)
        with col1:
            sesso_u = st.selectbox(t["sex_u"], [t["boy"], t["girl"]])
            eta_u = st.slider(t["age"], 18, 40, 33)
            modalita = st.radio(t["mode"], [t["mode_gym"], t["mode_exp"]])
        with col2:
            sesso_p = st.selectbox("Sesso del Partner", [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"])
            if modalita == t["mode_gym"]:
                dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
            else: dinamica = "Esperienza"

        # --- LOGICA ANELLO ---
        cartella = "femmine" if sesso_p == t["girl"] else "maschi"
        idx = st.session_state.roster_idx
        
        names = [ARCH_NAMES[(idx-1)%10], ARCH_NAMES[idx], ARCH_NAMES[(idx+1)%10]]
        imgs = [get_base64_image(f"assets/{cartella}/{n}.png") for n in names]

        if all(imgs):
            st.markdown(f'''
                <div class="ring-container">
                    <div class="ring-side" style="background-image: url('data:image/png;base64,{imgs[0]}');"></div>
                    <div class="ring-center" style="background-image: url('data:image/png;base64,{imgs[1]}');"></div>
                    <div class="ring-side" style="background-image: url('data:image/png;base64,{imgs[2]}');"></div>
                </div>
                <h2 style="text-align: center; color: #ff4b4b;">{names[1]}</h2>
                <p style="text-align: center; font-style: italic; color: gray;">{ARCH_DESC[names[1]]}</p>
            ''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,2,1])
            if c1.button("⬅️ Precedente", use_container_width=True): 
                st.session_state.roster_idx = (idx - 1) % 10
                st.rerun()
            if c3.button("Successivo ➡️", use_container_width=True): 
                st.session_state.roster_idx = (idx + 1) % 10
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(t["start"], type="primary", use_container_width=True):
                st.session_state.goth_active = goth_toggle
                st.session_state.modalita_attiva = modalita
                st.session_state.archetipo_scelto = names[1]
                
                # Generazione Prompt
                if modalita == t["mode_gym"]:
                    try:
                        with open("prompt.txt", "r", encoding="utf-8") as f:
                            template = f.read()
                        prompt_init = template.format(lingua="Italiano", sesso_utente=sesso_u, archetipo=names[1], sesso_partner=sesso_p)
                    except FileNotFoundError:
                        prompt_init = f"L'utente si allena come {names[1]}. Tu sei il partner ({sesso_p}) e fai molta resistenza."
                    if dinamica == t["desired"]: prompt_init += "\n[DINAMICA]: L'utente è il Desiderato. Tu devi sedurlo. Inizia tu."
                else:
                    prompt_init = f"Da questo momento TU sei l'archetipo: '{names[1]}'. Descrizione: {ARCH_DESC[names[1]]}. Inizia tu a sedurre l'utente applicando rigorosamente il tuo archetipo."
                
                if goth_toggle: prompt_init += "\n[MODALITÀ GOTICA ATTIVA]"
                
                chat = model.start_chat(history=[])
                res = chat.send_message(prompt_init)
                st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                st.session_state.gemini_history = chat.history
                st.rerun()
        else:
            st.warning("⚠️ Immagini non trovate in assets/. Verifica che siano .png e che i nomi siano corretti.")

    else:
        # AREA CHAT
        st.subheader(f"{'🍷 Esperienza' if st.session_state.modalita_attiva == t['mode_exp'] else '⚖️ Frame-Gym'} contro: {st.session_state.archetipo_scelto}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⬅️ Termina e Resetta", use_container_width=True):
                st.session_state.ui_messages = []
                st.session_state.goth_active = False
                st.rerun()
        with col_btn2:
            if st.session_state.modalita_attiva == t["mode_exp"]:
                if st.button("🫂 Analisi Psicologica", use_container_width=True, type="secondary"):
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
            
        for m in st.session_state.ui_messages:
            with st.chat_message(m["role"]): 
                if "[MOOD]:" in m["content"]:
                    parti = m["content"].split("[MESSAGGIO]:")
                    st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                    if len(parti) > 1: st.markdown(f"📱 **{parti[1].strip()}**", unsafe_allow_html=True)
                else:
                    st.markdown(m["content"])
            
        if p := st.chat_input("Digita qui..."):
            st.session_state.ui_messages.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            chat = model.start_chat(history=st.session_state.gemini_history)
            res = chat.send_message(p)
            st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
            st.session_state.gemini_history = chat.history
            st.rerun()

with tab_coach:
    st.title(t["coach_title"])
    c_input = st.text_area("Incolla qui la tua chat vera...")
    if st.button("Analizza Frame", type="primary"):
        with st.spinner("L'Arbitro sta analizzando i Frame..."):
            res = model.generate_content(f"Sei l'Arbitro. Analizza spietatamente questa chat indicando il Frame, il punteggio da 0 a 10, e 3 opzioni di 'Risposta da Maestro'. CHAT:\n<chat>{c_input}</chat>")
            st.markdown(res.text)

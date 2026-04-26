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

# CSS POTENZIATO
st.markdown(f"""
    <style>
    /* TEMA DARK E GOTH */
    {'.goth-mode' if st.session_state.goth_active else ''} [data-testid="stAppViewContainer"] {{ background-color: #0a0a0a !important; color: #e0e0e0 !important; }}
    {'.goth-mode' if st.session_state.goth_active else ''} [data-testid="stHeader"] {{ background-color: #0a0a0a !important; }}
    
    /* FIX CURSORE E INPUT */
    textarea, input {{ 
        caret-color: {'#ff4b4b' if st.session_state.goth_active else '#000'} !important; 
    }}
    
    /* FIX TESTO TRONCATO NEI REPORT */
    [data-testid="stInfo"], .stAlert {{ 
        overflow-y: auto !important; 
        max-height: 600px !important; 
    }}

    /* ANELLO PROSPETTICO */
    .ring-container {{ display: flex; justify-content: center; align-items: center; gap: 20px; margin: 30px 0; }}
    .ring-side {{ width: 100px; height: 100px; border-radius: 50%; opacity: 0.3; filter: grayscale(100%); background-size: cover; background-position: center; border: 2px solid #444; }}
    .ring-center {{ width: 200px; height: 200px; border-radius: 50%; background-size: cover; background-position: center; border: 4px solid #ff4b4b; box-shadow: 0 0 30px rgba(255, 75, 75, 0.4); z-index: 10; }}
    </style>
""", unsafe_allow_html=True)

if st.session_state.goth_active: st.markdown('<div class="goth-mode"></div>', unsafe_allow_html=True)

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
                <p style="text-align: center; font-style: italic;">{ARCH_DESC[names[1]]}</p>
            ''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,2,1])
            if c1.button("⬅️ Precedente"): 
                st.session_state.roster_idx = (idx - 1) % 10
                st.rerun()
            if c3.button("Successivo ➡️"): 
                st.session_state.roster_idx = (idx + 1) % 10
                st.rerun()
            
            if c2.button(t["start"], type="primary", use_container_width=True):
                st.session_state.goth_active = goth_toggle
                st.session_state.modalita_attiva = modalita
                st.session_state.archetipo_scelto = names[1]
                
                # Generazione Prompt
                prompt_init = f"Sei {names[1]}. {ARCH_DESC[names[1]]}. Partner: {sesso_p}. Utente: {sesso_u} ({eta_u} anni). Modalità: {modalita}."
                if goth_toggle: prompt_init += " [MODALITÀ GOTICA ATTIVA]"
                
                chat = model.start_chat(history=[])
                res = chat.send_message(prompt_init)
                st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                st.session_state.gemini_history = chat.history
                st.rerun()
        else:
            st.warning("⚠️ Immagini non trovate in assets/. Verifica che siano .png e che i nomi siano corretti.")
            # Debug per te
            if st.checkbox("Mostra Debug Percorsi"):
                st.write(f"Cerco in: assets/{cartella}/")
                st.write(f"File corrente: {names[1]}.png")

    else:
        # AREA CHAT
        st.subheader(f"Partita contro: {st.session_state.archetipo_scelto}")
        if st.button("⬅️ Esci"):
            st.session_state.ui_messages = []
            st.session_state.goth_active = False
            st.rerun()
            
        for m in st.session_state.ui_messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
            
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
    c_input = st.text_area("Incolla qui la tua chat...")
    if st.button("Analizza Frame"):
        res = model.generate_content(f"Analizza il frame di questa chat e offri 9 scambi da maestro: {c_input}")
        st.info(res.text)

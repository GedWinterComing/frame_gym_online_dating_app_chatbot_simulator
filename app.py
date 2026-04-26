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
        "analyze_btn": "🫂 Termina e Chiedi Analisi Psicologica",
        "coach_title": "🕵️‍♂️ Analizzatore di Frame (Agentic Mode)" # <-- ECCO IL FIX!
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

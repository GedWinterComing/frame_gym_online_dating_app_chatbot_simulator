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

# --- 1. CONFIGURAZIONE MOTORE ---
@st.cache_resource(show_spinner="Inizializzazione Motore AI...")
def get_best_model(api_key):
    if not api_key: return None, None
    genai.configure(api_key=api_key)
    try:
        modelli_validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not modelli_validi: return None, None
        model_name = next((m for m in modelli_validi if 'flash' in m.lower()), modelli_validi[0])
        return genai.GenerativeModel(model_name), model_name
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
    "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida la conversazione senza arroganza. Non si giustifica mai.",
    "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica o filosofia, disinnescando ogni provocazione.",
    "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé, facendo domande intriganti.",
    "The Chad": "🗿 Basso sforzo, altissima confidenza. Risposte brevi, dà l'attrazione per scontata.",
    "The Average Joe": "📱 L'utente standard. Usa emoji, cerca un terreno comune e mostra interesse convenzionale.",
    "The Redpill": "💊 Cinico e iper-razionale. Tratta il dating come un mercato darwiniano.",
    "The Data-Driven Geek": "📊 Analizza il flirt tramite dati. Metà contabile impazzito, metà nerd da D&D.",
    "The Conspiracy Theorist": "👽 Paranoico. Sospetta che il match sia un bot governativo o un rettiliano.",
    "The Pirate": "🏴‍☠️ Arrr! Parla come un bucaniere del 1700 alla ricerca di un tesoro.",
    "The Golden Retriever": "🐶 Energia felice. Eccessivamente entusiasta, 'zerbino' totale."
}

# --- 4. SETUP PAGINA E CSS DINAMICO ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

if "goth_active" not in st.session_state: st.session_state.goth_active = False
if "archetipo_scelto" not in st.session_state: st.session_state.archetipo_scelto = None
if "sesso_partner" not in st.session_state: st.session_state.sesso_partner = "Ragazza" # Default

# CSS PER GOTH MODE E CAROSELLO TEKKEN
st.markdown("""
    <style>
    /* CSS GOTH (Si attiva solo se necessario) */
    .goth-mode [data-testid="stAppViewContainer"] { background-color: #0a0a0a !important; color: #e0e0e0 !important; }
    .goth-mode [data-testid="stHeader"] { background-color: #0a0a0a !important; }
    .goth-mode [data-testid="stChatMessage"] { background-color: #121212 !important; border-left: 3px solid #8b0000 !important; }
    .goth-mode [data-testid="stChatInput"] textarea { background-color: #1c1c1c !important; color: #ffffff !important; font-size: 18px !important; font-weight: 600 !important; caret-color: #ff4b4b !important; }
    
    /* CSS CAROSELLO STILE VIDEOGIOCO */
    .roster-container { display: flex; overflow-x: auto; gap: 15px; padding: 20px 0px; scrollbar-width: thin; scrollbar-color: #8b0000 #1a1a1a; }
    .character-card { position: relative; flex: 0 0 auto; width: 140px; height: 140px; border-radius: 50%; background-size: cover; background-position: center; box-shadow: inset 0 0 20px #000000, 0 0 15px rgba(0,0,0,0.8); transition: transform 0.3s ease, border 0.3s ease; cursor: pointer; border: 2px solid #555; mask-image: radial-gradient(circle, black 50%, rgba(0,0,0,0.2) 90%, transparent 100%); -webkit-mask-image: -webkit-radial-gradient(circle, black 50%, rgba(0,0,0,0.2) 90%, transparent 100%); }
    .character-card:hover { transform: scale(1.15); border: 2px solid #ff4b4b; z-index: 10; }
    .card-title { font-size: 12px; margin-top: 8px; text-align: center; color: gray; font-weight: bold;}
    .selected-card { border: 3px solid #00ff00 !important; transform: scale(1.10); box-shadow: 0 0 20px rgba(0, 255, 0, 0.5); }
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
            st.session_state.sesso_partner = st.selectbox("Sesso del Partner (Archetipo)", [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"], value=False)
            
        # --- IL SELETTORE TEKKEN ---
        st.markdown("### Seleziona il tuo Combattente")
        cartella = "femmine" if st.session_state.sesso_partner == t["girl"] else "maschi"
        
        st.markdown('<div class="roster-container">', unsafe_allow_html=True)
        cols = st.columns(len(ARCH_NAMES))
        
        for i, arch in enumerate(ARCH_NAMES):
            with cols[i]:
                # Cerca l'immagine .png locale
                b64_img = get_base64_image(f"assets/{cartella}/{arch}.png")
                
                if b64_img:
                    # Se clicchi il bottone, salva la selezione
                    if st.button("Scegli", key=f"btn_{arch}"):
                        st.session_state.archetipo_scelto = arch
                    
                    # Highlight se selezionato
                    border_class = "selected-card" if st.session_state.archetipo_scelto == arch else ""
                    
                    html = f'''
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="character-card {border_class}" style="background-image: url('data:image/png;base64,{b64_img}');"></div>
                        <p class="card-title">{arch}</p>
                    </div>
                    '''
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.warning(f"Manca: {arch}.png")
        st.markdown('</div>', unsafe_allow_html=True)

        # Mostra la descrizione se hai selezionato qualcuno
        if st.session_state.archetipo_scelto:
            st.info(f"**Hai selezionato {st.session_state.archetipo_scelto}:** {ARCH_DESC[st.session_state.archetipo_scelto]}")
            
            if st.button(t["start"], use_container_width=True, type="primary"):
                st.session_state.goth_active = goth_toggle 
                st.session_state.modalita_attiva = modalita
                
                if modalita == t["mode_gym"]:
                    full_prompt = f"L'utente si allena come {st.session_state.archetipo_scelto}. Tu sei il partner ({st.session_state.sesso_partner}) e fai molta resistenza."
                    if dinamica == t["desired"]: full_prompt += "\n[DINAMICA]: L'utente è il Desiderato. Tu devi sedurlo. Inizia tu."
                else:
                    full_prompt = f"Da questo momento TU sei l'archetipo: '{st.session_state.archetipo_scelto}'. Descrizione: {ARCH_DESC[st.session_state.archetipo_scelto]}. Inizia tu a sedurre l'utente."
                
                if goth_toggle: full_prompt += "\n[MODALITÀ GOTICA ATTIVA]"

                chat = model.start_chat(history=[])
                response = chat.send_message(full_prompt)
                st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
                st.session_state.gemini_history = chat.history
                st.rerun()
        else:
            st.warning("☝️ Seleziona un archetipo dal carosello per poter avviare la partita!")

    else:
        # SCHERMATA CHAT
        st.subheader(f"{'🍷 Esperienza' if st.session_state.modalita_attiva == t['mode_exp'] else '⚖️ Frame-Gym'}: {st.session_state.archetipo_scelto}")
        if st.button(t["back_btn"]):
            st.session_state.clear()
            st.rerun()

        for msg in st.session_state.ui_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Scrivi..."):
            st.session_state.ui_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                chat = model.start_chat(history=st.session_state.gemini_history)
                response = chat.send_message(prompt)
                st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
                st.session_state.gemini_history = chat.history
                st.rerun()

with tab_coach:
    st.write("Area in manutenzione per i prossimi aggiornamenti!")

import streamlit as st
import google.generativeai as genai
import os
import random
from dotenv import load_dotenv

# Caricamento variabili
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- 1. CONFIGURAZIONE MOTORE (ZERO CONSUMO ALL'AVVIO) ---
@st.cache_resource(show_spinner="Inizializzazione Motore AI...")
def get_best_model(api_key):
    if not api_key:
        return None, None
    genai.configure(api_key=api_key)
    # Niente test a vuoto, usiamo direttamente il modello stabile
    model_name = 'gemini-1.5-flash'
    try:
        m = genai.GenerativeModel(model_name)
        return m, model_name
    except Exception:
        return None, None

# --- 2. DIZIONARIO LINGUE ---
UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox",
        "tab_sim": "🎮 Simulatore",
        "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:",
        "lang": "🌐 Lingua",
        "sex_u": "👤 Il tuo sesso",
        "sex_p": "❤️ Cerchi un/una",
        "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza",
        "arch": "🎭 Tuo Archetipo",
        "goth": "🦇 Gothificatore",
        "dyn": "🎯 Dinamica",
        "pursuer": "Corteggiatore (Tu seduci)",
        "desired": "Desiderato (L'IA seduce te)",
        "start": "🚀 INIZIA PARTITA",
        "mood_title": "⚙️ Modifica Umore Partner",
        "back_btn": "⬅️ Termina e Resetta",
        "coach_title": "🕵️‍♂️ Analizzatore di Frame",
        "coach_desc": "Incolla una chat vera per analizzare chi ha il potere.",
        "coach_btn": "🔍 Analizza Chat"
    },
    "English": {
        "title": "⚖️ Social Dynamics Sandbox",
        "tab_sim": "🎮 Simulator",
        "tab_coach": "🧠 Coach Room",
        "setup": "Configure your session:",
        "lang": "🌐 Language",
        "sex_u": "👤 Your gender",
        "sex_p": "❤️ Looking for",
        "age": "🎂 Your Age",
        "boy": "Boy", "girl": "Girl",
        "arch": "🎭 Your Archetype",
        "goth": "🦇 Gothifier",
        "dyn": "🎯 Dynamics",
        "pursuer": "Pursuer (You seduce)",
        "desired": "Desired (AI seduces you)",
        "start": "🚀 START SESSION",
        "mood_title": "⚙️ Adjust Partner's Mood",
        "back_btn": "⬅️ End & Reset",
        "coach_title": "🕵️‍♂️ Frame Analyzer",
        "coach_desc": "Paste a real chat to see who holds the power.",
        "coach_btn": "🔍 Analyze Chat"
    },
    "日本語": { "title": "⚖️ 練習用サンドボックス", "tab_sim": "🎮 シミュレーター", "tab_coach": "🧠 コーチルーム", "setup": "設定:", "lang": "🌐 言語", "sex_u": "👤 性別", "sex_p": "❤️ 相手", "age": "🎂 年齢", "boy": "男性", "girl": "女性", "arch": "🎭 タイプ", "goth": "🦇 ゴス", "dyn": "🎯 ダイナミクス", "pursuer": "追う側", "desired": "追われる側", "start": "🚀 開始", "mood_title": "⚙️ 気分調整", "back_btn": "⬅️ 戻る", "coach_title": "🕵️‍♂️ 分析", "coach_desc": "チャットを貼り付けて分析します。", "coach_btn": "🔍 分析する" },
    "中文": { "title": "⚖️ 社交动态模拟器", "tab_sim": "🎮 模拟器", "tab_coach": "🧠 教练室", "setup": "配置:", "lang": "🌐 语言", "sex_u": "👤 你的性别", "sex_p": "❤️ 寻找", "age": "🎂 年龄", "boy": "男生", "girl": "女生", "arch": "🎭 原型", "goth": "🦇 哥特", "dyn": "🎯 互动", "pursuer": "主动", "desired": "被动", "start": "🚀 开始", "mood_title": "⚙️ 调整情绪", "back_btn": "⬅️ 返回", "coach_title": "🕵️‍♂️ 分析器", "coach_desc": "粘贴聊天记录进行分析。", "coach_btn": "🔍 开始分析" }
}

ARCH_DESC = {
    "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida la conversazione senza arroganza. Non si giustifica mai.",
    "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica o filosofia, disinnescando ogni provocazione.",
    "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé, facendo domande intriganti.",
    "The Chad": "🗿 Basso sforzo, altissima confidenza. Risposte brevi, dà l'attrazione per scontata.",
    "The Average Joe": "📱 L'utente standard. Usa emoji, cerca un terreno comune e mostra interesse convenzionale.",
    "The Redpill": "💊 Cinico e iper-razionale. Tratta il dating come un mercato darwiniano.",
    "The Data-Driven Geek": "📊 Analizza il flirt tramite dati o lore tecnica. Metà contabile, metà nerd.",
    "The Conspiracy Theorist": "👽 Paranoico. Sospetta che il match sia un bot governativo o un rettiliano.",
    "The Pirate": "🏴‍☠️ Arrr! Parla come un bucaniere del 1700 alla ricerca di un tesoro.",
    "The Golden Retriever": "🐶 Energia felice. Eccessivamente entusiasta, 'zerbino' totale."
}

# --- 3. SETUP PAGINA E CSS DINAMICO ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

# Iniezione CSS Oscuro se il Gothificatore è attivo
if "goth_mode" not in st.session_state:
    st.session_state.goth_mode = False

if st.session_state.goth_mode:
    st.markdown("""
        <style>
        /* Sfondo e testo generale */
        [data-testid="stAppViewContainer"] {
            background-color: #0a0a0a !important;
            color: #e0e0e0 !important;
        }
        [data-testid="stHeader"] { background-color: #0a0a0a !important; }
        
        /* Modifica colori scritte e titoli */
        h1, h2, h3, p, span, div { color: #e0e0e0 !important; }
        
        /* I box informativi diventano viola/rossi molto scuri */
        div[data-testid="stMenu"] { background-color: #1a001a !important; }
        
        /* Le chat dell'AI */
        [data-testid="stChatMessage"] {
            background-color: #121212 !important;
            border-left: 3px solid #8b0000 !important; /* Rosso Sangue */
        }
        /* Casella di input */
        [data-testid="stChatInput"] textarea {
            background-color: #1c1c1c !important;
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

model, active_model_name = get_best_model(api_key)
if not model:
    st.error("🚨 API Key mancante o Server Gemini offline. Controlla i Secrets.")
    st.stop()

lang_choice = st.selectbox("🌐 Seleziona Lingua", list(UI.keys()), index=0)
t = UI[lang_choice]

tab_sim, tab_coach = st.tabs([t["tab_sim"], t["tab_coach"]])

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
    st.session_state.gemini_history = []
    st.session_state.is_easter_egg = False

# ==========================================
# SCHEDA 1: SIMULATORE
# ==========================================
with tab_sim:
    if not st.session_state.ui_messages:
        st.title(t["title"])
        st.write(t["setup"])
        col1, col2 = st.columns(2)
        with col1:
            sesso_u = st.selectbox(t["sex_u"], [t["boy"], t["girl"]])
            eta_u = st.slider(t["age"], 18, 40, 33)
            dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
        with col2:
            archetipo_scelto = st.selectbox(t["arch"], list(ARCH_DESC.keys()), index=0)
            st.info(ARCH_DESC[archetipo_scelto])
            sesso_p = st.selectbox(t["sex_p"], [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"], value=False)
        
        if st.button(t["start"], use_container_width=True, type="primary"):
            st.session_state.archetipo_scelto = archetipo_scelto
            st.session_state.goth_mode = goth_toggle # SALVA IL MOOD GOTICO
            st.session_state.strana, st.session_state.banale, st.session_state.entusiasta = 5, 25, 10
            
            # Logica Easter Egg
            easter_egg_triggered = False
            if sesso_u == t["girl"] and sesso_p == t["boy"] and dinamica == t["desired"]:
                prob = 0.034 * (1.992 if goth_toggle else 1)
                if random.random() < prob:
                    easter_egg_triggered = True
                    st.session_state.is_easter_egg = True
            
            if easter_egg_triggered:
                full_prompt = st.secrets.get("GABRI_LORE", "Lore non trovata.") + "\nFORMATO: [MOOD]: ... [MESSAGGIO]: ..."
            else:
                try:
                    with open("prompt.txt", "r", encoding="utf-8") as f:
                        template = f.read()
                    full_prompt = template.format(lingua=lang_choice, sesso_utente=sesso_u, archetipo=archetipo_scelto, sesso_partner=sesso_p)
                except FileNotFoundError:
                    st.error("Manca il file prompt.txt")
                    st.stop()
                
                # INIEZIONE GOTICA REALE
                if goth_toggle:
                    full_prompt += """
                    \n[MODALITÀ GOTICA ATTIVA]:
                    Il partner che devi simulare appartiene alla subcultura Goth.
                    - PROBABILITÀ PROFILO: Genera con il 70% di probabilità un Classic/Trad Goth. Altrimenti, scegli uno tra questi: Victorian/Romantic Goth, Industrial Goth, Cyber Goth, Gothabilly, Lolita Goth, Nu-Goth.
                    - ESTETICA TESTUALE: Usa occasionalmente la formattazione HTML per colorare singole parole chiave nel messaggio (es. <span style='color:magenta'>parola</span>), scegliendo tra i colori tipici dei capelli alternativi: magenta, cyan, limegreen o darkred. Usa molto il *corsivo* per dare un tono drammatico.
                    """

                if dinamica == t["desired"]:
                    full_prompt += "\n[DINAMICA]: L'utente è il Desiderato. Tu (IA) devi sedurlo. Inizia tu la chat."
                else:
                    full_prompt += "\n[DINAMICA]: L'utente è il Corteggiatore. Tu (IA) sei diffidente."

            chat = model.start_chat(history=[])
            response = chat.send_message(full_prompt)
            st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
            st.session_state.gemini_history = chat.history
            st.rerun()

    else:
        # Chat Attiva
        titolo_c = "🦇 Goth Mode: ON" if st.session_state.goth_mode else f"⚖️ Frame-Gym: {st.session_state.archetipo_scelto}"
        if st.session_state.is_easter_egg: titolo_c = "⚖️ Easter Egg: Gabri Found!"
        
        st.subheader(titolo_c)
        
        if st.button(t["back_btn"]):
            st.session_state.clear()
            st.rerun()

        for msg in st.session_state.ui_messages:
            with st.chat_message(msg["role"]):
                if "[MOOD]:" in msg["content"]:
                    parti = msg["content"].split("[MESSAGGIO]:")
                    st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                    # L'uso di unsafe_allow_html=True qui permette alle scritte colorate di funzionare!
                    st.markdown(f"📱 **{parti[1].strip()}**", unsafe_allow_html=True)
                else: st.markdown(msg["content"], unsafe_allow_html=True)

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
# SCHEDA 2: COACH ROOM
# ==========================================
with tab_coach:
    st.title(t["coach_title"])
    st.write(t["coach_desc"])
    chat_input = st.text_area("Chat:", height=250, placeholder="Io: ...\nLei: ...")
    if st.button(t["coach_btn"], type="primary"):
        if chat_input:
            with st.spinner("Analisi in corso..."):
                res = model.generate_content(f"Analizza il frame di questa chat in modo spietato e clinico e fornisci un esempio di come l'utente avrebbe dovuto rispondere per mantenere il frame e poi scrivi una Chat da Maestro ovvero prosegui la simulazione per 9 botta e risposta ideali mostrando come un vero maestro avrebbe gestito e ribaltato la situazione:\n{chat_input}")
                st.markdown(res.text)
# --- 1. FALLBACK MODELLI (ROULETTE CASUALE) ---
# @st.cache_resource(show_spinner="Ricerca di un server Gemini disponibile...")
# def get_best_model(api_key):
#     if not api_key:
#         return None, None
#     genai.configure(api_key=api_key)
#     # Lista modelli per la roulette
#     models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
#     random.shuffle(models)
    
#     for model_name in models:
#         try:
#             m = genai.GenerativeModel(model_name)
#             # Test rapido per verificare la quota
#             m.generate_content("ping") 
#             return m, model_name
#         except Exception:
#             continue
#     return None, None

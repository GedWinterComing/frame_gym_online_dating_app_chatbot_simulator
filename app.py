import streamlit as st
import google.generativeai as genai
import os
import random
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- 1. FALLBACK MODELLI ---
@st.cache_resource(show_spinner="Connessione ai server Google...")
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
    for model_name in models:
        try:
            m = genai.GenerativeModel(model_name)
            m.generate_content("test")
            return m, model_name
        except Exception:
            continue
    return None, None

# --- 2. DIZIONARIO LINGUE ---
UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox",
        "setup": "Configura la tua partita:",
        "lang": "🌐 Lingua / Language",
        "sex_u": "👤 Il tuo sesso",
        "sex_p": "❤️ Cerchi un/una",
        "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza",
        "arch": "🎭 Tuo Archetipo",
        "goth": "🦇 Gothificatore (Beta)",
        "dyn": "🎯 Dinamica Relazionale",
        "hunter": "Corteggiatore (Tu devi sedurre)",
        "prey": "Desiderato (L'IA deve sedurti)",
        "start": "🚀 GENERA PROFILO E INIZIA",
        "mood_title": "⚙️ Modifica Umore Partner in tempo reale",
        "back_btn": "⬅️ Torna al Menu Principale"
    },
    "English": {
        "title": "⚖️ Social Dynamics Sandbox",
        "setup": "Configure your session:",
        "lang": "🌐 Lingua / Language",
        "sex_u": "👤 Your gender",
        "sex_p": "❤️ Looking for",
        "age": "🎂 Your Age",
        "boy": "Boy", "girl": "Girl",
        "arch": "🎭 Your Archetype",
        "goth": "🦇 Gothifier (Beta)",
        "dyn": "🎯 Dynamics",
        "hunter": "Pursuer (You must seduce)",
        "prey": "Desired (AI must seduce you)",
        "start": "🚀 GENERATE PROFILE & START",
        "mood_title": "⚙️ Adjust Partner's Mood in real-time",
        "back_btn": "⬅️ Back to Main Menu"
    }
}

# --- 3. INIZIALIZZAZIONE ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

model, active_model_name = get_best_model(api_key)
if not model:
    st.error("🚨 Modelli Gemini offline. Riprova tra poco.")
    st.stop()

# --- 4. SELETTORE LINGUA GLOBALE ---
lang = st.selectbox("🌐 Seleziona Lingua / Select Language", ["Italiano", "English"], index=0)
t = UI[lang]

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
    st.session_state.gemini_history = []
    st.session_state.is_easter_egg = False

# --- 5. SCHERMATA DI SETUP ---
if not st.session_state.ui_messages:
    st.title(t["title"])
    col1, col2 = st.columns(2)
    with col1:
        sesso_u = st.selectbox(t["sex_u"], [t["boy"], t["girl"]])
        eta_u = st.slider(t["age"], 18, 40, 33)
        dinamica = st.radio(t["dyn"], [t["hunter"], t["prey"]])
    with col2:
        archetipi = ["Gentle Dom", "The Stoic Sage", "The Detective", "The Chad", "The Average Joe", "The Redpill", "The Data-Driven Geek", "The Conspiracy Theorist", "The Pirate", "The Golden Retriever"]
        archetipo_scelto = st.selectbox(t["arch"], archetipi, index=0)
        sesso_p = st.selectbox(t["sex_p"], [t["girl"], t["boy"]])
        goth_mode = st.toggle(t["goth"], value=False)
    
    st.divider()

    if st.button(t["start"], use_container_width=True, type="primary"):
        st.session_state.archetipo_scelto = archetipo_scelto
        st.session_state.strana, st.session_state.banale, st.session_state.entusiasta = 5, 25, 10
        
        # LOGICA PROBABILITÀ EASTER EGG (GABRI)
        easter_egg_triggered = False
        if sesso_u == t["girl"] and sesso_p == t["boy"] and dinamica == t["prey"]:
            prob = 0.034
            if goth_mode: prob *= 1.992
            if random.random() < prob:
                easter_egg_triggered = True
                st.session_state.is_easter_egg = True
        
        if easter_egg_triggered:
            # --- PROMPT SEGRETO GABRI ---
            full_prompt = f"""
            Sei 'Gabri', 34 anni, capelli biondi, hai fatto il liceo classico, laureato in Fisica Applicata, Data Scientist a Bologna. Sei un Easter Egg. L'utente è una ragazza.
            LORE:
            - Hai l'ADHD: questo ti rende a volte iper-focalizzato, entusiasta e saltelli tra i discorsi.
            - Personalità: sei calmo, riflessivo, dolce, gentile, nerd, introverso, INFJ, ami chicchierate profonde a 2 a 2 piuttosto che gruppi di amici vasti, ti perdi nei discorsi generali sui massimi sistemi. Ti paice One Piece e i manga giapponesi, la musica celtica, porti capelli lunghi con un taglio mullet/moicano rasato ai lati, orecchini nel sx.
            - Ragazza ideale: capelli neri o mora o colorati (rosa o blu o verdi ecc), dolce, meglio se tatuata, gotica.
            - Musica: Suoni la chitarra elettrica. Adori Steve Vai, Joe Satriani, Iron Maiden, Pearl Jam, metal anni 80, musica rock.
            - Segreto ironico: Nonostante ami i virtuosi melodici, non hai MAI imparato un brano dall'inizio alla fine (tipico ADHD).
            - Altri tratti: Apparecchi acustici, mediti (sei Buddhista), sei Comunista/Socialista. 
            - Cani: Ami i cani ma non ne hai. In una foto compare Lara, cane di amici. Sogni Noam (Malamute femmina grigia e bianca) e Chomsky (Chow Chow maschio miele o nero).
            - Stile: Scrivi con MOLTA punteggiatura, specialmente virgole. NO abbreviazioni.
            - Sessualità: Dominante nel privato (BDSM e sesso spinto), fuori tranquillo. Etero. Gentle Dom.
            - Obiettivo: Seduci l'utente iniziando tu la chat.
            FORMATO: [MOOD]: ... [MESSAGGIO]: ...
            """
        else:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                template = f.read()
            full_prompt = template.format(lingua=lang, sesso_utente=sesso_u, archetipo=archetipo_scelto, sesso_partner=sesso_p)
            
            # --- INIEZIONE LOGICA DINAMICA ---
            if dinamica == t["prey"]:
                full_prompt += "\n[DINAMICA DI GIOCO]: L'utente è 'Il Desiderato'. Tu (il Partner) sei molto interessato/a a lui/lei. Cerca di sedurlo/a, fai tu il primo passo inviando il primo messaggio. Fai domande e cerca di tenerlo/a stretto/a."
            else:
                full_prompt += "\n[DINAMICA DI GIOCO]: L'utente è 'Il Corteggiatore'. Tu (il Partner) sei diffidente, selettivo/a e fai il/la difficile. Genera solo il profilo e aspetta che sia l'utente a scriverti."

        chat = model.start_chat(history=[])
        response = chat.send_message(full_prompt)
        st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
        st.session_state.gemini_history = chat.history
        st.rerun()

# --- 6. INTERFACCIA CHAT ---
else:
    titolo = "⚖️ Easter Egg: Gabri Found!" if st.session_state.is_easter_egg else f"⚖️ Frame-Gym: {st.session_state.archetipo_scelto}"
    st.title(titolo)
    
    # IL NUOVO TASTO INDIETRO (Sempre visibile in alto prima della chat)
    if st.button(t["back_btn"], type="secondary"):
        st.session_state.clear()
        st.rerun()
    
    with st.expander(t["mood_title"]):
        st.session_state.strana = st.slider("Imprevedibile (%)", 0, 100, st.session_state.strana)
        st.session_state.banale = st.slider("Fredda (%)", 0, 100 - st.session_state.strana, st.session_state.banale)
        st.session_state.entusiasta = st.slider("Entusiasta (%)", 0, 100 - (st.session_state.strana + st.session_state.banale), st.session_state.entusiasta)

    st.divider()

    for msg in st.session_state.ui_messages:
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if "[MOOD]:" in content and "[MESSAGGIO]:" in content:
                parti = content.split("[MESSAGGIO]:")
                st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                st.info(f"📱 **{parti[1].strip()}**")
            else: st.markdown(content)

    if prompt := st.chat_input("Scrivi..."):
        st.session_state.ui_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            chat = model.start_chat(history=st.session_state.gemini_history)
            try:
                response = chat.send_message(prompt)
                res_text = response.text
                if "[MOOD]:" in res_text and "[MESSAGGIO]:" in res_text:
                    parti = res_text.split("[MESSAGGIO]:")
                    st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                    st.info(f"📱 **{parti[1].strip()}**")
                else: st.markdown(res_text)
                st.session_state.ui_messages.append({"role": "assistant", "content": res_text})
                st.session_state.gemini_history = chat.history
            except Exception as e: st.error(f"Errore: {e}")

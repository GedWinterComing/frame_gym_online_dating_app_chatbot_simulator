import streamlit as st
import google.generativeai as genai
import os
import random
import pandas as pd
import altair as alt
from dotenv import load_dotenv

# --- 1. CARICAMENTO ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    with open("prompt.txt", "r", encoding="utf-8") as file:
        base_prompt = file.read()
except FileNotFoundError:
    st.error("Errore: Manca 'prompt.txt'.")
    st.stop()

# --- 2. CONFIGURAZIONE SIDEBAR ---
st.set_page_config(page_title="Frame-Gym", page_icon="⚖️", layout="wide")
st.sidebar.title("⚙️ Setup Sessione")

goth_mode = st.sidebar.toggle("🦇 Gothificatore (Beta)", value=False)

st.sidebar.divider()
st.sidebar.subheader("📊 Probabilità Umore")
strana = st.sidebar.slider("Strana (%)", 0, 100, 5)
banale = st.sidebar.slider("Banale (%)", 0, 100 - strana, 25)
entusiasta = st.sidebar.slider("Entusiasta (%)", 0, 100 - (strana + banale), 10)
normale = 100 - (strana + banale + entusiasta)

# Grafico umore
df_umore = pd.DataFrame({
    'Umore': ['Strana', 'Banale', 'Entusiasta', 'Normale'],
    'Percentuale': [strana, banale, entusiasta, normale]
})
grafico = alt.Chart(df_umore).mark_arc(innerRadius=40).encode(
    theta="Percentuale", color="Umore"
).properties(height=200)
st.sidebar.altair_chart(grafico, use_container_width=True)

# --- 3. LOGICA IA ---
if not api_key:
    st.error("Chiave API mancante nei Secrets/Env.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Uso 1.5 per stabilità quota

def get_mood_instruction():
    roll = random.randint(1, 100)
    if roll <= strana: return "\n\n[MOOD SYSTEM: Sii molto strana/distratta]"
    if roll <= strana + banale: return "\n\n[MOOD SYSTEM: Sii banale/fredda, rispondi a monosillabi]"
    if roll <= strana + banale + entusiasta: return "\n\n[MOOD SYSTEM: Sii molto entusiasta]"
    return ""

# --- 4. STATO DELLA SESSIONE E AVVIO ---
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
    st.session_state.gemini_history = []

# SCHERMATA DI INIZIO
if not st.session_state.ui_messages:
    st.title("⚖️ Benvenuto nel Frame-Gym")
    st.write("Configura i parametri nella barra laterale e premi il tasto sotto per generare il tuo obiettivo.")
    
    if st.button("🚀 GENERA PROFILO E INIZIA", use_container_width=True):
        first_prompt = base_prompt + "\nGenera ora il profilo della ragazza."
        if goth_mode:
            first_prompt += " REQUISITO: Deve essere una ragazza GOTH/ALT."
        
        chat = model.start_chat(history=[])
        response = chat.send_message(first_prompt)
        st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
        st.session_state.gemini_history = chat.history
        st.rerun()

# SE IL GIOCO È IN CORSO
else:
    st.title("⚖️ Chat in corso...")
    
    # Mostra messaggi
    for msg in st.session_state.ui_messages:
        with st.chat_message(msg["role"]):
            # Logica colori per MOOD e MESSAGGIO
            contesto = msg["content"]
            if "[MOOD]:" in contesto and "[MESSAGGIO]:" in contesto:
                parti = contesto.split("[MESSAGGIO]:")
                st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                st.info(f"📱 **{parti[1].strip()}**")
            else:
                st.markdown(contesto)

    # Input Utente
    if prompt := st.chat_input("Scrivi..."):
        st.session_state.ui_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            instruction = get_mood_instruction()
            chat = model.start_chat(history=st.session_state.gemini_history)
            response = chat.send_message(prompt + instruction)
            
            # Visualizzazione divisa
            testo = response.text
            if "[MOOD]:" in testo and "[MESSAGGIO]:" in testo:
                parti = testo.split("[MESSAGGIO]:")
                st.markdown(f"*{parti[0].replace('[MOOD]:','').strip()}*")
                st.info(f"📱 **{parti[1].strip()}**")
            else:
                st.markdown(testo)
            
            st.session_state.ui_messages.append({"role": "assistant", "content": testo})
            st.session_state.gemini_history = chat.history

# Reset sempre disponibile
if st.sidebar.button("🔄 Reset / Nuova Ragazza", use_container_width=True):
    st.session_state.clear()
    st.rerun()

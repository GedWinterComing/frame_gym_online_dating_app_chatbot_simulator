import streamlit as st
import google.generativeai as genai
import os
import random
import pandas as pd
import altair as alt
from dotenv import load_dotenv

# --- 1. CARICAMENTO VARIABILI SICURE E PROMPT ---
# Carica la chiave API dal file .env nascoso
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Carica le regole dell'arbitro dal file di testo
try:
    with open("prompt.txt", "r", encoding="utf-8") as file:
        base_prompt = file.read()
except FileNotFoundError:
    st.error("Errore: Il file 'prompt.txt' non è stato trovato nella cartella.")
    st.stop()

# --- 2. CONFIGURAZIONE PAGINA E SIDEBAR ---
st.set_page_config(page_title="Frame-Gym: Dating Simulator", page_icon="⚖️", layout="wide")

st.sidebar.title("⚙️ Parametri Simulazione")

# Il Gothificatore (Toggle)
goth_mode = st.sidebar.toggle("🦇 Attiva Gothificatore (Beta)", value=False, help="Forza l'algoritmo a generare profili alt-girl/goth/metal.")

st.sidebar.divider()

# Regolazione Stocastica dell'Umore (Slider dinamici che fanno sempre 100)
st.sidebar.subheader("📊 Distribuzione Umore")
st.sidebar.caption("Regola le % di reazione della ragazza per ogni tuo messaggio. Il resto sarà 'Normale'.")

# Slider dinamici: il massimo si adatta per non superare 100
strana = st.sidebar.slider("Strana / Inusuale (%)", 0, 100, 5)
banale = st.sidebar.slider("Banale / Fredda (%)", 0, 100 - strana, 25)
entusiasta = st.sidebar.slider("Entusiasta (%)", 0, 100 - (strana + banale), 10)
normale = 100 - (strana + banale + entusiasta)

st.sidebar.write(f"**Normale (Calcolato): {normale}%**")

# Creazione Grafico a Torta (Altair)
df_umore = pd.DataFrame({
    'Umore': ['Strana', 'Banale', 'Entusiasta', 'Normale'],
    'Percentuale': [strana, banale, entusiasta, normale]
})

grafico_torta = alt.Chart(df_umore).mark_arc(innerRadius=40).encode(
    theta=alt.Theta(field="Percentuale", type="quantitative"),
    color=alt.Color(field="Umore", type="nominal", 
                    scale=alt.Scale(domain=['Strana', 'Banale', 'Entusiasta', 'Normale'], 
                                    range=['#9b59b6', '#34495e', '#e74c3c', '#2ecc71'])),
    tooltip=['Umore', 'Percentuale']
).properties(height=250)

st.sidebar.altair_chart(grafico_torta, use_container_width=True)

# --- 3. INIZIALIZZAZIONE IA E LOGICA ---
if not api_key:
    st.error("⚠️ Chiave API non trovata! Assicurati di aver creato il file .env correttamente.")
    st.stop()

genai.configure(api_key=api_key)
# Usiamo il modello più aggiornato
model = genai.GenerativeModel('gemini-2.5-flash')

# Funzione per tirare i dadi dell'umore
def get_mood_instruction():
    roll = random.randint(1, 100)
    if roll <= strana:
        return "\n\n[COMANDO DI SISTEMA INVISIBILE: Per questa singola risposta, ignora il tuo carattere base e comportati in modo molto strano, inusuale o visibilmente distratta.]"
    elif roll <= strana + banale:
        return "\n\n[COMANDO DI SISTEMA INVISIBILE: Per questa singola risposta, comportati in modo estremamente banale, annoiata e rispondi a monosillabi o frasi fatte.]"
    elif roll <= strana + banale + entusiasta:
        return "\n\n[COMANDO DI SISTEMA INVISIBILE: Per questa singola risposta, comportati in modo esageratamente entusiasta, interessata e usa molte emoji.]"
    else:
        return "" # Comportamento normale, nessuna forzatura

# Memoria separata: una per la UI (pulita) e una per Gemini (con i comandi segreti)
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
    st.session_state.gemini_history = []
    
    # Preparazione del primo prompt
    first_prompt = base_prompt + "\nInizia ora. Genera il profilo della ragazza."
    if goth_mode:
        first_prompt += " ATTENZIONE: La ragazza generata DEVE assolutamente avere un look e interessi legati alla subcultura Goth, Dark, Metal o Fetish. (es. vestiti in pelle, ascolta Black Sabbath o Cure, ecc)."
    
    # Avvio chat
    chat = model.start_chat(history=[])
    try:
        response = chat.send_message(first_prompt)
        st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
        st.session_state.gemini_history = chat.history
    except Exception as e:
        st.error(f"Errore di generazione iniziale: {e}")

# --- 4. INTERFACCIA CHAT PRINCIPALE ---
st.title("⚖️ Frame-Gym: Sandbox di Addestramento")
if goth_mode:
    st.caption("🦇 Modalità Gothificatore ATTIVA")

# Mostra i messaggi puliti all'utente
for message in st.session_state.ui_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. GESTIONE INPUT E RISPOSTA STOCASTICA ---
if prompt := st.chat_input("Fai la tua mossa (Gentle Dom)..."):
    # Mostra l'input utente a schermo (pulito)
    st.session_state.ui_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Calcola il comando segreto basato sui dadi
        secret_instruction = get_mood_instruction()
        hidden_prompt = prompt + secret_instruction
        
        # Inizializza la chat con la cronologia sporca
        chat = model.start_chat(history=st.session_state.gemini_history)
        
        try:
            # Inviamo al modello la frase dell'utente + il comando segreto
            response = chat.send_message(hidden_prompt)
            testo_ia = response.text
            
            # Controlla se l'IA ha usato il formato diviso
            if "[MOOD]:" in testo_ia and "[MESSAGGIO]:" in testo_ia:
                parti = testo_ia.split("[MESSAGGIO]:")
                mood_text = parti[0].replace("[MOOD]:", "").strip()
                messaggio_text = parti[1].strip()
                
                # Stampa il MOOD in grigetto, corsivo e piccolo
                st.markdown(f"*{mood_text}*")
                # Stampa il messaggio reale di Tinder in modo normale o in un box
                st.info(f"📱 **{messaggio_text}**")
            else:
                # Se è un Game Over o l'Inizializzazione, stampa normale
                st.markdown(testo_ia)
            
            # Salviamo la risposta pulita per la UI
            st.session_state.ui_messages.append({"role": "assistant", "content": testo_ia})
            
            # Salviamo la risposta pulita per la UI
            st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
            # Aggiorniamo la memoria di Gemini
            st.session_state.gemini_history = chat.history
        except Exception as e:
            st.error(f"Errore API: {e}")

# Tasto per azzerare la chat (Sidebar)
if st.sidebar.button("🔄 Nuova Partita", use_container_width=True):
    st.session_state.clear()
    st.rerun()
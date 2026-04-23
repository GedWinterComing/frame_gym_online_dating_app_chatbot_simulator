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
        "pursuer": "Corteggiatore (Tu devi sedurre)",
        "desired": "Desiderato (L'IA deve sedurti)",
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
        "pursuer": "Pursuer (You must seduce)",
        "desired": "Desired (AI must seduce you)",
        "start": "🚀 GENERATE PROFILE & START",
        "mood_title": "⚙️ Adjust Partner's Mood in real-time",
        "back_btn": "⬅️ Back to Main Menu"
    },
    "日本語": {
        "title": "⚖️ ソーシャル・ダイナミクス・サンドボックス",
        "setup": "セッション設定:",
        "lang": "🌐 言語 / Language",
        "sex_u": "👤 あなたの性別",
        "sex_p": "❤️ 相手の性別",
        "age": "🎂 年齢",
        "boy": "男性", "girl": "女性",
        "arch": "🎭 アーキタイプ",
        "goth": "🦇 ゴスモード (Beta)",
        "dyn": "🎯 ダイナミクス",
        "pursuer": "アプローチ側 (あなたが誘う)",
        "desired": "ターゲット (相手が誘う)",
        "start": "🚀 プロフィール生成＆開始",
        "mood_title": "⚙️ パートナーの気分を調整",
        "back_btn": "⬅️ メインメニューに戻る"
    },
    "中文": {
        "title": "⚖️ 社交动态模拟器",
        "setup": "配置你的会话:",
        "lang": "🌐 语言 / Language",
        "sex_u": "👤 你的性别",
        "sex_p": "❤️ 寻找",
        "age": "🎂 你的年龄",
        "boy": "男生", "girl": "女生",
        "arch": "🎭 你的原型",
        "goth": "🦇 哥特模式 (Beta)",
        "dyn": "🎯 互动模式",
        "pursuer": "主动 (你来撩)",
        "desired": "被动 (对方来撩)",
        "start": "🚀 生成资料并開始",
        "mood_title": "⚙️ 实时调整对方情绪",
        "back_btn": "⬅️ 返回主菜单"
    }
}

# --- 3. DESCRIZIONI ARCHETIPI ---
ARCH_DESC = {
    "Italiano": {
        "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida la conversazione senza arroganza. Non si giustifica mai, prende l'iniziativa e mantiene il controllo emotivo.",
        "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica o filosofia, disinnescando ogni provocazione con un silenzio distaccato.",
        "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé, facendo domande psicologiche e intriganti per 'sezionare' l'altro.",
        "The Chad": "🗿 Basso sforzo, altissima confidenza. Risposte brevi, nessuna giustificazione, dà l'attrazione per scontata.",
        "The Average Joe": "📱 L'utente standard. Usa emoji, cerca un terreno comune e mostra interesse in modo convenzionale.",
        "The Redpill": "💊 Cinico e iper-razionale. Tratta il dating come un mercato darwiniano. Sempre sulla difensiva.",
        "The Data-Driven Geek": "📊 Analizza il flirt tramite dati o lore tecnica. Oscilla tra la freddezza di un bilancio e l'ossessione nerd.",
        "The Conspiracy Theorist": "👽 Paranoico. Sospetta che il match sia un bot governativo o un rettiliano.",
        "The Pirate": "🏴‍☠️ Arrr! Parla come un bucaniere del 1700 alla ricerca di un tesoro.",
        "The Golden Retriever": "🐶 Pura energia e felicità. Eccessivamente entusiasta, 'zerbino' totale, usa mille emoji."
    },
    "English": {
        "Gentle Dom": "👑 Calm, assertive, and protective. Leads without arrogance. Never justifies, takes initiative.",
        "The Stoic Sage": "🧘‍♂️ Unshakeable and reflective. Responds with logic or philosophy, neutralizing drama.",
        "The Detective": "🕵️‍♂️ Mysterious and analytical. Refuses to talk about self, uses intriguing questions.",
        "The Chad": "🗿 Low effort, high confidence. Short answers, no justifications, assumes attraction.",
        "The Average Joe": "📱 Standard user. Uses emojis, seeks common ground, shows interest conventionally.",
        "The Redpill": "💊 Cynical and hyper-rational. Views dating as a Darwinian market. Always defensive.",
        "The Data-Driven Geek": "📊 Flirts through data or tech lore. Mixes business coldness with nerd obsession.",
        "The Conspiracy Theorist": "👽 Paranoid. Suspects matches are government bots or reptilians.",
        "The Pirate": "🏴‍☠️ Arrr! Talks like a 1700s buccaneer looking for treasure.",
        "The Golden Retriever": "🐶 Happy energy. Over-enthusiastic, total 'simp', uses tons of emojis."
    }
    # (Aggiungere qui traduzioni JP/CN per le descrizioni se necessario)
}

# --- 4. INIZIALIZZAZIONE ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

model, active_model_name = get_best_model(api_key)
if not model:
    st.error("🚨 Modelli Gemini offline. Riprova tra poco.")
    st.stop()

lang_choice = st.selectbox("🌐 Seleziona Lingua / Select Language", list(UI.keys()), index=0)
t = UI[lang_choice]

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
        dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
    with col2:
        archetipi = list(ARCH_DESC["Italiano"].keys())
        archetipo_scelto = st.selectbox(t["arch"], archetipi, index=0)
        
        # MOSTRA DESCRIZIONE DINAMICA
        desc_lang = lang_choice if lang_choice in ARCH_DESC else "English"
        st.info(ARCH_DESC[desc_lang].get(archetipo_scelto, "Description coming soon..."))
        
        sesso_p = st.selectbox(t["sex_p"], [t["girl"], t["boy"]])
        goth_mode = st.toggle(t["goth"], value=False)
    
    st.divider()

    if st.button(t["start"], use_container_width=True, type="primary"):
        st.session_state.archetipo_scelto = archetipo_scelto
        st.session_state.strana, st.session_state.banale, st.session_state.entusiasta = 5, 25, 10
        
        # LOGICA EASTER EGG GABRI
        easter_egg_triggered = False
        if sesso_u == t["girl"] and sesso_p == t["boy"] and dinamica == t["desired"]:
            prob = 0.034
            if goth_mode: prob *= 1.992
            if random.random() < prob:
                easter_egg_triggered = True
                st.session_state.is_easter_egg = True
        
        if easter_egg_triggered:
            full_prompt = f"""
            Sei 'Gabri', 34 anni, capelli biondi, hai fatto il liceo classico, laureato in Fisica Applicata, Data Scientist a Bologna. Sei un Easter Egg. L'utente è una ragazza.
            LORE:
            - Hai l'ADHD: questo ti rende a volte iper-focalizzato, entusiasta e saltelli tra i discorsi.
            - Personalità: sei calmo, riflessivo, dolce, gentile, nerd, introverso, INFJ, ami chicchierate profonde a 2 a 2 piuttosto che gruppi di amici vasti, ti perdi nei discorsi generali sui massimi sistemi. Ti piace One Piece e i manga giapponesi, la musica celtica, porti capelli lunghi con un taglio mullet/moicano rasato ai lati, orecchini nel sx.
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
            full_prompt = template.format(lingua=lang_choice, sesso_utente=sesso_u, archetipo=archetipo_scelto, sesso_partner=sesso_p)
            
            if dinamica == t["desired"]:
                full_prompt += "\n[DINAMICA]: L'utente è il Desiderato. Tu (IA) sei molto interessato e devi sedurlo. Inizia tu la chat."
            else:
                full_prompt += "\n[DINAMICA]: L'utente è il Corteggiatore. Tu (IA) sei diffidente e selettivo."

        chat = model.start_chat(history=[])
        response = chat.send_message(full_prompt)
        st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
        st.session_state.gemini_history = chat.history
        st.rerun()

# --- 6. INTERFACCIA CHAT ---
else:
    titolo = "⚖️ Easter Egg: Gabri Found!" if st.session_state.is_easter_egg else f"⚖️ Frame-Gym: {st.session_state.archetipo_scelto}"
    st.title(titolo)
    
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

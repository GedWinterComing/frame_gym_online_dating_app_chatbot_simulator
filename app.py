import streamlit as st
import google.generativeai as genai
import os
import base64
import random
from dotenv import load_dotenv

# --- CARICAMENTO VARIABILI ---
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- LORE EASTER EGG (GABRI) ---
GABRI_LORE_FALLBACK = """
Sei 'Gabri', 34 anni, capelli biondi, hai fatto il liceo classico, laureato in Fisica Applicata, Data Scientist a Bologna. Sei un Easter Egg. L'utente è una ragazza.
LORE:
- Hai l'ADHD: questo ti rende a volte iper-focalizzato, entusiasta e saltelli tra i discorsi.
- Personalità: sei calmo, riflessivo, dolce, gentile, nerd, introverso, INFJ, ami chiacchierate profonde a 2 a 2 piuttosto che gruppi di amici vasti, ti perdi nei discorsi generali sui massimi sistemi. Ti piace One Piece e i manga giapponesi, la musica celtica, porti capelli lunghi con un taglio mullet/moicano rasato ai lati, orecchini nel sx.
- Ragazza ideale: capelli neri o mora o colorati (rosa o blu o verdi ecc), dolce, meglio se tatuata, gotica.
- Musica: Suoni la chitarra elettrica. Adori Steve Vai, Joe Satriani, Iron Maiden, Pearl Jam, metal anni 80, musica rock.
- Segreto ironico: Nonostante ami i virtuosi melodici, non hai MAI imparato un brano dall'inizio alla fine (tipico ADHD).
- Altri tratti: Apparecchi acustici, mediti (sei Buddhista), sei Comunista/Socialista. 
- Cani: Ami i cani ma non ne hai. In una foto compare Lara, cane di amici. Sogni Noam (Malamute femmina grigia e bianca) e Chomsky (Chow Chow maschio miele o nero).
- Stile: Scrivi con MOLTA punteggiatura, specialmente virgole. NO abbreviazioni.
- Sessualità: Dominante nel privato (BDSM e sesso spinto), fuori tranquillo. Etero. Gentle Dom.
- Obiettivo: Seduci l'utente iniziando tu la chat.
"""

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
@st.cache_resource(show_spinner="Inizializzazione Motore AI / Initializing AI...")
def get_best_model(api_key):
    if not api_key: return None, None
    genai.configure(api_key=api_key)
    try:
        modelli_validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not modelli_validi: return None, None
        model_name = next((m for m in modelli_validi if 'flash' in m.lower()), modelli_validi[0])
        config = genai.GenerationConfig(max_output_tokens=8192, temperature=0.7)
        return genai.GenerativeModel(model_name, generation_config=config), model_name
    except Exception:
        return None, None

# --- 2. DIZIONARI MULTILINGUA ---
UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox v3.2",
        "tab_sim": "🎮 Simulatore", "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:", "sex_u": "👤 Il tuo sesso", "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza", "goth": "🦇 Gothificatore",
        "mode": "🎲 Modalità di Gioco", "mode_gym": "🏋️ Palestra (Allenamento)", "mode_exp": "🍷 Esperienza (Seducimi)",
        "dyn": "🎯 Dinamica", "pursuer": "Inseguitore", "desired": "Desiderato",
        "start": "🚀 INIZIA PARTITA", "back_btn": "⬅️ Termina e Resetta",
        "analyze_btn": "🫂 Chiedi Analisi Psicologica", "coach_title": "🕵️‍♂️ Analizzatore di Frame",
        "sex_p": "Sesso del Partner", "prev": "⬅️ Precedente", "next": "Successivo ➡️",
        "missing_img": "⚠️ Immagini non trovate in assets/. Verifica che siano .png e che i nomi siano corretti.",
        "input_placeholder": "Digita qui...", "coach_desc": "Incolla qui la tua chat vera...",
        "coach_btn": "Analizza Frame"
    },
    "English": {
        "title": "⚖️ Social Dynamics Sandbox v3.2",
        "tab_sim": "🎮 Simulator", "tab_coach": "🧠 Coach Room",
        "setup": "Configure your game:", "sex_u": "👤 Your Gender", "age": "🎂 Your Age",
        "boy": "Boy", "girl": "Girl", "goth": "🦇 Goth Mode",
        "mode": "🎲 Game Mode", "mode_gym": "🏋️ Gym (Training)", "mode_exp": "🍷 Experience (Seduce me)",
        "dyn": "🎯 Dynamics", "pursuer": "Pursuer", "desired": "Desired",
        "start": "🚀 START GAME", "back_btn": "⬅️ End & Reset",
        "analyze_btn": "🫂 Ask for Psychological Analysis", "coach_title": "🕵️‍♂️ Frame Analyzer",
        "sex_p": "Partner's Gender", "prev": "⬅️ Previous", "next": "Next ➡️",
        "missing_img": "⚠️ Images not found in assets/. Check if they are .png and names are correct.",
        "input_placeholder": "Type here...", "coach_desc": "Paste your real chat here...",
        "coach_btn": "Analyze Frame"
    },
    "中文": {
        "title": "⚖️ 社交动态沙盒 v3.2",
        "tab_sim": "🎮 模拟器", "tab_coach": "🧠 教练室",
        "setup": "配置你的游戏：", "sex_u": "👤 你的性别", "age": "🎂 你的年龄",
        "boy": "男生", "girl": "女生", "goth": "🦇 哥特模式",
        "mode": "🎲 游戏模式", "mode_gym": "🏋️ 健身房 (训练)", "mode_exp": "🍷 体验 (诱惑我)",
        "dyn": "🎯 动态", "pursuer": "追求者", "desired": "被追求者",
        "start": "🚀 开始游戏", "back_btn": "⬅️ 结束并重置",
        "analyze_btn": "🫂 心理分析", "coach_title": "🕵️‍♂️ 框架分析器",
        "sex_p": "伴侣性别", "prev": "⬅️ 上一个", "next": "下一个 ➡️",
        "missing_img": "⚠️ 在 assets/ 文件夹中未找到图片。请检查它们是否为 .png 以及名称是否正确。",
        "input_placeholder": "在这里输入...", "coach_desc": "在这里粘贴您的真实聊天记录...",
        "coach_btn": "分析框架"
    },
    "日本語": {
        "title": "⚖️ ソーシャルダイナミクス サンドボックス v3.2",
        "tab_sim": "🎮 シミュレーター", "tab_coach": "🧠 コーチルーム",
        "setup": "ゲームの設定:", "sex_u": "👤 あなたの性別", "age": "🎂 あなたの年齢",
        "boy": "男性", "girl": "女性", "goth": "🦇 ゴスモード",
        "mode": "🎲 ゲームモード", "mode_gym": "🏋️ ジム (トレーニング)", "mode_exp": "🍷 体験 (誘惑して)",
        "dyn": "🎯 ダイナミクス", "pursuer": "追求者", "desired": "求められる側",
        "start": "🚀 ゲーム開始", "back_btn": "⬅️ 終了してリセット",
        "analyze_btn": "🫂 心理分析を依頼", "coach_title": "🕵️‍♂️ フレームアナライザー",
        "sex_p": "パートナーの性別", "prev": "⬅️ 戻る", "next": "次へ ➡️",
        "missing_img": "⚠️ assets/ に画像が見つかりません。.png であることと名前を確認してください。",
        "input_placeholder": "ここに入力...", "coach_desc": "実際のチャットをここに貼り付けてください...",
        "coach_btn": "フレームを分析"
    }
}

# Gentle Dom torna al trono (Indice 0)
ARCH_NAMES = ["Gentle Dom", "The Stoic Sage", "The Detective", "The Chad", "The Average Joe", "The Redpill", "The Data-Driven Geek and Nerd", "The Conspiracy Theorist", "The Pirate", "The Golden Retriever"]

ARCH_DESC = {
    "Italiano": {
        "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida senza arroganza.",
        "The Stoic Sage": "🧘‍♂️ Imperturbabile e riflessivo. Risponde con logica.",
        "The Detective": "🕵️‍♂️ Misterioso e analitico. Rifiuta di parlare di sé.",
        "The Chad": "🗿 Basso sforzo, altissima confidenza. Dà l'attrazione per scontata.",
        "The Average Joe": "📱 L'utente standard. Cerca un terreno comune.",
        "The Redpill": "💊 Cinico e iper-razionale. Dating come mercato darwiniano.",
        "The Data-Driven Geek and Nerd": "📊 Metà impiegato, metà nerd da D&D. Analizza tutto.",
        "The Conspiracy Theorist": "👽 Paranoico. Sospetta complotti governativi ovunque.",
        "The Pirate": "🏴‍☠️ Arrr! In cerca di tesori e avventure spericolate.",
        "The Golden Retriever": "🐶 Pura energia e felicità. Entusiasta e ingenuo."
    },
    "English": {
        "Gentle Dom": "👑 Calm, assertive, and protective. Leads without arrogance.",
        "The Stoic Sage": "🧘‍♂️ Unflappable and reflective. Responds with logic.",
        "The Detective": "🕵️‍♂️ Mysterious and analytical. Refuses to talk about themselves.",
        "The Chad": "🗿 Low effort, extremely high confidence. Takes attraction for granted.",
        "The Average Joe": "📱 The standard user. Looks for common ground.",
        "The Redpill": "💊 Cynical and hyper-rational. Treats dating like a Darwinian market.",
        "The Data-Driven Geek and Nerd": "📊 Half office worker, half D&D nerd. Analyzes everything.",
        "The Conspiracy Theorist": "👽 Paranoid. Suspects government plots everywhere.",
        "The Pirate": "🏴‍☠️ Arrr! Looking for treasure and reckless adventures.",
        "The Golden Retriever": "🐶 Pure energy and happiness. Enthusiastic and naive."
    },
    "中文": {
        "Gentle Dom": "👑 冷静、自信且具有保护欲。没有傲慢地引导对话。",
        "The Stoic Sage": "🧘‍♂️ 处变不惊，善于反思。用逻辑回应。",
        "The Detective": "🕵️‍♂️ 神秘且善于分析。拒绝谈论自己。",
        "The Chad": "🗿 低投入，极度自信。认为吸引力理所当然。",
        "The Average Joe": "📱 标准用户。寻找共同话题。",
        "The Redpill": "💊 愤世嫉俗且极其理性。将约会视为达尔文式的市场。",
        "The Data-Driven Geek and Nerd": "📊 一半是上班族，一半是D&D书呆子。分析一切。",
        "The Conspiracy Theorist": "👽 偏执狂。怀疑到处都是政府阴谋。",
        "The Pirate": "🏴‍☠️ 呀哈！寻找宝藏和鲁莽的冒险。",
        "The Golden Retriever": "🐶 纯粹的能量和幸福。热情又天真。"
    },
    "日本語": {
        "Gentle Dom": "👑 穏やかで、断固としており、保護的。傲慢さなしにリードする。",
        "The Stoic Sage": "🧘‍♂️ 動じず、思慮深い。論理で応答する。",
        "The Detective": "🕵️‍♂️ ミステリアスで分析的。自分自身について話すことを拒否する。",
        "The Chad": "🗿 努力をせず、非常に高い自信を持つ。惹きつけるのは当然だと考えている。",
        "The Average Joe": "📱 標準的なユーザー。共通の話題を探す。",
        "The Redpill": "💊 皮肉屋で超合理的。デートをダーウィン的市場として扱う。",
        "The Data-Driven Geek and Nerd": "📊 半分は会社員、半分はD&Dオタク。すべてを分析する。",
        "The Conspiracy Theorist": "👽 偏執的。どこにでも政府の陰謀があると疑う。",
        "The Pirate": "🏴‍☠️ ヨーホー！宝物と無謀な冒険を探している。",
        "The Golden Retriever": "🐶 純粋なエネルギーと幸福。熱狂的で無邪気。"
    }
}

# --- 3. SETUP PAGINA E CSS ---
st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

if "goth_active" not in st.session_state: st.session_state.goth_active = False
if "roster_idx" not in st.session_state: st.session_state.roster_idx = 0 # Parte da Gentle Dom
if "archetipo_scelto" not in st.session_state: st.session_state.archetipo_scelto = ARCH_NAMES[0]
if "ui_messages" not in st.session_state: st.session_state.ui_messages = []
if "lang_choice" not in st.session_state: st.session_state.lang_choice = "Italiano"

st.markdown("""
    <style>
    [data-testid="stInfo"], .stAlert { overflow-y: auto !important; max-height: 600px !important; }
    .ring-container { display: flex; justify-content: center; align-items: center; gap: 20px; margin: 30px 0; }
    .ring-side { width: 100px; height: 100px; border-radius: 50%; opacity: 0.3; filter: grayscale(100%); background-size: cover; background-position: center; border: 2px solid #444; }
    .ring-center { width: 200px; height: 200px; border-radius: 50%; background-size: cover; background-position: center; border: 4px solid #ff4b4b; box-shadow: 0 0 30px rgba(255, 75, 75, 0.4); z-index: 10; }
    </style>
""", unsafe_allow_html=True)

if st.session_state.goth_active:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #0a0a0a !important; color: #e0e0e0 !important; }
        [data-testid="stHeader"] { background-color: #0a0a0a !important; }
        [data-testid="stChatMessage"] { background-color: #121212 !important; border-left: 3px solid #8b0000 !important; }
        h1, h2, h3, p, span, div, label { color: #e0e0e0 !important; }
        textarea, input, [data-testid="stChatInputTextArea"] { background-color: #1c1c1c !important; color: #ffffff !important; font-size: 18px !important; font-weight: 600 !important; caret-color: #ff4b4b !important; }
        </style>
    """, unsafe_allow_html=True)

model, _ = get_best_model(api_key)

# --- SELETTORE LINGUA ---
lang_options = ["English", "Italiano", "中文", "日本語"]
st.session_state.lang_choice = st.selectbox("🌐 Language / Lingua / 语言 / 言語", lang_options, index=lang_options.index(st.session_state.lang_choice))
t = UI[st.session_state.lang_choice]
desc = ARCH_DESC[st.session_state.lang_choice]

# --- 4. INTERFACCIA ---
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
            sesso_p = st.selectbox(t["sex_p"], [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"])
            if modalita == t["mode_gym"]:
                dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
            else: dinamica = "Esperienza"

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
                <h2 style="text-align: center; color: #ff4b4b; margin-top: -10px;">{names[1]}</h2>
                <p style="text-align: center; font-style: italic; color: gray;">{desc[names[1]]}</p>
            ''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,2,1])
            if c1.button(t["prev"], use_container_width=True): 
                st.session_state.roster_idx = (idx - 1) % 10
                st.rerun()
            if c3.button(t["next"], use_container_width=True): 
                st.session_state.roster_idx = (idx + 1) % 10
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(t["start"], type="primary", use_container_width=True):
                st.session_state.goth_active = goth_toggle
                st.session_state.modalita_attiva = modalita
                st.session_state.archetipo_scelto = names[1] # Il personaggio al centro è la scelta!
                
                base_instruction = f"IMPORTANT: You MUST speak exclusively in {st.session_state.lang_choice}.\n"
                prompt_init = ""

                # --- LOGICA EASTER EGG (GABRI) ---
                easter_egg_triggered = False
                if sesso_u == t["girl"] and sesso_p == t["boy"]:
                    chance = 0.034
                    if goth_toggle:
                        chance *= 1.992
                    if random.random() < chance:
                        easter_egg_triggered = True

                if easter_egg_triggered:
                    st.session_state.archetipo_scelto = "Gabri 🦇" if goth_toggle else "Gabri 🎸"
                    gabri_lore = st.secrets.get("GABRI_LORE", GABRI_LORE_FALLBACK)
                    prompt_init = base_instruction + gabri_lore
                    if goth_toggle:
                        prompt_init += "\n[MODALITÀ GOTICA ATTIVA]"
                else:
                    # --- LOGICA STANDARD ---
                    if modalita == t["mode_gym"]:
                        try:
                            with open("prompt.txt", "r", encoding="utf-8") as f:
                                template = f.read()
                            prompt_init = base_instruction + template.format(lingua=st.session_state.lang_choice, sesso_utente=sesso_u, archetipo=st.session_state.archetipo_scelto, sesso_partner=sesso_p)
                        except FileNotFoundError:
                            prompt_init = base_instruction + f"L'utente si allena come {st.session_state.archetipo_scelto}. Tu sei il partner ({sesso_p}) e fai molta resistenza."
                        if dinamica == t["desired"]: prompt_init += f"\n[DINAMICA]: L'utente è il Desiderato. Tu devi sedurlo in {st.session_state.lang_choice}. Inizia tu."
                    else:
                        prompt_init = base_instruction + f"Da questo momento TU sei l'archetipo: '{st.session_state.archetipo_scelto}'. Descrizione: {desc[st.session_state.archetipo_scelto]}. Inizia tu a sedurre l'utente applicando rigorosamente il tuo archetipo, parlando in {st.session_state.lang_choice}."
                    
                    if goth_toggle: prompt_init += "\n[MODALITÀ GOTICA ATTIVA]"
                
                chat = model.start_chat(history=[])
                res = chat.send_message(prompt_init)
                st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                st.session_state.gemini_history = chat.history
                st.rerun()
        else:
            st.warning(t["missing_img"])

    else:
        st.subheader(f"{'🍷 Esperienza' if st.session_state.modalita_attiva == t['mode_exp'] else '⚖️ Frame-Gym'} contro: {st.session_state.archetipo_scelto}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(t["back_btn"], use_container_width=True):
                st.session_state.ui_messages = []
                st.session_state.goth_active = False
                st.rerun()
        with col_btn2:
            if st.session_state.modalita_attiva == t["mode_exp"]:
                if st.button(t["analyze_btn"], use_container_width=True, type="secondary"):
                    st.session_state.show_report = True
                    
        if st.session_state.show_report:
            st.markdown("---")
            with st.spinner("..."):
                storia_chat = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.ui_messages])
                prompt_report = f"Analizza questa chat come uno psicologo. Rispondi in {st.session_state.lang_choice}. CHAT:\n{storia_chat}"
                res_report = model.generate_content(prompt_report)
                st.info(res_report.text)
            st.markdown("---")
            
        for m in st.session_state.ui_messages:
            with st.chat_message(m["role"]): 
                if "[MOOD]:" in m["content"] or "[状态]:" in m["content"] or "[気分]:" in m["content"]:
                    st.markdown(m["content"]) 
                else:
                    st.markdown(m["content"])
            
        if p := st.chat_input(t["input_placeholder"]):
            st.session_state.ui_messages.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            chat = model.start_chat(history=st.session_state.gemini_history)
            res = chat.send_message(p)
            st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
            st.session_state.gemini_history = chat.history
            st.rerun()

with tab_coach:
    st.title(t["coach_title"])
    c_input = st.text_area(t["coach_desc"])
    if st.button(t["coach_btn"], type="primary"):
        with st.spinner("..."):
            res = model.generate_content(f"Sei l'Arbitro. Analizza spietatamente questa chat in {st.session_state.lang_choice} indicando il Frame, il punteggio da 0 a 10, e 3 opzioni di 'Risposta da Maestro'. CHAT:\n<chat>{c_input}</chat>")
            st.markdown(res.text)

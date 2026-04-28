import streamlit as st
import google.generativeai as genai
import os
import base64
import random
import pandas as pd
import altair as alt
from dotenv import load_dotenv

# --- CARICAMENTO VARIABILI E GESTIONE LOCALE/CLOUD ---
load_dotenv()

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("GEMINI_API_KEY")

try:
    gabri_lore = st.secrets["GABRI_LORE"]
except (KeyError, FileNotFoundError):
    gabri_lore = GABRI_LORE_LOCALE

def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None
    return None

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

# --- DIZIONARIO NOMI DINAMICI ---
DEFAULT_NAMES = {
    "Italiano": {"boy": "Luca", "girl": "Elena"},
    "English": {"boy": "John", "girl": "Emma"},
    "中文": {"boy": "Wei", "girl": "Jing"},
    "日本語": {"boy": "Ken", "girl": "Sakura"}
}

UI = {
    "Italiano": {
        "title": "⚖️ Social Dynamics Sandbox v4.8",
        "tab_sim": "🎮 Simulatore", "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:", "name_u": "Il Tuo Nome", "sex_u": "👤 Il tuo sesso", "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza", "goth": "🦇 Gothificatore",
        "mode": "🎲 Modalità di Gioco", "mode_gym": "🏋️ Palestra (Tu sei l'archetipo)", "mode_exp": "🍷 Esperienza (Il Chatbot impersona l'archetipo)",
        "dyn": "🎯 Dinamica", "pursuer": "Seduttore (Tu insegui)", "desired": "Diffidente (Fatti sedurre)",
        "start": "🚀 INIZIA PARTITA", "back_btn": "⬅️ Termina e Resetta",
        "analyze_btn": "🫂 Chiedi Analisi Psicologica", "coach_title": "🕵️‍♂️ Analizzatore di Frame",
        "sex_p": "Sesso del Partner (Chatbot)", "prev": "⬅️ Precedente", "next": "Successivo ➡️",
        "missing_img": "⚠️ Immagini non trovate. Verifica i nomi e le cartelle (assets/ o goth/).",
        "input_placeholder": "Digita qui...", "coach_desc": "Incolla qui la tua chat vera...",
        "coach_btn": "Analizza Frame",
        "offline": "📵 L'utente è andato Offline. La chat è terminata.",
        "slider_weird": "👽 Strane/Caotiche (%)", "slider_boring": "🥱 Banali/Monosillabi (%)", "slider_enth": "🐶 Entusiaste (%)",
        "rate_warning_msg": "⏳ Nota: L'IA ha un limite di messaggi. Non inviare messaggi troppo velocemente.",
        "rate_error": "🚨 Limite API Raggiunto! L'IA si sta ricaricando. Aspetta circa 60 secondi e clicca il tasto qui sotto per inviare il tuo messaggio.",
        "retry_btn": "🔄 Riprova a Inviare"
    },
    "English": {
        "title": "⚖️ Social Dynamics Sandbox v4.8",
        "tab_sim": "🎮 Simulator", "tab_coach": "🧠 Coach Room",
        "setup": "Configure your game:", "name_u": "Your Name", "sex_u": "👤 Your Gender", "age": "🎂 Your Age",
        "boy": "Boy", "girl": "Girl", "goth": "🦇 Goth Mode",
        "mode": "🎲 Game Mode", "mode_gym": "🏋️ Gym (You are the archetype)", "mode_exp": "🍷 Experience (Chatbot impersonates archetype)",
        "dyn": "🎯 Dynamics", "pursuer": "Seducer (You pursue)", "desired": "Skeptical (Get seduced)",
        "start": "🚀 START GAME", "back_btn": "⬅️ End & Reset",
        "analyze_btn": "🫂 Ask for Psychological Analysis", "coach_title": "🕵️‍♂️ Frame Analyzer",
        "sex_p": "Partner's Gender (Chatbot)", "prev": "⬅️ Previous", "next": "Next ➡️",
        "missing_img": "⚠️ Images not found. Check names and folders (assets/ or goth/).",
        "input_placeholder": "Type here...", "coach_desc": "Paste your real chat here...",
        "coach_btn": "Analyze Frame",
        "offline": "📵 The user went Offline. Chat has ended.",
        "slider_weird": "👽 Weird/Chaotic (%)", "slider_boring": "🥱 Boring/One-word (%)", "slider_enth": "🐶 Enthusiastic (%)",
        "rate_warning_msg": "⏳ Note: The AI has a rate limit. Please do not send messages too rapidly.",
        "rate_error": "🚨 API Limit Reached! The AI is cooling down. Wait about 60 seconds and click the button below to resend your message.",
        "retry_btn": "🔄 Retry Sending"
    },
    "中文": {
        "title": "⚖️ 社交动态沙盒 v4.8",
        "tab_sim": "🎮 模拟器", "tab_coach": "🧠 教练室",
        "setup": "配置你的游戏：", "name_u": "你的名字", "sex_u": "👤 你的性别", "age": "🎂 你的年龄",
        "boy": "男生", "girl": "女生", "goth": "🦇 哥特模式",
        "mode": "🎲 游戏模式", "mode_gym": "🏋️ 健身房 (你是原型)", "mode_exp": "🍷 体验 (聊天机器人扮演原型)",
        "dyn": "🎯 动态", "pursuer": "诱惑者 (你追求)", "desired": "怀疑者 (被诱惑)",
        "start": "🚀 开始游戏", "back_btn": "⬅️ 结束并重置",
        "analyze_btn": "🫂 心理分析", "coach_title": "🕵️‍♂️ 框架分析器",
        "sex_p": "伴侣性别 (聊天机器人)", "prev": "⬅️ 上一个", "next": "下一个 ➡️",
        "missing_img": "⚠️ 未找到图片。请检查名称和文件夹 (assets/ 或 goth/)。",
        "input_placeholder": "在这里输入...", "coach_desc": "在这里粘贴您的真实聊天记录...",
        "coach_btn": "分析框架",
        "offline": "📵 用户已离线。聊天结束。",
        "slider_weird": "👽 奇怪/混乱 (%)", "slider_boring": "🥱 无聊/敷衍 (%)", "slider_enth": "🐶 热情 (%)",
        "rate_warning_msg": "⏳ 注意：AI 存在调用频率限制，请勿发送过快。",
        "rate_error": "🚨 API 限制！AI 需要冷却。请等待约 60 秒，然后点击下方按钮重新发送。",
        "retry_btn": "🔄 重新发送"
    },
    "日本語": {
        "title": "⚖️ ソーシャルダイナミクス サンドボックス v4.8",
        "tab_sim": "🎮 シミュレーター", "tab_coach": "🧠 コーチルーム",
        "setup": "ゲームの設定:", "name_u": "あなたの名前", "sex_u": "👤 あなたの性別", "age": "🎂 あなたの年齢",
        "boy": "男性", "girl": "女性", "goth": "🦇 ゴスモード",
        "mode": "🎲 ゲームモード", "mode_gym": "🏋️ ジム (あなたがアーキタイプ)", "mode_exp": "🍷 体験 (チャットボットがアーキタイプを演じる)",
        "dyn": "🎯 ダイナミクス", "pursuer": "誘惑者 (あなたが追求する)", "desired": "懐疑的 (誘惑される)",
        "start": "🚀 ゲーム開始", "back_btn": "⬅️ 終了してリセット",
        "analyze_btn": "🫂 心理分析を依頼", "coach_title": "🕵️‍♂️ フレームアナライザー",
        "sex_p": "パートナーの性別 (チャットボット)", "prev": "⬅️ 戻る", "next": "次へ ➡️",
        "missing_img": "⚠️ 画像が見つかりません。名前とフォルダ（assets/ または goth/）を確認してください。",
        "input_placeholder": "ここに入力...", "coach_desc": "実際のチャットをここに貼り付けてください...",
        "coach_btn": "フレームを分析",
        "offline": "📵 ユーザーはオフラインになりました。チャットは終了しました。",
        "slider_weird": "👽 奇妙な/カオス (%)", "slider_boring": "🥱 退屈/一言 (%)", "slider_enth": "🐶 熱狂的 (%)",
        "rate_warning_msg": "⏳ メモ: AI にはレート制限があります。メッセージを速く送りすぎないでください。",
        "rate_error": "🚨 API 制限到達！AI が冷却中です。約60秒待ってから下のボタンをクリックして再送信してください。",
        "retry_btn": "🔄 再送信"
    }
}

ARCH_NAMES = ["The Average Joe", "Gentle Dom", "The Stoic Sage", "The Detective", "The Chad", "The Redpill", "The Data-Driven Geek and Nerd", "The Conspiracy Theorist", "The Pirate", "The Golden Retriever"]

ARCH_DESC = {
    "Italiano": {
        "The Average Joe": "📱 L'utente standard. Usa emoji, cerca sempre un terreno comune, fa domande banali e mostra un interesse convenzionale. Evita conflitti, è amichevole ma prevedibile.",
        "Gentle Dom": "👑 Calmo, assertivo e protettivo. Guida la conversazione senza arroganza né aggressività. Non si giustifica mai, offre soluzioni e fa sentire l'altra persona al sicuro ma subordinata.",
        "The Stoic Sage": "🧘‍♂️ Imperturbabile e distaccato. Risponde alle provocazioni con logica o filosofia. Non si scompone emotivamente e disinnesca il dramma con fredda e tagliente razionalità.",
        "The Detective": "🕵️‍♂️ Misterioso e analitico. Risponde alle domande con altre domande, indaga ossessivamente sull'altro e rifiuta categoricamente di rivelare dettagli su di sé.",
        "The Chad": "🗿 Basso sforzo, altissima confidenza. Dà l'attrazione per scontata, usa frasi brevissime, ignora le critiche e non cerca mai l'approvazione altrui. Sfacciato e polarizzante.",
        "The Redpill": "💊 Cinico, calcolatore e disilluso. Tratta le relazioni come un mercato spietato, valuta l'altro come un 'asset', evidenzia le dinamiche sociali crude e usa un linguaggio strategico.",
        "The Data-Driven Geek and Nerd": "📊 Ossessionato dai dati e dalla cultura pop. Paragona le situazioni a campagne di D&D, usa fogli Excel mentali per valutare il partner, è goffamente analitico ma molto entusiasta.",
        "The Conspiracy Theorist": "👽 Intensamente paranoico e diffidente. Sospetta che l'altro sia un bot, una spia o un ologramma. Collega argomenti normali a cospirazioni assurde e non si fida di nulla.",
        "The Pirate": "🏴‍☠️ Arrr! Parla e si comporta come un bucaniere del 1700. Cerca avventure, usa slang piratesco ('ciurma', 'bottino', 'grog'), è sfrontato, ribelle e non rispetta le regole moderne.",
        "The Golden Retriever": "🐶 Pura energia positiva. È eccessivamente felice, ingenuo, riempie l'altro di complimenti sinceri, usa tantissimi punti esclamativi ed è letteralmente un 'bravo ragazzo/ragazza'."
    },
    "English": {
        "The Average Joe": "📱 The standard user. Uses emojis, always looks for common ground, asks mundane questions, and shows conventional interest. Avoids conflicts, friendly but predictable.",
        "Gentle Dom": "👑 Calm, assertive, and protective. Leads the conversation without arrogance or aggression. Never justifies themselves, offers solutions, and makes the other feel safe but bound to their rules.",
        "The Stoic Sage": "🧘‍♂️ Unflappable and detached. Responds to provocations with logic or philosophy, never loses emotional control, and defuses drama with cold rationality.",
        "The Detective": "🕵️‍♂️ Mysterious and analytical. Answers questions with more questions, investigates the other person, and strictly refuses to reveal details about themselves.",
        "The Chad": "🗿 Low effort, extremely high confidence. Takes attraction for granted, uses very short sentences, ignores criticism, and never seeks approval. Brash and polarizing.",
        "The Redpill": "💊 Cynical, calculating, and disillusioned. Treats relationships like a ruthless market, evaluates the other as an 'asset', highlights raw social dynamics, and uses technical language.",
        "The Data-Driven Geek and Nerd": "📊 Obsessed with data and pop culture. Compares dating to D&D campaigns, uses mental Excel sheets to evaluate partners, awkwardly analytical but highly enthusiastic.",
        "The Conspiracy Theorist": "👽 Intensely paranoid and distrustful. Suspects you are a bot, a spy, or a hologram. Connects normal topics to absurd conspiracies and trusts nothing you say.",
        "The Pirate": "🏴‍☠️ Arrr! Speaks and acts like a true 1700s buccaneer. Seeks adventure, uses pirate slang ('crew', 'booty', 'grog'), is brazen, rebellious, and disrespects modern rules.",
        "The Golden Retriever": "🐶 Pure positive energy. Excessively happy, naive, showers you with sincere compliments, uses tons of exclamation marks, and is literally a 'good boy/girl'."
    },
    "中文": {
        "The Average Joe": "📱 标准用户。使用表情符号，总是寻找共同话题，问普通的问题，表现出传统的兴趣。避免冲突，友好但有时容易被预测。",
        "Gentle Dom": "👑 冷静、自信且具有保护欲。没有傲慢或攻击性地引导对话。从不为自己辩护，提供解决方案，让对方感到安全但服从于他们的规则。",
        "The Stoic Sage": "🧘‍♂️ 处变不惊，善于反思且超然。用逻辑或哲学回应挑衅，从不失控，用冷酷的理性化解戏剧性事件。",
        "The Detective": "🕵️‍♂️ 神秘且善于分析。用问题回答问题，调查对方，并断然拒绝透露关于自己的细节，保持一种神秘的氛围。",
        "The Chad": "🗿 低投入，极度自信。认为吸引力理所当然，使用极短的句子，无视批评，从不寻求认可。厚颜无耻且容易引起两极分化。",
        "The Redpill": "💊 愤世嫉俗、精于算计且幻想破灭。将恋爱关系视为无情的市场，将对方评估为‘资产’，强调残酷的社会动态。",
        "The Data-Driven Geek and Nerd": "📊 沉迷于数据和流行文化。将约会比作D&D战役，使用心理Excel表格来评估伴侣，笨拙地进行分析，但充满热情。",
        "The Conspiracy Theorist": "👽 极度偏执和多疑。怀疑你是一个机器人、间谍或全息图。将正常话题与荒谬的阴谋联系起来，不相信你说的任何话。",
        "The Pirate": "🏴‍☠️ 呀哈！像18世纪真正的海盗一样说话和行事。寻求冒险，使用海盗俚语，厚颜无耻，叛逆，不遵守现代规则。",
        "The Golden Retriever": "🐶 纯粹的积极能量。极其快乐，天真，用真诚的赞美淹没你，使用大量的感叹号，简直就是一个只想着取悦所有人的‘好孩子’。"
    },
    "日本語": {
        "The Average Joe": "📱 標準的なユーザー。絵文字を使い、常に共通点を探し、平凡な質問をし、ありきたりな関心を示す。争いを避け、友好的だが予測可能。",
        "Gentle Dom": "👑 穏やかで、断固としており、保護的。傲慢さや攻撃性なしに会話をリードする。言い訳せず、解決策を提示し、相手に安心感を与えつつ自分のルールに従わせる。",
        "The Stoic Sage": "🧘‍♂️ 動じず、思慮深く、超然としている。挑発には論理や哲学で応じ、決して感情的にならず、冷たい合理性でドラマを鎮める。",
        "The Detective": "🕵️‍♂️ ミステリアスで分析的。質問には質問で返し、相手を調査し、自分自身の詳細を明かすことを断固として拒否し、謎めいたオーラを保つ。",
        "The Chad": "🗿 努力をせず、非常に高い自信を持つ。惹きつけるのは当然だと考え、非常に短い文を使い、批判を無視し、決して承認を求めない。",
        "The Redpill": "💊 皮肉屋で、打算的で、幻滅している。恋愛を無情な市場として扱い、相手を「資産」として評価し、生々しい社会的力学を強調する。",
        "The Data-Driven Geek and Nerd": "📊 データとポップカルチャーに夢中。デートをD&Dのキャンペーンに例え、頭の中のExcelシートでパートナーを評価し、不器用に分析的だが情熱的。",
        "The Conspiracy Theorist": "👽 激しい被害妄想と不信感。あなたがボット、スパイ、ホログラムではないかと疑う。普通の話題を馬鹿げた陰謀に結びつけ、何も信じない。",
        "The Pirate": "🏴‍☠️ ヨーホー！18世紀の本当の海賊のように話し、行動する。冒険を求め、海賊のスラングを使い、厚かましく、現代のルールを無視する。",
        "The Golden Retriever": "🐶 純粋なポジティブエネルギー。過剰にハッピーで、無邪気で、心からの褒め言葉を浴びせ、感嘆符を多用する、まさに「いい子」。"
    }
}

st.set_page_config(page_title="Frame-Gym Pro", page_icon="⚖️", layout="centered")

if "goth_active" not in st.session_state: st.session_state.goth_active = False
if "roster_idx" not in st.session_state: st.session_state.roster_idx = 0 
if "archetipo_scelto" not in st.session_state: st.session_state.archetipo_scelto = ARCH_NAMES[0]
if "ui_messages" not in st.session_state: st.session_state.ui_messages = []
if "lang_choice" not in st.session_state: st.session_state.lang_choice = "Italiano"
if "nome_utente" not in st.session_state: st.session_state.nome_utente = "Anon"

if "pending_user_msg" not in st.session_state: st.session_state.pending_user_msg = None

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

lang_options = ["English", "Italiano", "中文", "日本語"]
st.session_state.lang_choice = st.selectbox("🌐 Language / Lingua / 语言 / 言語", lang_options, index=lang_options.index(st.session_state.lang_choice))
t = UI[st.session_state.lang_choice]
desc = ARCH_DESC[st.session_state.lang_choice]
MAX_TURNS_EXP = 20

tab_sim, tab_coach = st.tabs([t["tab_sim"], t["tab_coach"]])

with tab_sim:
    if not st.session_state.ui_messages:
        st.title(t["title"])
        st.write(t["setup"])
        
        col_sex, col_name, col_age = st.columns([1, 2, 1])
        with col_sex:
            sesso_u = st.selectbox(t["sex_u"], [t["boy"], t["girl"]])
        with col_name:
            gender_key = "boy" if sesso_u == t["boy"] else "girl"
            default_n = DEFAULT_NAMES[st.session_state.lang_choice][gender_key]
            nome_u = st.text_input(t["name_u"], value=default_n)
        with col_age:
            eta_u = st.slider(t["age"], 18, 40, 33)

        col1, col2 = st.columns(2)
        with col1:
            modalita = st.radio(t["mode"], [t["mode_gym"], t["mode_exp"]])
            if modalita == t["mode_gym"]:
                dinamica = st.radio(t["dyn"], [t["pursuer"], t["desired"]])
            else: dinamica = "Esperienza"
        with col2:
            sesso_p = st.selectbox(t["sex_p"], [t["girl"], t["boy"]])
            goth_toggle = st.toggle(t["goth"])

        st.markdown("---")
        st.markdown("### 🎲 " + ("Comportamento Partner" if st.session_state.lang_choice == "Italiano" else "Partner Behavior"))
        
        col_sliders, col_pie = st.columns([2, 1])
        with col_sliders:
            prob_strana = st.slider(t["slider_weird"], 0, 100, 5)
            prob_banale = st.slider(t["slider_boring"], 0, 100, 25)
            prob_enth = st.slider(t["slider_enth"], 0, 100, 10)
        
        if (prob_strana + prob_banale + prob_enth) > 100:
            st.error("⚠️ La somma non può superare 100.")
            prob_normale = 0
        else:
            prob_normale = 100 - (prob_strana + prob_banale + prob_enth)

        with col_pie:
            df_pie = pd.DataFrame({
                "Comportamento": ["Normale", "Strana", "Banale", "Entusiasta"],
                "Probabilità": [prob_normale, prob_strana, prob_banale, prob_enth]
            })
            df_pie = df_pie[df_pie["Probabilità"] > 0]
            
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=30).encode(
                theta=alt.Theta(field="Probabilità", type="quantitative"),
                color=alt.Color(field="Comportamento", type="nominal", 
                                scale=alt.Scale(domain=["Normale", "Strana", "Banale", "Entusiasta"], 
                                                range=["#4b4bff", "#ff4bff", "#888888", "#ffb400"]), 
                                legend=None),
                tooltip=["Comportamento", "Probabilità"]
            ).properties(width=150, height=150)
            
            st.altair_chart(pie_chart, use_container_width=True)

        st.markdown("---")

        base_dir = "assets"
        if modalita == t["mode_exp"] and goth_toggle:
            base_dir = "goth"

        if modalita == t["mode_gym"]:
            sub_dir = "femmine" if sesso_u == t["girl"] else "maschi"
        else:
            sub_dir = "femmine" if sesso_p == t["girl"] else "maschi"

        percorso_cartella = f"{base_dir}/{sub_dir}"

        idx = st.session_state.roster_idx
        names = [ARCH_NAMES[(idx-1)%10], ARCH_NAMES[idx], ARCH_NAMES[(idx+1)%10]]
        imgs = [get_base64_image(f"{percorso_cartella}/{n}.png") for n in names]

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
                
            with c2:
                if st.button(t["start"], type="primary", use_container_width=True):
                    st.session_state.goth_active = goth_toggle
                    st.session_state.modalita_attiva = modalita
                    st.session_state.archetipo_scelto = names[1] 
                    st.session_state.nome_utente = nome_u
                    
                    st.session_state.prob_normale = prob_normale
                    st.session_state.prob_strana = prob_strana
                    st.session_state.prob_banale = prob_banale
                    st.session_state.prob_enth = prob_enth
                    
                    base_instruction = f"IMPORTANT: You MUST speak exclusively in {st.session_state.lang_choice}.\n"
                    prompt_init = ""

                    easter_egg_triggered = False
                    if sesso_u == t["girl"] and sesso_p == t["boy"]:
                        chance = 0.034
                        if goth_toggle:
                            chance *= 1.992
                        if random.random() < chance:
                            easter_egg_triggered = True

                    if easter_egg_triggered:
                        st.session_state.archetipo_scelto = "Gabri 🦇" if goth_toggle else "Gabri 🎸"
                        prompt_init = base_instruction + gabri_lore.format(nome_utente=nome_u)
                        if goth_toggle:
                            prompt_init += "\n[MODALITÀ GOTICA ATTIVA]: Applica la formattazione testuale descritta sotto."
                    else:
                        if modalita == t["mode_gym"]:
                            try:
                                with open("prompt.txt", "r", encoding="utf-8") as f:
                                    template = f.read()
                                prompt_init = base_instruction + template.format(lingua=st.session_state.lang_choice, sesso_utente=sesso_u, nome_utente=nome_u, archetipo=st.session_state.archetipo_scelto, desc_archetipo=desc[st.session_state.archetipo_scelto], sesso_partner=sesso_p)
                            except FileNotFoundError:
                                prompt_init = base_instruction + f"L'utente {nome_u} ({sesso_u}) interpreta RIGOROSAMENTE l'archetipo {st.session_state.archetipo_scelto}. Le regole sono: {desc[st.session_state.archetipo_scelto]}. Tu sei il partner ({sesso_p}) e valuti il suo frame. Dai il Game Over se cede."
                            
                            if dinamica == t["desired"]: 
                                prompt_init += f"\n[DINAMICA]: L'utente {nome_u} è il Diffidente/Desiderato. Tu (IA) fai la corte. Se {nome_u} cede troppo in fretta o esce dal Frame da Diffidente, dichiara GAME OVER."
                            else:
                                prompt_init += f"\n[DINAMICA]: L'utente {nome_u} è il Seduttore. Tu (IA) fai molta resistenza. Se {nome_u} diventa bisognoso, rompe il Frame o supplica, dichiara GAME OVER."
                                
                        else:
                            prompt_init = base_instruction + f"Da questo momento TU sei l'archetipo: '{st.session_state.archetipo_scelto}'. Descrizione: {desc[st.session_state.archetipo_scelto]}. \nL'utente si chiama {nome_u}, ha {eta_u} anni, è un {sesso_u}. \nInizia tu a sedurre l'utente applicando rigorosamente il tuo archetipo, parlando in {st.session_state.lang_choice}. Ricorda che questa è una chat di appuntamenti online."
                        
                    if goth_toggle:
                        prompt_init += """
                        \n[MODALITÀ GOTICA ATTIVA]:
                        Il partner che devi simulare appartiene alla subcultura Goth.
                        - PROBABILITÀ PROFILO: Genera con il 70% di probabilità un Classic/Trad Goth. Altrimenti, scegli uno tra questi: Victorian/Romantic Goth, Industrial Goth, Cyber Goth, Gothabilly, Lolita Goth, Nu-Goth.
                        - ESTETICA TESTUALE: Usa occasionalmente la formattazione HTML per colorare singole parole chiave nel messaggio (es. <span style='color:magenta'>parola</span>), scegliendo tra i colori tipici dei capelli alternativi: magenta, cyan, limegreen o darkred. Usa molto il *corsivo* per dare un tono drammatico.
                        """
                    
                    try:
                        chat = model.start_chat(history=[])
                        res = chat.send_message(prompt_init)
                        st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                        st.session_state.gemini_history = chat.history
                        st.rerun()
                    except Exception as e:
                        st.error(t["rate_error"])
                    
            if c3.button(t["next"], use_container_width=True): 
                st.session_state.roster_idx = (idx + 1) % 10
                st.rerun()
        else:
            st.warning(t["missing_img"])

    else:
        st.subheader(f"{'🍷 Esperienza' if st.session_state.modalita_attiva == t['mode_exp'] else '⚖️ Palestra'} contro: {st.session_state.archetipo_scelto}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(t["back_btn"], use_container_width=True):
                st.session_state.ui_messages = []
                st.session_state.goth_active = False
                st.session_state.pending_user_msg = None
                st.rerun()
        with col_btn2:
            if st.session_state.modalita_attiva == t["mode_exp"]:
                if st.button(t["analyze_btn"], use_container_width=True, type="secondary"):
                    st.session_state.show_report = True
                    
        if st.session_state.show_report:
            st.markdown("---")
            with st.spinner("..."):
                storia_chat = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.ui_messages])
                prompt_report = f"Analizza questa chat come uno psicologo. Rispondi in {st.session_state.lang_choice}. L'utente si chiama {st.session_state.nome_utente}. CHAT:\n{storia_chat}"
                res_report = model.generate_content(prompt_report)
                st.info(res_report.text)
            st.markdown("---")
            
        st.caption(t["rate_warning_msg"])
            
        for m in st.session_state.ui_messages:
            with st.chat_message(m["role"]): 
                if "[MOOD]:" in m["content"] or "[状态]:" in m["content"] or "[気分]:" in m["content"]:
                    st.markdown(m["content"], unsafe_allow_html=True) 
                else:
                    st.markdown(m["content"], unsafe_allow_html=True)
        
        user_turns = sum(1 for m in st.session_state.ui_messages if m["role"] == "user")
        
        if st.session_state.modalita_attiva == t["mode_exp"] and user_turns >= MAX_TURNS_EXP:
            st.error(t["offline"])
        else:
            if st.session_state.pending_user_msg:
                st.error(t["rate_error"])
                st.info(f"**Tuo messaggio in sospeso:** {st.session_state.pending_user_msg}")
                if st.button(t["retry_btn"], type="primary"):
                    p = st.session_state.pending_user_msg
                    prompt_for_ai = p
                    
                    if hasattr(st.session_state, 'prob_normale'):
                        tipi_risposta = ["Normale", "Strana", "Banale", "Entusiasta"]
                        pesi = [st.session_state.prob_normale, st.session_state.prob_strana, st.session_state.prob_banale, st.session_state.prob_enth]
                        risposta_scelta = random.choices(tipi_risposta, weights=pesi, k=1)[0]
                        if risposta_scelta == "Strana": prompt_for_ai += "\n\n[SISTEMA]: Rispondi in modo CAOTICO o BIZZARRO."
                        elif risposta_scelta == "Banale": prompt_for_ai += "\n\n[SISTEMA]: Rispondi in modo ESTREMAMENTE noioso a monosillabi."
                        elif risposta_scelta == "Entusiasta": prompt_for_ai += "\n\n[SISTEMA]: Sii MOLTO ENTUSIASTA e fai complimenti."

                    try:
                        chat = model.start_chat(history=st.session_state.gemini_history)
                        res = chat.send_message(prompt_for_ai)
                        st.session_state.ui_messages.append({"role": "user", "content": p})
                        st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                        st.session_state.gemini_history = chat.history
                        st.session_state.pending_user_msg = None
                        st.rerun()
                    except Exception as e:
                        st.error(t["rate_error"])
            else:
                if p := st.chat_input(t["input_placeholder"]):
                    st.session_state.ui_messages.append({"role": "user", "content": p})
                    with st.chat_message("user"): st.markdown(p)
                    
                    prompt_for_ai = p
                    
                    if hasattr(st.session_state, 'prob_normale'):
                        tipi_risposta = ["Normale", "Strana", "Banale", "Entusiasta"]
                        pesi = [st.session_state.prob_normale, st.session_state.prob_strana, st.session_state.prob_banale, st.session_state.prob_enth]
                        risposta_scelta = random.choices(tipi_risposta, weights=pesi, k=1)[0]
                        
                        if risposta_scelta == "Strana":
                            prompt_for_ai += "\n\n[SISTEMA]: Per questo turno, ignora leggermente la logica del tuo archetipo e fornisci una risposta CAOTICA, BIZZARRA o TOTALMENTE FUORI CONTESTO."
                        elif risposta_scelta == "Banale":
                            prompt_for_ai += "\n\n[SISTEMA]: Per questo turno, sii ESTREMAMENTE noioso. Rispondi a monosillabi (es. 'Ah ok', 'Boh', 'Certo') senza fare domande."
                        elif risposta_scelta == "Entusiasta":
                            prompt_for_ai += "\n\n[SISTEMA]: Per questo turno, mostra un ENTUSIASMO INGIUSTIFICATO per quello che ha detto l'utente. Fai tanti complimenti."

                    if st.session_state.modalita_attiva == t["mode_exp"]:
                        if user_turns == MAX_TURNS_EXP - 3:
                            prompt_for_ai += f"\n\n[SISTEMA]: Mancano 2 messaggi alla fine. Nel tuo prossimo messaggio, inventa una scusa ASSOLUTAMENTE COERENTE CON IL TUO ARCHETIPO per dire a {st.session_state.nome_utente} che tra poco devi scappare via o staccarti dal telefono."
                        elif user_turns == MAX_TURNS_EXP - 1:
                            prompt_for_ai += f"\n\n[SISTEMA]: Questo è il tuo ULTIMO messaggio. Saluta definitivamente {st.session_state.nome_utente} e chiudi la conversazione in modo coerente col tuo archetipo, poi esci dalla chat."

                    try:
                        chat = model.start_chat(history=st.session_state.gemini_history)
                        res = chat.send_message(prompt_for_ai)
                        st.session_state.ui_messages.append({"role": "assistant", "content": res.text})
                        st.session_state.gemini_history = chat.history
                        st.rerun()
                    except Exception as e:
                        st.session_state.ui_messages.pop()
                        st.session_state.pending_user_msg = p
                        st.rerun()

with tab_coach:
    st.title(t["coach_title"])
    c_input = st.text_area(t["coach_desc"])
    if st.button(t["coach_btn"], type="primary"):
        with st.spinner("..."):
            res = model.generate_content(f"Sei l'Arbitro. Analizza spietatamente questa chat in {st.session_state.lang_choice} indicando il Frame, il punteggio da 0 a 10, e 3 opzioni di 'Risposta da Maestro'. CHAT:\n<chat>{c_input}</chat>")
            st.markdown(res.text)

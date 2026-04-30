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

@st.cache_resource(show_spinner="Inizializzazione Motore AI...")
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
        "title": "⚖️ Social Dynamics Sandbox v4.10",
        "tab_sim": "🎮 Simulatore", "tab_coach": "🧠 Coach Room",
        "setup": "Configura la tua partita:", "name_u": "Il Tuo Nome", "sex_u": "👤 Il tuo sesso", "age": "🎂 Tua Età",
        "boy": "Ragazzo", "girl": "Ragazza", "goth": "🦇 Gothificatore",
        "mode": "🎲 Modalità di Gioco", "mode_gym": "🏋️ Palestra (Tu sei l'archetipo)", "mode_exp": "🍷 Esperienza (Il Chatbot impersona l'archetipo)",
        "dyn": "🎯 Dinamica", "pursuer": "Seduttore (Tu insegui)", "desired": "Diffidente (Fatti sedurre)",
        "start": "🚀 INIZIA PARTITA", "back_btn": "⬅️ Termina e Resetta",
        "analyze_btn": "🫂 Chiedi Analisi Psicologica", "coach_title": "🕵️‍♂️ Analizzatore di Frame",
        "sex_p": "Sesso del Partner (Chatbot)", "prev": "⬅️ Precedente", "next": "Successivo ➡️",
        "missing_img": "⚠️ Immagini non trovate. Verifica i nomi e le cartelle (assets/ o goth/).",
        "input_placeholder": "Digita qui...", "coach_desc": "Incolla qui la chat reale...",
        "coach_btn": "Analizza Frame",
        "offline": "📵 L'utente è andato Offline. La chat è terminata.",
        "slider_weird": "👽 Strane/Caotiche (%)", "slider_boring": "🥱 Banali/Monosillabi (%)", "slider_enth": "🐶 Entusiaste (%)",
        "rate_warning_msg": "⏳ Nota: L'IA ha un limite di messaggi. Non inviare troppo velocemente.",
        "rate_error": "🚨 Limite API! Aspetta 60s e clicca Riprova.",
        "retry_btn": "🔄 Riprova a Inviare",
        "coach_arch_name": "Nome dell'archetipo da analizzare", "coach_arch_desc": "Spiega le regole di questo archetipo (Bio, stile, mindset)",
        "coach_arch_name_ph": "Esempio: Gentle Dom, Artista Maledetto...", "coach_arch_desc_ph": "Descrivi qui come dovrebbe comportarsi l'archetipo..."
    },
    "English": {
        "title": "⚖️ Social Dynamics Sandbox v4.10",
        "tab_sim": "🎮 Simulator", "tab_coach": "🧠 Coach Room",
        "setup": "Configure your game:", "name_u": "Your Name", "sex_u": "👤 Your Gender", "age": "🎂 Your Age",
        "boy": "Boy", "girl": "Girl", "goth": "🦇 Goth Mode",
        "mode": "🎲 Game Mode", "mode_gym": "🏋️ Gym (You are the archetype)", "mode_exp": "🍷 Experience (Chatbot impersonates archetype)",
        "dyn": "🎯 Dynamics", "pursuer": "Seducer (You pursue)", "desired": "Skeptical (Get seduced)",
        "start": "🚀 START GAME", "back_btn": "⬅️ End & Reset",
        "analyze_btn": "🫂 Ask for Psychological Analysis", "coach_title": "🕵️‍♂️ Frame Analyzer",
        "sex_p": "Partner's Gender (Chatbot)", "prev": "⬅️ Previous", "next": "Next ➡️",
        "missing_img": "⚠️ Images not found. Check names and folders (assets/ or goth/).",
        "input_placeholder": "Type here...", "coach_desc": "Paste real chat here...",
        "coach_btn": "Analyze Frame",
        "offline": "📵 The user went Offline. Chat has ended.",
        "slider_weird": "👽 Weird/Chaotic (%)", "slider_boring": "🥱 Boring/One-word (%)", "slider_enth": "🐶 Enthusiastic (%)",
        "rate_warning_msg": "⏳ Note: AI has rate limits. Don't send too fast.",
        "rate_error": "🚨 API Limit! Wait 60s and click Retry.",
        "retry_btn": "🔄 Retry Sending",
        "coach_arch_name": "Name of the archetype to analyze", "coach_arch_desc": "Explain the rules of this archetype (Bio, style, mindset)",
        "coach_arch_name_ph": "Example: Gentle Dom, Cursed Artist...", "coach_arch_desc_ph": "Describe how the archetype should behave here..."
    },
    "中文": {
        "title": "⚖️ 社交动态沙盒 v4.10",
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
        "rate_warning_msg": "⏳ 注意：AI 调用频率限制，请勿发送过快。",
        "rate_error": "🚨 API 限制！请等待约 60 秒并重试。",
        "retry_btn": "🔄 重新发送",
        "coach_arch_name": "要分析的原型名称", "coach_arch_desc": "说明此原型的规则（简介、风格、心态）",
        "coach_arch_name_ph": "示例：温柔的统治者，被诅咒的艺术家...", "coach_arch_desc_ph": "在这里描述原型应该如何表现..."
    },
    "日本語": {
        "title": "⚖️ ソーシャルダイナミクス サンドボックス v4.10",
        "tab_sim": "🎮 シミュレーター", "tab_coach": "🧠 コーチルーム",
        "setup": "ゲームの設定:", "name_u": "あなたの名前", "sex_u": "👤 あなたの性別", "age": "🎂 あなたの年齢",
        "boy": "男性", "girl": "女性", "goth": "🦇 ゴスモード",
        "mode": "🎲 ゲームモード", "mode_gym": "🏋️ ジム (あなたがアーキタイプ)", "mode_exp": "🍷 体験 (チャットボットがアーキタイプを演じる)",
        "dyn": "🎯 ダイナミクス", "pursuer": "誘惑者 (あなたが追求する)", "desired": "懐疑的 (誘惑される)",
        "start": "🚀 ゲーム開始", "back_btn": "⬅️ 終了してリセット",
        "analyze_btn": "🫂 心理分析を依頼", "coach_title": "🕵️‍♂️ フレームアナライザー",
        "sex_p": "パートナーの性別 (チャットボット)", "prev": "⬅️ 戻る", "next": "次へ ➡️",
        "missing_img": "⚠️ 画像が見つかりません。名前とフォルダを確認してください。",
        "input_placeholder": "ここに入力...", "coach_desc": "実際のチャットをここに貼り付けてください...",
        "coach_btn": "フレームを分析",
        "offline": "📵 ユーザーはオフラインになりました。チャットは終了しました。",
        "slider_weird": "👽 奇妙な/カオス (%)", "slider_boring": "🥱 退屈/一言 (%)", "slider_enth": "🐶 熱狂的 (%)",
        "rate_warning_msg": "⏳ メモ: AI レート制限があります。速く送りすぎないでください。",
        "rate_error": "🚨 API 制限！60秒待って再試行してください。",
        "retry_btn": "🔄 再送信",
        "coach_arch_name": "分析するアーキタイプの名前", "coach_arch_desc": "このアーキタイプのルールを説明してください（バイオ、スタイル、考え方）",
        "coach_arch_name_ph": "例：ジェントル・ドム、呪われたアーティスト...", "coach_arch_desc_ph": "アーキタイプがどのように振る舞うべきかをここに記述してください..."
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
        "The Redpill": "💊 Cinico,

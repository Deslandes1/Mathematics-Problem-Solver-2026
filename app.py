import streamlit as st
import base64
import os
import tempfile
import re
from gtts import gTTS
from groq import Groq

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Math Solver",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- AUTHENTICATION ----------
PASSWORD = "20082010"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "language" not in st.session_state:
    st.session_state.language = "en"
if "exercise" not in st.session_state:
    st.session_state.exercise = ""
if "solution" not in st.session_state:
    st.session_state.solution = ""

def login():
    st.markdown(
        """
        <style>
        .login-box {
            max-width: 400px;
            margin: 10% auto;
            padding: 2.5rem;
            background: #1a5276;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(26, 82, 118, 0.5);
            text-align: center;
        }
        .login-box h2 {
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .login-box input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 40px;
            border: none;
            font-size: 1rem;
        }
        .login-box button {
            width: 100%;
            padding: 12px;
            background: #ffd700;
            border: none;
            border-radius: 40px;
            font-weight: bold;
            font-size: 1.1rem;
            cursor: pointer;
        }
        </style>
        <div class="login-box">
            <h2>🔐 AI Math Solver</h2>
            <p style="color: #ddd;">Enter the password to continue</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        pwd = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
        submitted = st.form_submit_button("Access")
        if submitted:
            if pwd == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

if not st.session_state.authenticated:
    login()

# ---------- LANGUAGE DICTIONARY ----------
LANG = {
    "en": {
        "title": "🧮 AI Math Solver",
        "subtitle": "Write any math exercise, and AI will solve it step by step with voice explanation.",
        "input_label": "📝 Type your math exercise here:",
        "resolve_btn": "✨ AI Resolve",
        "clear_btn": "🗑️ Clear",
        "solution_title": "📖 Step‑by‑Step Solution",
        "board_exercise": "📝 Exercise",
        "final_message": "This Mathematics Exercise resolved software was built by Gesner Deslandes, Engineer in Chief at GlobalInternet.py.",
        "error_api": "Groq API key not set. Please add GROQ_API_KEY in secrets.",
        "error_empty": "Please type a math exercise first."
    },
    "fr": {
        "title": "🧮 Solveur Mathématique IA",
        "subtitle": "Écrivez n'importe quel exercice de maths, l'IA le résoudra étape par étape avec explication vocale.",
        "input_label": "📝 Tapez votre exercice de maths ici :",
        "resolve_btn": "✨ Résoudre avec IA",
        "clear_btn": "🗑️ Effacer",
        "solution_title": "📖 Solution étape par étape",
        "board_exercise": "📝 Exercice",
        "final_message": "Ce logiciel de résolution d'exercices mathématiques a été construit par Gesner Deslandes, Ingénieur en chef chez GlobalInternet.py.",
        "error_api": "Clé API Groq non définie. Ajoutez GROQ_API_KEY dans les secrets.",
        "error_empty": "Veuillez d'abord taper un exercice de maths."
    },
    "es": {
        "title": "🧮 Solucionador Matemático IA",
        "subtitle": "Escribe cualquier ejercicio de matemáticas, la IA lo resolverá paso a paso con explicación de voz.",
        "input_label": "📝 Escribe tu ejercicio de matemáticas aquí:",
        "resolve_btn": "✨ Resolver con IA",
        "clear_btn": "🗑️ Borrar",
        "solution_title": "📖 Solución paso a paso",
        "board_exercise": "📝 Ejercicio",
        "final_message": "Este software de resolución de ejercicios matemáticos fue construido por Gesner Deslandes, Ingeniero Jefe en GlobalInternet.py.",
        "error_api": "Clave API de Groq no configurada. Agrega GROQ_API_KEY en los secretos.",
        "error_empty": "Primero escribe un ejercicio de matemáticas."
    }
}

def t(key):
    return LANG[st.session_state.language].get(key, key)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:10px;">
            <img src="https://github.com/Deslandes1/DocumentAIFillOut-2026/blob/main/Gesner%20Deslandes%202026.png?raw=true" 
                 style="width:120px; height:120px; border-radius:50%; object-fit:cover; border:3px solid #1a5276; margin-bottom:5px;">
            <h3 style="color:#1a5276; margin:0;">Gesner Deslandes</h3>
            <p style="color:#2c3e50; font-weight:bold; margin:0;">Engineer in Chief</p>
            <hr style="border-color:#1a5276;">
            <p style="font-size:0.9rem;">💼 Built by <b>Gesner Deslandes</b><br>Engineer in Chief at GlobalInternet.py</p>
            <p style="font-size:0.85rem;">📞 (509) 4738-5663<br>✉️ deslandes78@gmail.com</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    lang_choice = st.selectbox(
        "🌐 Language",
        options=["en", "fr", "es"],
        format_func=lambda x: {"en": "English", "fr": "Français", "es": "Español"}[x],
        index=["en", "fr", "es"].index(st.session_state.language)
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

    st.divider()
    st.caption("🔊 Voice explanation uses Google TTS")
    st.caption("🤖 Powered by Groq (Llama 3.1)")

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    .stApp {
        background: #d4e6f1; /* light blue */
    }
    .board {
        background: #2e7d32;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border: 4px solid #1b5e20;
        color: #ffffff;
        font-size: 1.3rem;
        font-family: 'Courier New', monospace;
        min-height: 120px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .board h3 {
        color: #ffd700;
        margin-top: 0;
    }
    .solution-box {
        background: #1b5e20;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: #ffffff;
        font-size: 1.1rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        border-left: 8px solid #ffd700;
    }
    .stTextArea textarea {
        border: 2px solid #1a5276 !important;
        border-radius: 20px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    .stButton>button {
        background-color: #1a5276;
        color: white;
        border-radius: 40px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2471a3;
        transform: scale(1.02);
        box-shadow: 0 8px 20px rgba(26, 82, 118, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- MAIN PAGE ----------
st.title(t("title"))
st.caption(t("subtitle"))

# Input area
exercise = st.text_area(t("input_label"), height=120, value=st.session_state.exercise, key="exercise_input")

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button(t("resolve_btn"), use_container_width=True):
        if not exercise.strip():
            st.warning(t("error_empty"))
        else:
            # Call Groq AI
            api_key = st.secrets.get("GROQ_API_KEY")
            if not api_key:
                st.error(t("error_api"))
            else:
                with st.spinner("🧠 AI is thinking..."):
                    client = Groq(api_key=api_key)
                    lang = st.session_state.language
                    system_prompt = {
                        "en": "You are a math tutor. Solve the exercise step by step in a clear, friendly manner. Break it down into logical steps and show the final answer. Use plain text.",
                        "fr": "Vous êtes un professeur de mathématiques. Résolvez l'exercice étape par étape de manière claire et amicale. Décomposez en étapes logiques et montrez la réponse finale. Utilisez du texte simple.",
                        "es": "Eres un tutor de matemáticas. Resuelve el ejercicio paso a paso de manera clara y amigable. Desglosa en pasos lógicos y muestra la respuesta final. Usa texto simple."
                    }[lang]
                    prompt = f"{system_prompt}\n\nExercise: {exercise}\n\nSolution:"
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=1024
                        )
                        solution_text = response.choices[0].message.content
                        st.session_state.solution = solution_text
                        st.session_state.exercise = exercise
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI error: {e}")

with col2:
    if st.button(t("clear_btn"), use_container_width=True):
        st.session_state.exercise = ""
        st.session_state.solution = ""
        st.rerun()

# Display exercise on board
st.markdown("---")
st.subheader(t("board_exercise"))
st.markdown(f'<div class="board">{exercise if exercise else "📝 Your exercise will appear here..."}</div>', unsafe_allow_html=True)

# Display solution
if st.session_state.solution:
    st.subheader(t("solution_title"))
    st.markdown(f'<div class="solution-box">{st.session_state.solution}</div>', unsafe_allow_html=True)

    # Voice explanation
    if st.button("🔊 Listen to Explanation", key="voice_btn"):
        with st.spinner("🔊 Generating voice..."):
            # Combine solution + final message
            final_msg = t("final_message")
            full_text = f"{st.session_state.solution}\n\n{final_msg}"
            lang_code = st.session_state.language
            try:
                tts = gTTS(text=full_text, lang=lang_code, slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts.save(tmp.name)
                    audio_path = tmp.name
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                os.unlink(audio_path)
                st.success("▶️ Audio playing...")
            except Exception as e:
                st.error(f"TTS error: {e}")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("© 2026 GlobalInternet.py | Built with ❤️ by Gesner Deslandes")

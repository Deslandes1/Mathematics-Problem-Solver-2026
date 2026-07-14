import streamlit as st
import base64
import os
import tempfile
import re
from gtts import gTTS
from groq import Groq

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Subject Solver",
    page_icon="🧠",
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
if "clean_steps" not in st.session_state:
    st.session_state.clean_steps = ""
if "subject" not in st.session_state:
    st.session_state.subject = "Math"

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
            <h2>🔐 AI Subject Solver</h2>
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
        "title_math": "🧮 AI Math Solver",
        "title_physics": "⚛️ AI Physics Solver",
        "title_chemistry": "🧪 AI Chemistry Solver",
        "title_english": "📝 AI English Solver",
        "subtitle": "Select a subject, enter your problem, and AI will solve it with explanation.",
        "input_label_math": "📝 Type your math exercise here:",
        "input_label_physics": "⚛️ Type your physics problem here:",
        "input_label_chemistry": "🧪 Type your chemistry question here:",
        "input_label_english": "📝 Type your English test request here:",
        "resolve_btn": "✨ Solve",
        "clear_btn": "🗑️ Clear",
        "solution_title": "📖 Detailed Solution",
        "clean_steps_title": "📋 Step‑by‑Step (numbered)",
        "board_exercise": "📝 Problem",
        "final_message": "This software was built by Gesner Deslandes, Engineer in Chief at GlobalInternet.py.",
        "error_api": "Groq API key not set. Please add GROQ_API_KEY in secrets.",
        "error_empty": "Please type a problem first.",
        "examples_math": "Try: 3x + 7 = 22",
        "examples_physics": "Try: A car accelerates from rest at 2 m/s² for 5 seconds. How far does it travel?",
        "examples_chemistry": "Try: Balance the equation: Fe + O₂ → Fe₂O₃",
        "examples_english": "Try: Generate a grammar test with 5 questions on tenses."
    },
    "fr": {
        "title_math": "🧮 Solveur Mathématique IA",
        "title_physics": "⚛️ Solveur Physique IA",
        "title_chemistry": "🧪 Solveur Chimie IA",
        "title_english": "📝 Solveur Anglais IA",
        "subtitle": "Choisissez une matière, entrez votre problème, et l'IA le résoudra avec explication.",
        "input_label_math": "📝 Tapez votre exercice de maths ici :",
        "input_label_physics": "⚛️ Tapez votre problème de physique ici :",
        "input_label_chemistry": "🧪 Tapez votre question de chimie ici :",
        "input_label_english": "📝 Tapez votre demande de test d'anglais ici :",
        "resolve_btn": "✨ Résoudre",
        "clear_btn": "🗑️ Effacer",
        "solution_title": "📖 Solution détaillée",
        "clean_steps_title": "📋 Étapes numérotées",
        "board_exercise": "📝 Problème",
        "final_message": "Ce logiciel a été construit par Gesner Deslandes, Ingénieur en chef chez GlobalInternet.py.",
        "error_api": "Clé API Groq non définie. Ajoutez GROQ_API_KEY dans les secrets.",
        "error_empty": "Veuillez d'abord taper un problème.",
        "examples_math": "Essayez : 3x + 7 = 22",
        "examples_physics": "Essayez : Une voiture accélère de 0 à 2 m/s² pendant 5 secondes. Quelle distance parcourt-elle ?",
        "examples_chemistry": "Essayez : Équilibrer l'équation : Fe + O₂ → Fe₂O₃",
        "examples_english": "Essayez : Générez un test de grammaire avec 5 questions sur les temps."
    },
    "es": {
        "title_math": "🧮 Solucionador Matemático IA",
        "title_physics": "⚛️ Solucionador Física IA",
        "title_chemistry": "🧪 Solucionador Química IA",
        "title_english": "📝 Solucionador Inglés IA",
        "subtitle": "Selecciona una materia, ingresa tu problema, y la IA lo resolverá con explicación.",
        "input_label_math": "📝 Escribe tu ejercicio de matemáticas aquí:",
        "input_label_physics": "⚛️ Escribe tu problema de física aquí:",
        "input_label_chemistry": "🧪 Escribe tu pregunta de química aquí:",
        "input_label_english": "📝 Escribe tu solicitud de prueba de inglés aquí:",
        "resolve_btn": "✨ Resolver",
        "clear_btn": "🗑️ Borrar",
        "solution_title": "📖 Solución detallada",
        "clean_steps_title": "📋 Pasos numerados",
        "board_exercise": "📝 Problema",
        "final_message": "Este software fue construido por Gesner Deslandes, Ingeniero Jefe en GlobalInternet.py.",
        "error_api": "Clave API de Groq no configurada. Agrega GROQ_API_KEY en los secretos.",
        "error_empty": "Primero escribe un problema.",
        "examples_math": "Prueba: 3x + 7 = 22",
        "examples_physics": "Prueba: Un coche acelera desde el reposo a 2 m/s² durante 5 segundos. ¿Qué distancia recorre?",
        "examples_chemistry": "Prueba: Balancea la ecuación: Fe + O₂ → Fe₂O₃",
        "examples_english": "Prueba: Genera un test de gramática con 5 preguntas sobre tiempos verbales."
    }
}

def t(key):
    return LANG[st.session_state.language].get(key, key)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:10px;">
            <img src="https://raw.githubusercontent.com/Deslandes1/Mathematics-Problem-Solver-2026/main/Gesner%20Deslandes.JPG" 
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
        background: #d4e6f1;
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
    .clean-steps-box {
        background: #1b5e20;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: #ffffff;
        font-size: 1.1rem;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        word-wrap: break-word;
        border-left: 8px solid #00ff88;
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
    .example-btn button {
        background-color: #2e86c1;
        font-size: 0.8rem;
        padding: 0.2rem 1rem;
    }
    .example-btn button:hover {
        background-color: #1a5276;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SUBJECT SELECTION (TABS) ----------
subject_tabs = ["🧮 Math", "⚛️ Physics", "🧪 Chemistry", "📝 English"]
subject_map = {0: "Math", 1: "Physics", 2: "Chemistry", 3: "English"}
tabs = st.tabs(subject_tabs)

# Loop through tabs – set subject when tab is clicked, but do NOT call st.rerun()
for i, tab in enumerate(tabs):
    with tab:
        if st.session_state.subject != subject_map[i]:
            st.session_state.subject = subject_map[i]
            # Clear previous results when switching subject
            st.session_state.exercise = ""
            st.session_state.solution = ""
            st.session_state.clean_steps = ""
            # No st.rerun() – the page will naturally update

# ---------- GET CURRENT SUBJECT ----------
subject = st.session_state.subject

# ---------- DYNAMIC TITLE ----------
subject_title_key = {
    "Math": "title_math",
    "Physics": "title_physics",
    "Chemistry": "title_chemistry",
    "English": "title_english"
}
st.title(t(subject_title_key[subject]))
st.caption(t("subtitle"))

# ---------- INPUT LABEL & EXAMPLES ----------
input_label_key = {
    "Math": "input_label_math",
    "Physics": "input_label_physics",
    "Chemistry": "input_label_chemistry",
    "English": "input_label_english"
}[subject]
examples_key = {
    "Math": "examples_math",
    "Physics": "examples_physics",
    "Chemistry": "examples_chemistry",
    "English": "examples_english"
}[subject]

exercise = st.text_area(t(input_label_key), height=120, value=st.session_state.exercise, key="exercise_input")

# Example button and hint
col_ex1, col_ex2 = st.columns(2)
with col_ex1:
    if st.button(f"📌 Load Example", key="example_btn"):
        example_map = {
            "Math": "3x + 7 = 22",
            "Physics": "A car accelerates from rest at 2 m/s² for 5 seconds. How far does it travel?",
            "Chemistry": "Balance the equation: Fe + O₂ → Fe₂O₃",
            "English": "Generate a grammar test with 5 questions on tenses."
        }
        st.session_state.exercise = example_map[subject]
        st.session_state.solution = ""
        st.session_state.clean_steps = ""
        st.rerun()
with col_ex2:
    st.caption(f"💡 {t(examples_key)}")

# ---------- BUTTONS ----------
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button(t("resolve_btn"), use_container_width=True):
        if not exercise.strip():
            st.warning(t("error_empty"))
        else:
            api_key = st.secrets.get("GROQ_API_KEY")
            if not api_key:
                st.error(t("error_api"))
            else:
                with st.spinner("🧠 AI is thinking..."):
                    client = Groq(api_key=api_key)
                    lang = st.session_state.language
                    # Build system prompt based on subject
                    system_prompt = {
                        "Math": {
                            "en": """You are a math tutor. Solve the exercise step by step.
                            Provide two sections:
                            1. Detailed explanation with friendly text.
                            2. Clean numbered steps with only equations and operations, no extra words, each step on a new line starting with the step number.

                            Format:
                            ---EXPLANATION---
                            [detailed explanation]
                            ---CLEAN_STEPS---
                            1. [equation/operation]
                            2. [equation/operation]
                            ...
                            Final answer: [answer]
                            """,
                            "fr": """Vous êtes un professeur de mathématiques. Résolvez l'exercice étape par étape.
                            Fournissez deux sections :
                            1. Explication détaillée avec texte amical.
                            2. Étapes claires numérotées avec uniquement les équations et opérations, sans mots supplémentaires, chaque étape sur une nouvelle ligne commençant par le numéro.

                            Format :
                            ---EXPLANATION---
                            [explication détaillée]
                            ---CLEAN_STEPS---
                            1. [équation/opération]
                            2. [équation/opération]
                            ...
                            Réponse finale : [réponse]
                            """,
                            "es": """Eres un tutor de matemáticas. Resuelve el ejercicio paso a paso.
                            Proporciona dos secciones:
                            1. Explicación detallada con texto amigable.
                            2. Pasos claros numerados con solo ecuaciones y operaciones, sin palabras adicionales, cada paso en una nueva línea comenzando con el número.

                            Formato:
                            ---EXPLANATION---
                            [explicación detallada]
                            ---CLEAN_STEPS---
                            1. [ecuación/operación]
                            2. [ecuación/operación]
                            ...
                            Respuesta final: [respuesta]
                            """
                        },
                        "Physics": {
                            "en": """You are a physics tutor. Solve the physics problem step by step.
                            Provide two sections:
                            1. Detailed explanation with formulas and reasoning.
                            2. Clean numbered steps with only equations and final result.

                            Format:
                            ---EXPLANATION---
                            [detailed explanation]
                            ---CLEAN_STEPS---
                            1. [equation/operation]
                            2. [equation/operation]
                            ...
                            Final answer: [answer]
                            """,
                            "fr": """Vous êtes un professeur de physique. Résolvez le problème de physique étape par étape.
                            Fournissez deux sections :
                            1. Explication détaillée avec formules et raisonnement.
                            2. Étapes claires numérotées avec uniquement les équations et le résultat final.

                            Format :
                            ---EXPLANATION---
                            [explication détaillée]
                            ---CLEAN_STEPS---
                            1. [équation/opération]
                            2. [équation/opération]
                            ...
                            Réponse finale : [réponse]
                            """,
                            "es": """Eres un tutor de física. Resuelve el problema de física paso a paso.
                            Proporciona dos secciones:
                            1. Explicación detallada con fórmulas y razonamiento.
                            2. Pasos claros numerados con solo ecuaciones y resultado final.

                            Formato:
                            ---EXPLANATION---
                            [explicación detallada]
                            ---CLEAN_STEPS---
                            1. [ecuación/operación]
                            2. [ecuación/operación]
                            ...
                            Respuesta final: [respuesta]
                            """
                        },
                        "Chemistry": {
                            "en": """You are a chemistry tutor. Solve the chemistry problem step by step.
                            Provide two sections:
                            1. Detailed explanation with chemical equations and reasoning.
                            2. Clean numbered steps with only equations and final result.

                            Format:
                            ---EXPLANATION---
                            [detailed explanation]
                            ---CLEAN_STEPS---
                            1. [equation/operation]
                            2. [equation/operation]
                            ...
                            Final answer: [answer]
                            """,
                            "fr": """Vous êtes un professeur de chimie. Résolvez le problème de chimie étape par étape.
                            Fournissez deux sections :
                            1. Explication détaillée avec équations chimiques et raisonnement.
                            2. Étapes claires numérotées avec uniquement les équations et le résultat final.

                            Format :
                            ---EXPLANATION---
                            [explication détaillée]
                            ---CLEAN_STEPS---
                            1. [équation/opération]
                            2. [équation/opération]
                            ...
                            Réponse finale : [réponse]
                            """,
                            "es": """Eres un tutor de química. Resuelve el problema de química paso a paso.
                            Proporciona dos secciones:
                            1. Explicación detallada con ecuaciones químicas y razonamiento.
                            2. Pasos claros numerados con solo ecuaciones y resultado final.

                            Formato:
                            ---EXPLANATION---
                            [explicación detallada]
                            ---CLEAN_STEPS---
                            1. [ecuación/operación]
                            2. [ecuación/operación]
                            ...
                            Respuesta final: [respuesta]
                            """
                        },
                        "English": {
                            "en": """You are an English tutor. Generate a test or answer a question about English grammar, vocabulary, or reading comprehension.
                            Provide two sections:
                            1. Detailed explanation of the answer or the test content with answers.
                            2. Clean list of answers or steps (numbered).

                            Format:
                            ---EXPLANATION---
                            [detailed explanation]
                            ---CLEAN_STEPS---
                            1. [answer 1]
                            2. [answer 2]
                            ...
                            Final summary: [summary]
                            """,
                            "fr": """Vous êtes un professeur d'anglais. Générez un test ou répondez à une question sur la grammaire, le vocabulaire ou la compréhension de lecture.
                            Fournissez deux sections :
                            1. Explication détaillée de la réponse ou du contenu du test avec réponses.
                            2. Liste claire des réponses ou étapes (numérotées).

                            Format :
                            ---EXPLANATION---
                            [explication détaillée]
                            ---CLEAN_STEPS---
                            1. [réponse 1]
                            2. [réponse 2]
                            ...
                            Résumé final : [résumé]
                            """,
                            "es": """Eres un tutor de inglés. Genera un test o responde a una pregunta sobre gramática, vocabulario o comprensión de lectura.
                            Proporciona dos secciones:
                            1. Explicación detallada de la respuesta o del contenido del test con respuestas.
                            2. Lista clara de respuestas o pasos (numerados).

                            Formato:
                            ---EXPLANATION---
                            [explicación detallada]
                            ---CLEAN_STEPS---
                            1. [respuesta 1]
                            2. [respuesta 2]
                            ...
                            Resumen final: [resumen]
                            """
                        }
                    }[subject][lang]

                    prompt = f"{system_prompt}\n\nProblem: {exercise}\n\nSolution:"
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=1024
                        )
                        full_response = response.choices[0].message.content

                        explanation = ""
                        clean_steps = ""
                        if "---EXPLANATION---" in full_response and "---CLEAN_STEPS---" in full_response:
                            parts = full_response.split("---CLEAN_STEPS---")
                            explanation_part = parts[0].replace("---EXPLANATION---", "").strip()
                            clean_part = parts[1].strip()
                            explanation = explanation_part
                            clean_steps = clean_part
                        else:
                            explanation = full_response
                            lines = full_response.split('\n')
                            step_lines = []
                            for line in lines:
                                if re.match(r'^\d+\.', line.strip()):
                                    step_lines.append(line.strip())
                            if step_lines:
                                clean_steps = "\n".join(step_lines)
                            else:
                                clean_steps = "No clean steps extracted."

                        st.session_state.solution = explanation
                        st.session_state.clean_steps = clean_steps
                        st.session_state.exercise = exercise
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI error: {e}")

with col2:
    if st.button(t("clear_btn"), use_container_width=True):
        st.session_state.exercise = ""
        st.session_state.solution = ""
        st.session_state.clean_steps = ""
        st.rerun()

# ---------- DISPLAY BOARD ----------
st.markdown("---")
st.subheader(t("board_exercise"))
st.markdown(f'<div class="board">{exercise if exercise else "📝 Your problem will appear here..."}</div>', unsafe_allow_html=True)

# ---------- DISPLAY SOLUTION ----------
if st.session_state.solution:
    st.subheader(t("solution_title"))
    st.markdown(f'<div class="solution-box">{st.session_state.solution}</div>', unsafe_allow_html=True)

    if st.session_state.clean_steps and st.session_state.clean_steps != "No clean steps extracted.":
        st.subheader(t("clean_steps_title"))
        st.markdown(f'<div class="clean-steps-box">{st.session_state.clean_steps}</div>', unsafe_allow_html=True)

    if st.button("🔊 Listen to Explanation", key="voice_btn"):
        with st.spinner("🔊 Generating voice..."):
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

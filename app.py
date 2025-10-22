import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64
import random

# ========== CONFIGURACIÓN ==========
st.set_page_config(page_title="Cuentos & Audio", page_icon="📖", layout="centered")

# Para almacenar el cuento actual
if "cuento_actual" not in st.session_state:
    st.session_state["cuento_actual"] = ""

# ========== ESTILOS ==========
st.markdown("""
<style>

body {
    background: #0f0f17;
}

.main {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 15px;
    backdrop-filter: blur(8px);
}

/* PORTADA */
.img-portada img {
    border-radius: 18px;
    box-shadow: 0 0 25px rgba(80,80,255,0.4);
}

/* BOTONES */
.stButton>button {
    background: linear-gradient(135deg, #2b2b52, #5a4fa3);
    color: #ffffff;
    font-weight: 600;
    font-size: 16px;
    border-radius: 12px;
    padding: 12px 25px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0px 4px 12px rgba(0,0,0,0.35);
    transition: 0.3s ease-in-out;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #3b3b70, #6c5fd1);
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0px 6px 18px rgba(0,0,0,0.45);
}

</style>
""", unsafe_allow_html=True)

# ========== PORTADA ==========
portada = Image.open("portada.png")
st.markdown('<div class="img-portada">', unsafe_allow_html=True)
st.image(portada, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.title("Cuentos & Conversión a Audio")

# ========== CUENTOS ==========
cuentos = [
    """La niña del faro

Cada noche, Ela encendía el faro junto al mar. No lo hacía por obligación, sino por promesa. Su padre, un viejo navegante, le había dicho antes de desaparecer entre tormentas: 
«Mientras la luz siga encendida, siempre sabré volver».

Años pasaron. Algunos en el pueblo pensaban que era inútil, que no volvería nadie. Pero Ela jamás falló.

Una noche silenciosa, con el mar en calma, una campana sonó a lo lejos. Ela corrió a la orilla, y entre la bruma vio una vieja embarcación acercándose, guiada por la luz del faro.

—Te lo prometí —susurró.

Nunca dejó de creer."""
,
    """La hoja que no quería caer

Había una hoja pequeña en un gran roble. Todas sus hermanas caían con el viento del otoño, pero ella tenía miedo. «¿Y si caer duele?» se preguntaba.

Un día, el viento la abrazó y le dijo: «No temas. Caer no es el final. Es el comienzo de tu viaje».

La hoja decidió soltarse. Y mientras descendía, descubrió que no caía… volaba."""
]

st.subheader("Generar cuento aleatorio")
if st.button("Nuevo cuento"):
    st.session_state["cuento_actual"] = random.choice(cuentos)
    st.write(st.session_state["cuento_actual"])

# ========== CONVERTIR CUENTO A AUDIO ==========
st.subheader("Convertir cuento actual a audio")

def text_to_speech(text, lg):
    tts = gTTS(text, lang=lg)
    tts.save("temp/audio.mp3")
    return "temp/audio.mp3"

idioma_cuento = "es"  # El cuento siempre será en español

if st.button("Convertir cuento en audio"):
    if st.session_state["cuento_actual"].strip() == "":
        st.error("Primero genera un cuento antes de convertirlo.")
    else:
        try:
            os.mkdir("temp")
        except:
            pass

        audio_path = text_to_speech(st.session_state["cuento_actual"], idioma_cuento)
        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")

        b64 = base64.b64encode(audio_bytes).decode()
        href = f'<a href="data:file/mp3;base64,{b64}" download="cuento.mp3">Descargar audio del cuento</a>'
        st.markdown(href, unsafe_allow_html=True)

# ========== CONVERTIR TEXTO LIBRE A AUDIO ==========
st.subheader("Convertir texto a audio")

text = st.text_area("Escribe o pega el texto que deseas convertir a audio:")

idioma = st.selectbox("Selecciona el idioma del audio", ("Español", "English"))
lg = "es" if idioma == "Español" else "en"

if st.button("Convertir texto a audio"):
    if text.strip() == "":
        st.error("Por favor, escribe un texto antes de convertir.")
    else:
        audio_path = text_to_speech(text, lg)
        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
        b64 = base64.b64encode(audio_bytes).decode()
        href = f'<a href="data:file/mp3;base64,{b64}" download="audio.mp3">Descargar audio</a>'
        st.markdown(href, unsafe_allow_html=True)

# ========= LIMPIEZA ==========
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            os.remove(f)

remove_files(7)

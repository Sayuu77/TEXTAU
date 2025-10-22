import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64
import io
import random

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Texto → Audio • Aesthetic", page_icon="🎧", layout="centered")

# -------------------- CSS & BACKGROUND --------------------
# Usa images/clouds.png si existe; si no, cae en un gradiente lila–celeste
clouds_path = "images/clouds.png"
bg_css = ""
if os.path.exists(clouds_path):
    # usa la imagen clouds como fondo (cover)
    bg_css = f"""
    <style>
      body {{
        background-image: url('{clouds_path}');
        background-size: cover;
        background-attachment: fixed;
      }}
      .stApp > .main {{ background-color: rgba(255,255,255,0.6); border-radius: 14px; padding: 18px; }}
    </style>
    """
else:
    bg_css = """
    <style>
      body { background: linear-gradient(180deg, #F5E9FF, #E8F8FF); }
      .stApp > .main { background-color: rgba(255,255,255,0.7); border-radius: 14px; padding: 18px; }
    </style>
    """

st.markdown(bg_css, unsafe_allow_html=True)

# -------------------- HEADER / IMAGEN --------------------
st.title("🎧 Conversión de Texto a Audio — Soft Aesthetic")
# mostrar la imagen del gato/ratón si existe
if os.path.exists("gato_raton.png"):
    img = Image.open("gato_raton.png")
    st.image(img, width=320)
else:
    st.markdown("*(Coloca `gato_raton.png` en la carpeta del proyecto para ver la imagen)*")

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("Instrucciones")
    st.write("""
    1. Pega o escribe texto en el área principal.  
    2. Selecciona idioma.  
    3. Presiona **Convertir a Audio**.  
    4. Descarga el MP3 si lo deseas.  
    """)
    st.markdown("---")
    st.write("Si quieres música de fondo coloca `musica.mp3` en la carpeta del proyecto.")

# -------------------- REEMPLAZO: CUENTO JUDE & CARDAN --------------------
st.subheader("📖 Una historia corta — Jude & Cardan")

cuento_jude_cardan = (
    "El patio del palacio estaba frío, pero las flores encantadas proyectaban un brillo "
    "que parecía burlarse de la noche. Jude caminó sin ceremonias, la armadura de quien "
    "aprendió a no pedir nada. Cardan apareció en el borde de la fuente, con la sonrisa "
    "que tanto la irritaba y, en ocasiones, la dejaba sin aliento.\n\n"
    "—Nunca eres sencilla, ¿sabes? —dijo él con voz baja—. Insistes en convertir todo en combate.\n\n"
    "Jude clavó la mirada. —Y tú insistes en hacer del mundo una broma hilarante. ¿Qué quieres ahora?\n\n"
    "Cardan se acercó, las manos en los bolsillos, incómodo y exacto a la vez.\n\n"
    "—Quiero que dejes de mirarme como si fuera un rival. Me cansas, Jude. Me haces sentir demasiado.\n\n"
    "Ella casi rió. El borde de la risa se vio y lo rechazó por mil motivos prácticos: orgullo, estrategia.\n\n"
    "—¿Sentir demasiado? Qué original. ¿Vas a llorar ahora, príncipe?\n\n"
    "Por primera vez en muchas noches, él no devolvió el insulto. En vez de eso, tomó su mano con una "
    "manera torpe que parecía importarle más que su orgullo.\n\n"
    "—No sé qué harás conmigo —murmuró—. No sé si serás fuego o refugio. Solo sé que no quiero que te vayas.\n\n"
    "Jude apretó los dedos, no por debilidad, sino para recordar que aún podía decidir. Sus labios se curvaron "
    "en algo que no era sonrisa, pero casi.\n\n"
    "—Entonces no me falles —dijo—. No porque te importe el corazón que tienes, sino porque no lo soportaré si me traicionas.\n\n"
    "Cardan la miró largo, y el silencio del jardín llenó lo que las palabras no dijeron. Allí, entre orgullo y ternura, "
    "se quedaron, juntos por una decisión que ninguno nombraría todavía."
)

st.write(cuento_jude_cardan)

# -------------------- MÚSICA DE FONDO (LOOP) --------------------
# Si existe musica.mp3, intentamos reproducirla en loop. Nota: algunos navegadores bloquean autoplay.
if os.path.exists("musica.mp3"):
    try:
        with open("musica.mp3", "rb") as mf:
            music_bytes = mf.read()
        # mostramos un control para que el usuario lo pause si quiere
        st.audio(music_bytes, format="audio/mp3", start_time=0)
        # Intento extra: insertar un elemento <audio> con autoplay & loop (puede ser bloqueado por el navegador)
        audio_html = """
        <audio autoplay loop>
          <source src="musica.mp3" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        st.info("Música de fondo activada (loop). Si no suena automáticamente, presiona el botón de reproducir.")
    except Exception as e:
        st.warning("No se pudo cargar musica.mp3 automáticamente. Asegúrate de que el archivo exista y sea MP3.")
else:
    st.info("Coloca `musica.mp3` en la carpeta del proyecto para activar la música de fondo en loop.")

# -------------------- ÁREA DE TEXTO A CONVERTIR --------------------
st.markdown("---")
st.markdown("### ✏️ Escribe o pega el texto que quieres escuchar")
text = st.text_area("Texto a convertir", height=180)

option_lang = st.selectbox("Selecciona el idioma", ("Español", "English"))
lg = 'es' if option_lang == "Español" else 'en'

# -------------------- FUNCIONES TTS Y DESCARGA --------------------
try:
    os.makedirs("temp", exist_ok=True)
except Exception:
    pass

def text_to_speech(text, lg):
    if not text or not text.strip():
        return None, "No hay texto"
    try:
        tts = gTTS(text, lang=lg)
        safe_name = "".join(c for c in text[:20] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
        filename = f"{safe_name or 'audio'}.mp3"
        path = os.path.join("temp", filename)
        tts.save(path)
        return path, text
    except Exception as e:
        return None, str(e)

def get_download_link(file_path, label="Descargar audio"):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
    return href

# -------------------- BOTÓN CONVERSIÓN --------------------
if st.button("✨ Convertir a Audio"):
    if not text.strip():
        st.warning("Por favor escribe o pega el texto que quieres convertir.")
    else:
        path, out = text_to_speech(text, lg)
        if path:
            st.success("Audio generado ✅")
            # reproducir en la app
            with open(path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
            # mostrar enlace de descarga
            st.markdown(get_download_link(path, label="📥 Descargar audio generado"), unsafe_allow_html=True)
        else:
            st.error(f"Error al generar audio: {out}")

# -------------------- LIMPIEZA DE ARCHIVOS ANTIGUOS --------------------
def cleanup_temp(days=7):
    files = glob.glob("temp/*.mp3")
    now = time.time()
    cutoff = now - days * 86400
    for f in files:
        try:
            if os.path.getmtime(f) < cutoff:
                os.remove(f)
        except Exception:
            pass

cleanup_temp(7)

# -------------------- FOOTER --------------------
st.markdown("---")
footer_options = [
    "Un día a la vez 🤍",
    "No te sueltes.",
    "También mereces cosas bonitas."
]
st.caption(random.choice(footer_options))

# -------------------- RECUERDOS / AYUDA --------------------
st.info("Si necesitas que te mande un enlace para descargar música libre de derechos (suave, lo-fi / instrumental), dime y te lo comparto.")

# app.py
import streamlit as st
import os
import time
import glob
import base64
import io
import random
from gtts import gTTS

# -------------------- CONFIG --------------------
st.set_page_config(page_icon="🌌", layout="centered")

# -------------------- ESTILO NEO-GLASS --------------------
st.markdown("""
    <style>
    body {
      background: linear-gradient(180deg, rgba(8,6,23,0.94), rgba(18,10,40,0.96));
      color: #EAEAF6;
      font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .stApp > .main {
      background: rgba(255,255,255,0.03);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.04);
      box-shadow: 0 10px 30px rgba(1,4,20,0.6);
      border-radius: 14px;
      padding: 22px;
    }
    .header { display:flex; align-items:center; gap:16px; }
    .glass-btn {
      background: linear-gradient(90deg, rgba(140,100,255,0.14), rgba(90,130,255,0.10));
      color: #F6F7FF;
      border: 1px solid rgba(255,255,255,0.06);
      padding: 8px 14px;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
    }
    textarea { background: rgba(255,255,255,0.02); color: #F1F1FF; }
    .small-note { color: #cfcff6; font-size: 13px; }
    a { color: #C7B3FF; }
    .muted { color: #bfbfe6 }
    </style>
""", unsafe_allow_html=True)

# -------------------- BACKGROUND OVERLAY (opcional clouds) --------------------
if os.path.exists("images/clouds.png"):
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('images/clouds.png');
            background-size: cover;
            background-attachment: fixed;
            background-blend-mode: overlay;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# -------------------- HEADER --------------------
col1, col2 = st.columns([1,4])
with col1:
    if os.path.exists("portada.png"):
        try:
            from PIL import Image
            port = Image.open("portada.png")
            st.image(port, width=110)
        except Exception:
            pass
with col2:
    st.markdown("<div class='header'><h1 style='margin:0'>🌌 Cuentos & Audio</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='small-note'>Neo-Glass • Lo-fi lluvia (autoplay) • Cuentos en español</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- MÚSICA AUTOPLAY (LO-FI LLUVIA) --------------------
# Coloca 'music.mp3' en la carpeta para activar sonido. Técnica: audio autoplay muted -> script intenta unmute + fade-in.
if os.path.exists("music.mp3"):
    audio_html = """
    <audio id="bg_audio" autoplay loop muted>
      <source src="music.mp3" type="audio/mpeg">
      Your browser does not support the audio element.
    </audio>
    <script>
      (function() {
        const a = document.getElementById('bg_audio');
        if (!a) return;
        a.volume = 0.0;
        // small timeout to help browsers accept autoplay if initially muted
        setTimeout(() => {
          try {
            a.muted = false;
            let vol = 0.0;
            const target = 0.15; // volumen objetivo suave
            const step = 0.01;
            const interval = setInterval(() => {
              vol = Math.min(vol + step, target);
              a.volume = vol;
              if (vol >= target) clearInterval(interval);
            }, 80);
          } catch (e) {
            console.log('Autoplay unmute blocked', e);
          }
        }, 500);
      })();
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    # fallback visible control
    try:
        with open("music.mp3", "rb") as mf:
            st.audio(mf.read(), format="audio/mp3", start_time=0)
    except Exception:
        st.info("Música detectada pero no se pudo cargar el control nativo.")
else:
    st.info("Para tener música de fondo automática, coloca 'music.mp3' (lo-fi lluvia) en la carpeta del proyecto.")

st.markdown("---")

# -------------------- CUENTOS EN ESPAÑOL (LOCALES / FÁCILES) --------------------
# Usamos por defecto cuentos originales en español (limpios) para garantizar que siempre sean adecuados.
ORIGINAL_SPANISH_STORIES = [
    "La luna rompió el silencio del pueblo. Marta encontró una carta bajo la puerta que no esperaba. En ella había una sola frase: 'Vuelve cuando te falte el corazón'. Fue suficiente para que entendiera que algunas ausencias no eran olvido, sino invitación.",
    "En la estación, el tren llegó tarde. Un niño soltó su cometa y la rueda de la fortuna del parque se quedó pensando. Ella lo ayudó a recuperar el hilo; aprendió que a veces las manos extrañas empiezan amistades inesperadas.",
    "El faro seguía encendido por costumbre. Álvaro subió sus escaleras y, desde la cima, decidió escribir la primera carta a quien aún no conocía. Así prometió cuidar lo que estaba por venir sin prisa.",
    "Un anciano vendía historias en el mercado; no las cobraba, las prestaba. Quien se sentaba a escuchar, salía con la sensación de que el mundo era más grande y menos urgente.",
    "En un jardín secreto, las palabras crecían como flores. Sofía aprendió a regarlas con silencio y, al final, fue capaz de decir solo lo que realmente importaba."
]

# -------------------- UTILIDADES TTS --------------------
def ensure_temp():
    os.makedirs("temp", exist_ok=True)

def text_to_mp3_bytes(text, lang='es'):
    ensure_temp()
    safe = "".join(c for c in text[:30] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
    if not safe:
        safe = "audio"
    filename = f"{safe}_{int(time.time())}.mp3"
    path = os.path.join("temp", filename)
    # Generar audio (gTTS — necesita conexión)
    tts = gTTS(text, lang=lang)
    tts.save(path)
    with open(path, "rb") as f:
        data = f.read()
    return path, data

def download_link_bytes(bytes_data, filename="audio.mp3", label="📥 Descargar audio"):
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{label}</a>'
    return href

# -------------------- INTERFAZ: OBTENER CUENTO --------------------
st.markdown("## 📚 Obtener cuento aleatorio (ES)")
st.write("Pulsa **Obtener cuento aleatorio** para mostrar una historia breve y directa (solo la historia).")

if st.button("📥 Obtener cuento aleatorio"):
    story = random.choice(ORIGINAL_SPANISH_STORIES)
    # Guardamos temporalmente en session_state para permitir convertirlo sin mostrar 'último cuento'
    st.session_state['current_story'] = story
    # Mostramos solo la historia generada
    st.markdown("### ✨ Cuento")
    st.write(story)

st.markdown("---")

# -------------------- CONVERTIR EL CUENTO ACTUAL --------------------
st.markdown("## 🔊 Convertir el cuento actual a audio")
st.write("Si acabas de obtener un cuento, puedes convertirlo a audio en español (o en inglés si lo deseas).")

if st.button("🔁 Convertir cuento actual a audio"):
    if 'current_story' not in st.session_state:
        st.warning("Primero pulsa 'Obtener cuento aleatorio'.")
    else:
        try:
            # permitimos elegir idioma para la conversión (solo afecta al TTS)
            lang_choice = st.selectbox("Idioma para el audio del cuento:", ("Español", "English"), key="lang_story_convert")
            lg = 'es' if lang_choice == "Español" else 'en'
            path, data = text_to_mp3_bytes(st.session_state['current_story'], lang=lg)
            st.success("Audio del cuento generado ✅")
            st.audio(data, format="audio/mp3")
            st.markdown(download_link_bytes(data, filename=os.path.basename(path), label="📥 Descargar audio del cuento"), unsafe_allow_html=True)
            # una vez convertido, podemos eliminar la clave para evitar "último cuento"
            del st.session_state['current_story']
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

st.markdown("---")

# -------------------- AREA: PEGAR TEXTO PROPIO --------------------
st.markdown("## ✍️ Pega tu propio texto (español)")
user_text = st.text_area("Pega tu texto o cuento aquí:", height=220)
lang_choice2 = st.selectbox("Idioma para el audio (tu texto):", ("Español", "English"), key="lang_text_convert")
if st.button("🔊 Convertir texto a audio"):
    if not user_text.strip():
        st.warning("Por favor pega o escribe algún texto.")
    else:
        try:
            lg2 = 'es' if lang_choice2 == "Español" else 'en'
            path2, data2 = text_to_mp3_bytes(user_text, lang=lg2)
            st.success("Audio generado ✅")
            st.audio(data2, format="audio/mp3")
            st.markdown(download_link_bytes(data2, filename=os.path.basename(path2), label="📥 Descargar tu audio"), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

st.markdown("---")

# -------------------- LIMPIEZA AUTOMÁTICA --------------------
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
st.caption("Historias en español — limpias y directas. gTTS requiere conexión a internet para generar audio.")

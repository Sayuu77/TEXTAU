# app.py
import streamlit as st
import os
import time
import glob
import base64
import io
import random
import urllib.request
from gtts import gTTS
from PIL import Image

# -------------------- CONFIG --------------------
st.set_page_config(page_title=, page_icon="🌌", layout="centered")

# -------------------- STYLE (Neo-Glass nocturno) --------------------
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
      padding: 24px;
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

# -------------------- BACKGROUND OVERLAY (optional clouds) --------------------
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
            port = Image.open("portada.png")
            st.image(port, width=110)
        except Exception:
            pass
with col2:
    st.markdown("<div class='header'><h1 style='margin:0'>🌌 Cuentos & Audio (ES)</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='small-note'>Neo-Glass • Música en loop • Cuentos en español</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- MÚSICA AUTOPLAY (muted -> fade-in) --------------------
# Coloca 'music.mp3' en la carpeta del proyecto para activar música.
if os.path.exists("music.mp3"):
    audio_html = """
    <audio id="bg_audio" autoplay loop muted>
      <source src="music.mp3" type="audio/mpeg">
    </audio>
    <script>
      (function() {
        const a = document.getElementById('bg_audio');
        if (!a) return;
        a.volume = 0.0;
        setTimeout(() => {
          try {
            a.muted = false;
            let vol = 0.0;
            const target = 0.14;
            const step = 0.02;
            const interval = setInterval(() => {
              vol = Math.min(vol + step, target);
              a.volume = vol;
              if (vol >= target) clearInterval(interval);
            }, 100);
          } catch (e) {
            console.log('Autoplay unmute blocked', e);
          }
        }, 600);
      })();
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    try:
        with open("music.mp3", "rb") as mf:
            st.audio(mf.read(), format="audio/mp3", start_time=0)
    except Exception:
        st.info("Música encontrada, pero no se pudo cargar el control nativo.")
else:
    st.info("Para activar música de fondo automática: coloca un archivo `music.mp3` en la carpeta del proyecto.")

st.markdown("---")

# -------------------- FUENTES PÚBLICAS EN ESPAÑOL (ejemplos) --------------------
# Intentamos obtener cuentos en español desde fuentes públicas en español.
# Si la descarga falla, usamos cuentos originales en español (limpios y cortos).
# Las URLs pueden ser actualizadas por ti; muchas bibliotecas digitales tienen textos de dominio público.
SPANISH_STORY_URLS = [
    # Ejemplos de textos en español en dominio público (puedes añadir más URLs válidas).
    # NOTA: Algunas URLs pueden requerir adaptación o fallar según respuesta del servidor.
    "https://www.gutenberg.org/cache/epub/2000/pg2000.txt",  # ejemplo (puede ser en inglés) - se intentará limpiar y si no está en español usamos fallback
    # Puedes agregar otras fuentes públicas en español aquí.
]

# -------------------- HISTORIAS ORIGINALES (fallback / preferidas) --------------------
# Lista de cuentos breves originales en español (limpios, directos)
ORIGINAL_SPANISH_STORIES = [
    # 1
    "La luna rompió el silencio de la plaza. Ana caminó sin prisa, sosteniendo un pequeño papel con una dirección que ya no recordaba. Al llegar, encontró la casa con las luces aún encendidas. Allí, una voz antigua la reconoció por su risa. Fue suficiente para que entendiera: a veces, volver no borra lo pasado, lo transforma en compañía.",
    # 2
    "El río guardaba secretos; Pedro se sentó a la orilla y dejó que el agua le devolviera recuerdos ligeros. Sonrió al pensar que no todo lo que perdemos se va: algunas cosas solo cambian de bolsillo y vuelven como historias.",
    # 3
    "En un pueblo donde todas las puertas eran iguales, Clara encontró una con una marca diminuta. Al cruzarla, descubrió un jardín donde las palabras brotaban en flores. Aprendió a cultivar silencios y a hablar solo cuando la tierra estaba lista.",
    # 4
    "El faro ya no alumbraba barcos, pero seguía encendido por costumbre. Martín subió sus escaleras y, desde arriba, prometió escribir una carta a su propio futuro: la única persona que debía leerla era la que aún no existía.",
    # 5
    "Una niña vendía luciérnagas en frascos. No por maldad, sino por memoria: quería que la noche guardara pequeñas luces que nadie pudiera apagar. Quien compró un frasco, volvió a creer en rutas inesperadas."
]

# -------------------- UTIL: LIMPIAR TEXTO OBTENIDO --------------------
def clean_fetched_text(raw):
    """
    Intenta eliminar cabeceras, pies y metadatos comunes (Gutenberg y similares),
    y devuelve un bloque de texto en español (o cercano) sin prólogos/índices.
    """
    try:
        # Quitar headers tipo Gutenberg
        if '*** START' in raw:
            raw = raw.split('*** START', 1)[-1]
        if '*** END' in raw:
            raw = raw.split('*** END', 1)[0]
        # Quitar secuencias largas de mayúsculas (índices) iniciales
        # Tomar una ventana inicial razonable y buscar primer párrafo largo
        raw = raw.strip()
        # Reemplazar múltiples saltos de línea por doble salto
        raw = "\n\n".join([p.strip() for p in raw.splitlines() if p.strip() != ""])
        # Buscar segmentos en español (heurística: presencia de artículos en español)
        spanish_indicators = [' la ', ' el ', ' que ', ' de ', ' y ', ' los ', ' las ', ' un ', ' una ']
        # Si no parece español, devolvemos None para fallback
        lowered = raw.lower()
        if not any(ind in lowered for ind in spanish_indicators):
            return None
        # Tomar hasta 2000 caracteres terminando en final de párrafo
        max_chars = 2000
        if len(raw) <= max_chars:
            return raw
        # intentar cortar en un parrafo entero
        cut = raw[:max_chars]
        # expandir hasta el siguiente doble salto de linea
        next_break = raw.find('\n\n', max_chars - 200, max_chars + 500)
        if next_break != -1 and next_break < max_chars + 600:
            cut = raw[:next_break]
        return cut.strip()
    except Exception:
        return None

# -------------------- OBTENER CUENTO ALEATORIO (intento internet -> fallback original) --------------------
def fetch_random_spanish_story():
    # Intentar cada URL hasta que alguna devuelva texto en español
    random.shuffle(SPANISH_STORY_URLS)
    for url in SPANISH_STORY_URLS:
        try:
            with urllib.request.urlopen(url, timeout=12) as r:
                raw = r.read().decode('utf-8', errors='ignore')
            cleaned = clean_fetched_text(raw)
            if cleaned:
                return cleaned, url
        except Exception:
            continue
    # Si no se obtuvo nada, devolvemos un cuento original aleatorio
    return random.choice(ORIGINAL_SPANISH_STORIES), "interno:historia_original"

# -------------------- UI: Cuento aleatorio --------------------
st.markdown("## 📚 Cuento aleatorio en español")
st.write("Pulsa **Obtener cuento aleatorio** para traer una historia breve y directa (sin prólogos ni índices).")

if st.button("📥 Obtener cuento aleatorio (ES)"):
    story_text, source = fetch_random_spanish_story()
    st.session_state['last_story'] = story_text
    st.session_state['last_story_source'] = source
    st.markdown("### ✨ Cuento obtenido")
    st.write(story_text)

# Mostrar último cuento si existe
if 'last_story' in st.session_state:
    st.markdown("### ✨ Último cuento obtenido")
    st.write(st.session_state['last_story'])
    st.markdown(f"*Fuente:* <span class='muted'>{st.session_state.get('last_story_source','')}</span>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- TTS / CONVERSIÓN --------------------
def ensure_temp():
    os.makedirs("temp", exist_ok=True)

def text_to_mp3_bytes(text, lang='es'):
    ensure_temp()
    safe = "".join(c for c in text[:30] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
    if not safe:
        safe = "audio"
    filename = f"{safe}_{int(time.time())}.mp3"
    path = os.path.join("temp", filename)
    # Generar con gTTS
    tts = gTTS(text, lang=lang)
    tts.save(path)
    with open(path, "rb") as f:
        data = f.read()
    return path, data

def download_link_bytes(bytes_data, filename="audio.mp3", label="📥 Descargar audio"):
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{label}</a>'
    return href

# -------------------- Convertir cuento obtenido --------------------
st.markdown("## 🔊 Convertir cuento obtenido a audio")
st.write("Si ya obtuviste un cuento arriba, puedes convertirlo a audio en español.")

if st.button("🔁 Convertir cuento obtenido a audio"):
    if 'last_story' not in st.session_state:
        st.warning("Primero pulsa 'Obtener cuento aleatorio'.")
    else:
        try:
            path, data = text_to_mp3_bytes(st.session_state['last_story'], lang='es')
            st.success("Audio del cuento generado ✅")
            st.audio(data, format="audio/mp3")
            st.markdown(download_link_bytes(data, filename=os.path.basename(path), label="📥 Descargar audio del cuento"), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

st.markdown("---")

# -------------------- Convertir texto propio --------------------
st.markdown("## ✍️ Pega tu propio texto (en español)")
user_text = st.text_area("Tu texto aquí (puedes pegar un cuento o cualquier texto en español)", height=220)
lang_choice2 = st.selectbox("Idioma para el audio (texto propio):", ("Español", "English"), key="lang_text")
if st.button("🔊 Convertir texto a audio"):
    if not user_text.strip():
        st.warning("Por favor pega o escribe algún texto.")
    else:
        lg2 = 'es' if lang_choice2 == "Español" else 'en'
        try:
            path2, data2 = text_to_mp3_bytes(user_text, lang=lg2)
            st.success("Audio generado ✅")
            st.audio(data2, format="audio/mp3")
            st.markdown(download_link_bytes(data2, filename=os.path.basename(path2), label="📥 Descargar tu audio"), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

st.markdown("---")

# -------------------- LIMPIEZA TEMP --------------------
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
st.caption("Historias en español — limpias y directas. Si quieres más fuentes públicas en español, puedo añadirlas.")
st.caption("gTTS usa conexión a internet para generar audio. Nada de la interfaz está en inglés, excepto la opción de idioma para convertir el texto si así lo deseas.")

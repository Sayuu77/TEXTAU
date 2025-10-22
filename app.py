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
st.set_page_config(page_title="Cuentos → Audio • Neo-Glass", page_icon="🌌", layout="centered")

# -------------------- STYLE (Neo-Glass) --------------------
st.markdown("""
    <style>
    body {
      background: linear-gradient(180deg, rgba(20,12,40,0.85), rgba(30,18,60,0.92));
      color: #E8EAF6;
      font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .stApp > .main {
      background: rgba(255,255,255,0.03);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.06);
      box-shadow: 0 8px 30px rgba(2,6,23,0.6);
      border-radius: 14px;
      padding: 22px;
    }
    .header {
      display:flex;
      align-items:center;
      gap:16px;
    }
    .glass-btn {
      background: linear-gradient(90deg, rgba(120,84,255,0.18), rgba(80,120,255,0.12));
      color: #F8F9FF;
      border: 1px solid rgba(255,255,255,0.06);
      padding: 10px 16px;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
    }
    textarea { background: rgba(255,255,255,0.02); color: #F1F1FF; }
    .small-note { color: #cfcff6; font-size: 13px; }
    a { color: #C7B3FF; }
    </style>
""", unsafe_allow_html=True)

# -------------------- BACKGROUND IMAGE (optional clouds) --------------------
# If you want to use an image as a gentle overlay background, you can place it in 'images/clouds.png'
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
        port = Image.open("portada.png")
        st.image(port, width=120)
with col2:
    st.markdown("<div class='header'><h1 style='margin:0'>🌌 Cuentos & Audio</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='small-note'>Neo-Glass • Música en loop • Cuentos públicos</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- MUSIC AUTOPLAY (muted -> fade-in) --------------------
# Place 'music.mp3' in the same folder to enable background music.
if os.path.exists("music.mp3"):
    # We include an <audio> element muted (browsers allow autoplay if muted), then unmute + fade-in with JS.
    audio_html = """
    <audio id="bg_audio" autoplay loop muted>
      <source src="music.mp3" type="audio/mpeg">
    </audio>
    <script>
      // Fade-in logic: only attempt after small timeout to increase success across browsers.
      (function() {
        const a = document.getElementById('bg_audio');
        if (!a) return;
        // Try to set volume from 0 to 0.25 over 1.5s
        a.volume = 0.0;
        // Some browsers block unmuting programmatically; but many allow unmuting after short delay if played muted first.
        setTimeout(() => {
          try {
            a.muted = false;
            let vol = 0.0;
            const target = 0.18;
            const step = 0.02;
            const interval = setInterval(() => {
              vol = Math.min(vol + step, target);
              a.volume = vol;
              if (vol >= target) clearInterval(interval);
            }, 80);
          } catch (e) {
            // If unmute is blocked, the user can still press play on the control shown below.
            console.log('Autoplay unmute blocked or failed', e);
          }
        }, 600);
      })();
    </script>
    """
    # Also show a visible player as fallback so user can manually play if autoplay blocked
    st.markdown(audio_html, unsafe_allow_html=True)
    try:
        with open("music.mp3", "rb") as mf:
            st.audio(mf.read(), format="audio/mp3", start_time=0)
    except Exception:
        st.info("Música encontrada, pero no se pudo cargar el control nativo.")
else:
    st.info("Para activar música de fondo: coloca un archivo `music.mp3` en la carpeta del proyecto.")

st.markdown("---")

# -------------------- PUBLIC-DOMAIN STORY SOURCES (Project Gutenberg) --------------------
# We'll fetch a short public-domain story at random from this list.
PUBLIC_STORY_URLS = [
    # O. Henry - The Gift of the Magi (public domain). Plain text UTF-8 endpoint.
    "https://www.gutenberg.org/ebooks/7256.txt.utf-8",
    # Aesop's Fables collection
    "https://www.gutenberg.org/ebooks/21.txt.utf-8",
    # Edgar Allan Poe works (contains many short stories; we'll pick an excerpt)
    "https://www.gutenberg.org/ebooks/2148.txt.utf-8"
]

st.markdown("## 📚 Cuento aleatorio (dominio público)")
st.write("Pulsa *Obtener cuento aleatorio* para traer un cuento corto de una fuente pública (Project Gutenberg).")

# Helper: download a story and produce a reasonable excerpt (tries to keep full short stories or short excerpt)
def fetch_text_from_url(url, max_chars=2200):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            raw = r.read().decode('utf-8', errors='ignore')
        # Heurística: buscar títulos y separar por capítulos o relatos
        # Si hay '*** START' Gutenberg header, strip header
        if '*** START' in raw:
            raw = raw.split('*** START')[1]
        # Reduce large prefaces and pick a reasonably sized window:
        clean = raw.strip()
        if len(clean) <= max_chars:
            return clean
        # Try to find two newlines (i.e., paragraph) boundaries for nicer cuts
        # We'll take the first 2000-2200 chars that end at a paragraph boundary
        chunk = clean[:max_chars]
        # expand to next paragraph end if available
        next_break = clean.find('\n\n', max_chars - 200, max_chars + 400)
        if next_break != -1 and next_break < max_chars + 600:
            chunk = clean[:next_break]
        # Trim leading/trailing whitespace
        chunk = chunk.strip()
        return chunk
    except Exception as e:
        return f"(Error al obtener el cuento: {e})"

# Button to fetch a random public-domain story
if st.button("📥 Obtener cuento aleatorio"):
    url = random.choice(PUBLIC_STORY_URLS)
    st.info(f"Obteniendo desde: {url}")
    story_text = fetch_text_from_url(url)
    st.session_state['last_fetched_story'] = story_text
    st.session_state['last_fetched_source'] = url
    st.markdown("### ✨ Cuento obtenido")
    st.write(story_text)

# If user already fetched before, show it
if 'last_fetched_story' in st.session_state:
    st.markdown("### ✨ Último cuento obtenido")
    st.write(st.session_state['last_fetched_story'])
    st.markdown(f"*Fuente:* <small>{st.session_state.get('last_fetched_source','')}</small>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- AREA: convertir cuento a audio --------------------
st.markdown("## 🔊 Convertir cuento (o texto) a audio")
st.write("Puedes convertir el cuento obtenido arriba ó pegar tu propio texto abajo.")

def ensure_temp():
    os.makedirs("temp", exist_ok=True)

def text_to_mp3_bytes(text, lang='es'):
    # returns path to temp file and bytes
    ensure_temp()
    safe = "".join(c for c in text[:30] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
    if not safe:
        safe = "audio"
    filename = f"{safe}_{int(time.time())}.mp3"
    path = os.path.join("temp", filename)
    # Generate using gTTS
    tts = gTTS(text, lang=lang)
    tts.save(path)
    with open(path, "rb") as f:
        data = f.read()
    return path, data

def download_link_bytes(bytes_data, filename="audio.mp3", label="Descargar audio"):
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{label}</a>'
    return href

# Convert last fetched story
if st.button("🔁 Convertir cuento obtenido a audio"):
    if 'last_fetched_story' not in st.session_state:
        st.warning("Primero obtén un cuento con 'Obtener cuento aleatorio'.")
    else:
        lang_choice = st.selectbox("Idioma para el audio (cuento)", ("Español", "English"), key="lang_story")
        lg = 'es' if lang_choice == "Español" else 'en'
        path, data = text_to_mp3_bytes(st.session_state['last_fetched_story'], lang=lg)
        st.success("Audio del cuento generado ✅")
        st.audio(data, format="audio/mp3")
        st.markdown(download_link_bytes(data, filename=os.path.basename(path), label="📥 Descargar audio del cuento"), unsafe_allow_html=True)

st.markdown("---")

# -------------------- AREA: pegar texto propio --------------------
st.markdown("## ✍️ Pega tu propio texto")
user_text = st.text_area("Tu texto aquí (o pega un cuento)", height=200)
lang_choice2 = st.selectbox("Idioma para el audio (texto propio)", ("Español", "English"), key="lang_text")
if st.button("🔊 Convertir texto a audio"):
    if not user_text.strip():
        st.warning("Por favor pega o escribe algún texto.")
    else:
        lg2 = 'es' if lang_choice2 == "Español" else 'en'
        path2, data2 = text_to_mp3_bytes(user_text, lang=lg2)
        st.success("Audio generado ✅")
        st.audio(data2, format="audio/mp3")
        st.markdown(download_link_bytes(data2, filename=os.path.basename(path2), label="📥 Descargar tu audio"), unsafe_allow_html=True)

st.markdown("---")

# -------------------- CLEANUP --------------------
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

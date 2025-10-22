import streamlit as st
import os
import time
import glob
import base64
import io
import random
from gtts import gTTS
from PIL import Image
import requests

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Cuentos → Audio • Lofi Dreamy", page_icon="🌙", layout="centered")

# -------------------- ESTILO Lofi Dreamy (neo-glass) --------------------
st.markdown("""
    <style>
    :root{
      --accent1: #9B84FF; /* lila */
      --accent2: #90E0FF; /* celeste */
      --glass-bg: rgba(255,255,255,0.04);
      --text-soft: #F3F2FF;
    }
    body {
      background: linear-gradient(180deg, #0B0820 0%, #1B1130 50%, #0F1724 100%);
      color: var(--text-soft);
      font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
    }
    .stApp > .main {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1px solid rgba(255,255,255,0.03);
      box-shadow: 0 8px 30px rgba(2,6,23,0.7);
      border-radius: 16px;
      padding: 26px;
    }
    /* Hero banner */
    .hero-title {
      font-size: 34px;
      font-weight: 700;
      margin: 8px 0 2px 0;
      color: white;
      letter-spacing: 0.2px;
    }
    .hero-sub {
      color: #DAD6FF;
      margin: 0 0 12px 0;
    }

    /* Buttons */
    .stButton>button, .glass-btn {
      background: linear-gradient(90deg, var(--accent2), var(--accent1));
      color: white;
      border: none;
      padding: 10px 16px;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 6px 18px rgba(139,115,255,0.12);
    }
    .stButton>button:hover {
      filter: brightness(1.06);
      transform: translateY(-1px);
    }

    /* Cards / textareas */
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(255,255,255,0.03);
      padding: 14px;
      border-radius: 12px;
      box-shadow: 0 6px 20px rgba(2,6,23,0.6);
    }
    textarea { background: rgba(255,255,255,0.02); color: #F6F6FF; }
    .small-note { color: #CFCFF6; font-size: 13px; margin-top:6px; }
    .muted { color: #BDB9E8; font-size:13px; }
    </style>
""", unsafe_allow_html=True)

# -------------------- HERO BANNER (portada grande) --------------------
# If portada.png exists in folder, use it. Otherwise use an online fallback image.
hero_image_path = "portada.png"
fallback_url = "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1350&q=80"

st.markdown("<div style='display:flex; gap:18px; align-items:center'>", unsafe_allow_html=True)
if os.path.exists(hero_image_path):
    try:
        img = Image.open(hero_image_path)
        st.image(img, use_column_width=True)
    except Exception:
        # if failed to load local, try remote
        st.image(fallback_url, use_container_width=True)
else:
    # load remote hero image
    st.image(fallback_url, use_column_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>🌙 Cuentos & Audio — Lofi Dreamy</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Historias en español — inmersivas, sutiles y en tono de realismo mágico</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- CUENTOS (medianos, realismo mágico + fantasía suave) --------------------
STORIES = [
    """La noche había teñido la laguna de un azul que parecía guardar secretos. Marta llegó con una carta sin remitente y la dejó sobre la piedra más alta. Al abrirla descubrió una palabra: regreso. La palabra no era una instrucción; era una puerta. Cuando la pronunció, las linternas del pueblo encendieron una fila de luces en el agua y un barquero de sombra la condujo hacia una isla que no aparecía en los mapas. Allí encontró objetos con nombres olvidados: una taza que susurraba palabras de infancia, un reloj que corría hacia atrás para recuperar instantes. Marta comprendió que el lugar no borraba el pasado, lo ponía en orden como quien acomoda los libros de una biblioteca para que vuelvan a leerse con ternura.""",
    """En la plaza central, los relojes marcaban horas distintas según el lado por donde uno entrara. Bruno, aburrido de la rutina, decidió cruzar la plaza cada día por una puerta diferente. Un martes halló una puerta pequeña y circular, apenas perceptible, que lo condujo a una estación donde el tren esperaba silencioso. Solo subían viajeros que buscaban un recuerdo específico: la sonrisa de una madre, la voz de un abuelo, el sabor de una merienda. Bruno pidió su recuerdo y, al mirarlo, descubrió que aquello que había perdido no era solo una cosa, sino la manera en que lo miraba. Al bajar del tren, volvió al pueblo un poco más paciente con su propia memoria.""",
    """Una librería se escondía entre fachadas iguales; su dueño, sin edad, iba colocando palabras que nadie pedía. Marta entró una tarde de lluvia porque su paraguas le pidió refugio. Allí encontró una novela que describía exactamente la escena que vivía en ese instante: la humedad en el cristal, la mirada de un hombre leyendo al fondo, su propia duda. La novela no era espejo, era promesa: quien la leyera con atención hallaría una página extra, un relato pequeño que hablaba de decisiones aún no tomadas. Marta escribió su nombre en esa página y la tinta, por un instante, se transformó en una escalera hacia una ventana que ella no sabía que necesitaba abrir.""",
    """Un faro que ya no guiaba barcos seguía encendido por costumbre. Cada noche, su luz dibujaba un camino que nadie seguía hasta que Lucas, cansado de ciudades sin memoria, subió los peldaños. En la cima halló cartas atadas con cordeles: palabras dirigidas a futuros lectores que aún no existían. Tomó una, la leyó y sintió que leían en voz baja aquello que su propia vida callaba. Escribió otra, puso su firma y la ató. Tiempo después recibió una carta desde un lugar que no conocía: quien la firmaba decía haber recibido la suya y agradecía por haber escrito algo que lo había salvado de una noche sin estrellas.""",
    """En un barrio donde las casas cambiaban de paredes cada primavera, Lucía encontró una puerta que crujía en otra lengua. Tras atravesarla apareció un jardín donde crecían frases como flores: poemas, silencios, promesas. Para regarlas no usaba agua sino recuerdos. Lucía dejó caer en la tierra una memoria de su infancia, una tarde de juegos y risas olvidadas, y al crecer la planta le entregó un recuerdo que nunca supo que necesitaba: la certeza de que algunas pérdidas se convierten en compañía si se les permite echar raíces.""",
    """Había un café en la esquina donde los clientes solo pedían cosas pequeñas: un gesto, una disculpa, una canción. El dueño no cobraba sino que guardaba las palabras en frascos. Una tarde entró Elena y señaló un frasco sin etiqueta. Al abrirlo, una melodía salió y llenó el lugar de nombres propios. Elena entendió que el frasco guardaba lo que uno había sido y decidió llevarse un poco. Desde entonces volvió a hablar con quienes evitaba y notó que el mundo tenía más huecos para llenar que para temer."""
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
    # gTTS puede fallar si el texto es muy largo; dividimos si es necesario en chunks razonables
    # Para la mayoría de historias medianas esto funciona directo.
    tts = gTTS(text, lang=lang)
    tts.save(path)
    with open(path, "rb") as f:
        data = f.read()
    return path, data

def download_link_bytes(bytes_data, filename="audio.mp3", label="📥 Descargar audio"):
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{label}</a>'
    return href

# -------------------- UI: Obtener cuento --------------------
st.markdown("## 📚 Cuento aleatorio")
st.write("Pulsa **Obtener cuento** y aparecerá una historia completa (mediana, lista para leer).")

if st.button("📥 Obtener cuento"):
    story = random.choice(STORIES)
    st.session_state['current_story'] = story
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### ✨ Tu cuento")
    st.write(story)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------- CONVERTIR EL CUENTO A AUDIO --------------------
st.markdown("## 🔊 Convertir el cuento a audio")
st.write("Convierte el cuento obtenido o conviértelo en otro idioma con la opción de idioma.")

if st.button("🔁 Convertir cuento a audio"):
    if 'current_story' not in st.session_state:
        st.warning("Primero pulsa 'Obtener cuento'.")
    else:
        try:
            # elegir idioma solo para TTS (interface sigue en español)
            lang_choice = st.selectbox("Idioma para el audio del cuento:", ("Español", "English"), key="lang_story_convert")
            lg = 'es' if lang_choice == "Español" else 'en'
            path, data = text_to_mp3_bytes(st.session_state['current_story'], lang=lg)
            st.success("Audio del cuento generado ✅")
            st.audio(data, format="audio/mp3")
            st.markdown(download_link_bytes(data, filename=os.path.basename(path), label="📥 Descargar audio del cuento"), unsafe_allow_html=True)
            # borrar el cuento actual para no recordarlo después
            del st.session_state['current_story']
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

st.markdown("---")

# -------------------- CONVERTIR TEXTO PROPIO --------------------
st.markdown("## ✍️ Pega tu propio texto (en español)")
user_text = st.text_area("Pega tu texto o cuento aquí:", height=220)
lang_choice2 = st.selectbox("Idioma para el audio (tu texto):", ("Español", "English"), key="lang_text_convert")
if st.button("🔊 Convertir tu texto a audio"):
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

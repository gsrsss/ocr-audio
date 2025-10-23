import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Variable global para almacenar el texto extraído
text = ""

def text_to_speech(input_language, output_language, text, tld):
    """
    Traduce el texto y lo convierte a voz, guardándolo como un archivo MP3.
    """
    try:
        translator = Translator()
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        
        # Crear un nombre de archivo simple
        try:
            my_file_name = text[0:20].replace(" ", "_").replace("\n", "_")
        except:
            my_file_name = "audio"
        
        # Asegurarse de que el directorio temp exista
        os.makedirs("temp", exist_ok=True)
        
        audio_path = f"temp/{my_file_name}.mp3"
        tts.save(audio_path)
        return my_file_name, trans_text, audio_path
    except Exception as e:
        st.error(f"Error en la conversión a voz: {e}")
        return None, None, None

def remove_files(n):
    """
    Elimina archivos MP3 antiguos del directorio temporal.
    """
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            try:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)
            except Exception as e:
                print(f"No se pudo eliminar {f}: {e}")

# --- Inicio de la App de Streamlit ---

# Limpiar archivos antiguos al iniciar
remove_files(7)

# Se eliminó el Estilo CSS para las cajas rosadas

st.title("Reconocimiento Óptico de Caracteres (✿^‿^)")
st.subheader("Extrae texto de imágenes y escúchalo en otro idioma.")

# --- Sección 1: Carga de Imagen ---
st.markdown("<h2>Paso 1: Elige tu Imágen</h2>", unsafe_allow_html=True)

cam_ = st.checkbox("Usar Cámara")
filtro = 'No'  # Valor por defecto

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
    filtro = st.radio("Aplicar filtro (invertir color)", ('Sí', 'No'), help="Útil para texto blanco sobre fondo oscuro.")
else:
    img_file_buffer = None

st.markdown("<p style='text-align: center; color: #FFB6C1;'>— O —</p>", unsafe_allow_html=True)

bg_image = st.file_uploader("Cargar una Imagen:", type=["png", "jpg", "jpeg"])


# --- Sección 2: Procesamiento de Imagen y OCR ---
if bg_image is not None:
    try:
        # Para manejar archivos en memoria
        file_bytes = np.asarray(bytearray(bg_image.read()), dtype=np.uint8)
        img_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)
        st.success("¡Imagen cargada y procesada! (◕‿◕)")
    except Exception as e:
        st.error(f"Error al procesar la imagen cargada: {e}")
        text = "" # Resetear texto en caso de error

if img_file_buffer is not None:
    try:
        # To read image file buffer with OpenCV:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        if filtro == 'Sí':
            # Aplicar filtro de inversión de color
            cv2_img = cv2.bitwise_not(cv2_img)
        
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)
        st.success("¡Foto capturada y procesada! (◠‿◠)")
    except Exception as e:
        st.error(f"Error al procesar la foto de la cámara: {e}")
        text = "" # Resetear texto en caso de error

# --- Sección 3: Mostrar Texto Extraído (Editable) ---
# Se eliminó la caja rosada
st.subheader("Texto Extraído (Puedes editarlo) ✧˖°")
text = st.text_area("Resultado del OCR:", text, height=200, label_visibility="collapsed")


# --- Sección 4: Traducción y Text-to-Speech ---
st.markdown("<h2>Paso 2: Traducir y Escuchar 🎧</h2>", unsafe_allow_html=True)

# Crear directorio temporal si no existe
try:
    os.makedirs("temp", exist_ok=True)
except FileExistsError:
    pass

# Columnas para los selectores de idioma
col1, col2 = st.columns(2)

with col1:
    in_lang = st.selectbox(
        "Lenguaje de entrada (original):",
        ("Español", "Ingles", "Bengali", "Koreano", "Mandarin", "Japones"),
        index=1 # Default a Ingles
    )
    
with col2:
    out_lang = st.selectbox(
        "Lenguaje de salida (traducción):",
        ("Español", "Ingles", "Bengali", "Koreano", "Mandarin", "Japones"),
        index=0 # Default a Español
    )

# Mapeo de nombres amigables a códigos de idioma
lang_map = {
    "Ingles": "en",
    "Español": "es",
    "Bengali": "bn",
    "Koreano": "ko",
    "Mandarin": "zh-cn",
    "Japones": "ja"
}
input_language = lang_map.get(in_lang, "en")
output_language = lang_map.get(out_lang, "es")

# Selector de acento (solo relevante para inglés)
english_accent = st.selectbox(
    "Seleccione el acento (si la salida es Inglés):",
    (
        "Default (US)", "India", "United Kingdom", "Canada", "Australia",
        "Ireland", "South Africa",
    ),
)

accent_map = {
    "Default (US)": "com",
    "India": "co.in",
    "United Kingdom": "co.uk",
    "Canada": "ca",
    "Australia": "com.au",
    "Ireland": "ie",
    "South Africa": "co.za"
}
tld = accent_map.get(english_accent, "com")

display_output_text = st.checkbox("Mostrar texto traducido", value=True)

if st.button("Convertir y Hablar!", use_container_width=True, type="primary"):
    if text and text.strip():
        with st.spinner("Traduciendo y generando audio..."):
            result, output_text, audio_path = text_to_speech(input_language, output_language, text, tld)
            
            if audio_path and os.path.exists(audio_path):
                audio_file = open(audio_path, "rb")
                audio_bytes = audio_file.read()
                
                st.markdown("### ¡Tu audio está listo!")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                
                if display_output_text:
                    # Se eliminó la caja rosada
                    st.markdown("### Texto Traducido:")
                    st.write(f"> {output_text}")
            else:
                st.error("No se pudo generar el archivo de audio.")
    else:
        st.warning("No hay texto para convertir. Por favor, carga una imagen o toma una foto primero. (・_・;)")

import streamlit as st
import tempfile
import os
from groq import Groq
from moviepy.editor import VideoFileClip
import time

# Configurar la página
st.set_page_config(
  page_title="Transcriptor de Videos",
  page_icon="🎥",
  layout="centered"
)

# Estilo personalizado mejorado
st.markdown("""
  <style>
    /* Estilos generales */
    .stApp {
      max-width: 900px;
      margin: 0 auto;
    }
    
    .main {
      background-color: #f8f9fa;
      padding: 2rem;
      border-radius: 12px;
    }
    
    /* Estilos para el contenedor principal */
    .block-container {
      padding-top: 2rem;
      padding-bottom: 3rem;
    }
    
    /* Estilos para el título */
    h1 {
      color: #1e1e1e;
      margin-bottom: 2rem !important;
      padding-bottom: 1rem;
      border-bottom: 2px solid #e0e0e0;
    }
    
    /* Estilos para el área de carga */
   
    
    /* Estilos para botones */
    .stButton button {
      width: 100%;
      background-color: #4CAF50 !important;
      color: white !important;
      padding: 0.75rem 1.5rem !important;
      font-size: 1.1rem !important;
      font-weight: 500 !important;
      border-radius: 8px !important;
      border: none !important;
      box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2) !important;
      transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
      background-color: #45a049 !important;
      box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3) !important;
      transform: translateY(-1px);
    }
    
    
    .transcription-text {
      background-color: #ffffff;
      color: #1e1e1e;
      padding: 1.5rem;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      font-size: 1.1rem;
      line-height: 1.6;
      margin-top: 1rem;
      white-space: pre-wrap;
    }
    
    /* Estilos para el spinner */
    .stSpinner {
      text-align: center;
      margin: 2rem 0;
    }
    
    /* Estilos para mensajes de error */
    .stAlert {
      background-color: #fff3f3;
      color: #dc3545;
      padding: 1rem;
      border-radius: 8px;
      margin: 1rem 0;
    }
  </style>
""", unsafe_allow_html=True)

# Título de la aplicación
st.title("🎥 Transcriptor de Videos")

# Configurar cliente Groq
@st.cache_resource
def get_groq_client():
  return Groq(api_key="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")

client = get_groq_client()

def video_to_audio(video_path):
  """Convierte video a audio usando moviepy"""
  try:
    temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
    video.close()
    return temp_audio.name
  except Exception as e:
    st.error(f"Error al convertir video a audio: {str(e)}")
    return None

def cleanup_temp_files(*files):
  """Limpia archivos temporales con reintentos"""
  for file in files:
    if file and os.path.exists(file):
      for _ in range(3):  # Intentar 3 veces
        try:
          os.close(getattr(file, 'file_no', -1))
          os.unlink(file)
          break
        except Exception:
          time.sleep(1)

# Contenedor principal
with st.container():
  # Área de carga de archivos
  st.markdown('<div class="upload-area">', unsafe_allow_html=True)
  video_file = st.file_uploader(
    "📤 Selecciona un video para transcribir",
    type=['mp4', 'avi', 'mov', 'mkv'],
    help="Formatos soportados: MP4, AVI, MOV, MKV"
  )
  st.markdown('</div>', unsafe_allow_html=True)

  if video_file:
    # Mostrar el video
    st.video(video_file)
    
    # Botón para transcribir
    if st.button("🎯 Transcribir Video", use_container_width=True):
      with st.spinner('🔄 Procesando video, por favor espere...'):
        temp_video = None
        audio_path = None
        
        try:
          temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
          temp_video.write(video_file.read())
          temp_video.close()
          
          audio_path = video_to_audio(temp_video.name)
          
          if not audio_path:
            st.error("Error al procesar el video")
          else:
            with open(audio_path, "rb") as audio_file:
              transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), audio_file.read()),
                model="whisper-large-v3",
                language="es"
              )
            
            # Mostrar transcripción con mejor formato
            st.markdown('<div class="transcription-area">', unsafe_allow_html=True)
            st.markdown("### 📝 Transcripción:")
            st.markdown(f'<div class="transcription-text">{transcription.text}</div>', unsafe_allow_html=True)
            
            # Botón de descarga
            st.download_button(
              "⬇️ Descargar transcripción",
              transcription.text,
              file_name="transcripcion.txt",
              mime="text/plain",
              help="Descarga el texto transcrito en formato TXT"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
          st.error(f"❌ Error en la transcripción: {str(e)}")
        finally:
          cleanup_temp_files(
            getattr(temp_video, 'name', None),
            audio_path
          )

# Información adicional
with st.expander("ℹ️ Acerca de esta aplicación"):
  st.markdown("""
    ### 🚀 Características:
    
    - **Whisper**: Motor de transcripción de audio a texto de última generación
    - **Groq**: Backend de procesamiento de alto rendimiento
    - **Streamlit**: Interfaz de usuario moderna y responsive
    
    ### ⏱️ Tiempos de procesamiento:
    La transcripción puede tomar varios minutos dependiendo de:
    - Duración del video
    - Calidad del audio
    - Complejidad del contenido
    
    ### 📋 Formatos soportados:
    - MP4
    - AVI
    - MOV
    - MKV
  """)
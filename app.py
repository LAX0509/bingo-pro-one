import streamlit as st
import time
import base64
import os
from utils.aleatorios import LibreriaAleatoria

# 1. CONFIGURACIÓN E INTERFAZ BASE
st.set_page_config(page_title="Bingo Pro One", layout="wide", page_icon="🎰")

# Función robusta para cargar imágenes en Base64
def get_base64(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# 2. LÓGICA DE GENERACIÓN
def crear_carton_logica(generador):
    carton = {
        'B': generador.generar_lista_unica(5, 1, 15),
        'I': generador.generar_lista_unica(5, 16, 30),
        'N': generador.generar_lista_unica(4, 31, 45),
        'G': generador.generar_lista_unica(5, 46, 60),
        'O': generador.generar_lista_unica(5, 61, 75)
    }
    carton['N'].insert(2, "👑") 
    return carton

# 3. COMPONENTES VISUALES
def mostrar_balota_lider(letra, numero):
    # Ruta corregida según tu estructura (.png)
    bin_balota = get_base64("assets/plantilla balota.png")
    st.markdown(f"""
        <div style="position: relative; width: 350px; margin: auto;">
            <img src="data:image/png;base64,{bin_balota}" style="width: 100%;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -45%); text-align: center;">
                <h1 style="color: #f1c40f; font-size: 80px; margin: 0; text-shadow: 2px 2px 5px black; font-family: Arial;">{numero}</h1>
                <p style="color: white; font-size: 25px; margin: 0; font-weight: bold; font-family: sans-serif;">{letra}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def mostrar_carton_visual(carton):
    # Ruta corregida según tu estructura (.png)
    bin_carton = get_base64("assets/carton.png")
    html_carton = f"""
    <div style="position: relative; width: 450px; margin: auto;">
        <img src="data:image/png;base64,{bin_carton}" style="width: 100%;">
        <div style="position: absolute; top: 22%; left: 8%; width: 84%; height: 70%; 
                    display: grid; grid-template-columns: repeat(5, 1fr); 
                    grid-template-rows: repeat(5, 1fr); text-align: center; align-items: center;">
    """
    for i in range(5):
        for letra in 'BINGO':
            val = carton[letra][i]
            estilo = "color: #f1c40f; font-size: 24px; font-weight: bold;"
            if val == "👑": estilo = "font-size: 30px;"
            html_carton += f"<div style='{estilo}'>{val}</div>"
    html_carton += "</div></div>"
    st.markdown(html_carton, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'bingo' not in st.session_state:
    st.session_state.bingo = LibreriaAleatoria()
    st.session_state.balotas = []
    st.session_state.corriendo = False
    st.session_state.mi_carton = None
    st.session_state.creditos = 1000

# Header - Ruta corregida (.png)
st.image("assets/logo.png", use_column_width=True)

# --- SIDEBAR ---
st.sidebar.subheader("🎵 Ambiente")
try:
    audio_path = 'assets/musica.mp3'
    if os.path.exists(audio_path):
        audio_file = open(audio_path, 'rb')
        st.sidebar.audio(audio_file.read(), format='audio/mp3', loop=True)
    else:
        st.sidebar.warning("Archivo musica.mp3 no encontrado")
except Exception as e:
    st.sidebar.error(f"Error de audio: {e}")

velocidad = st.sidebar.slider("Velocidad de sorteo (seg)", 0.5, 5.0, 2.0)

if st.sidebar.button("♻️ Reiniciar Partida"):
    st.session_state.balotas = []
    st.session_state.corriendo = False
    st.rerun()

prob = (75 - len(st.session_state.balotas)) / 75 * 100
st.sidebar.metric("Probabilidad Restante", f"{prob:.1f}%")

# --- CUERPO PRINCIPAL ---
col_balota, col_tablero = st.columns([1, 2])

with col_balota:
    st.subheader("🔮 Sorteo")
    if st.button("🎰 Lanzar / Pausar"):
        st.session_state.corriendo = not st.session_state.corriendo

    if st.session_state.corriendo:
        if len(st.session_state.balotas) < 75:
            n = st.session_state.bingo.generar_entero(1, 75)
            if n not in st.session_state.balotas:
                st.session_state.balotas.append(n)
                letra = 'B' if n <= 15 else 'I' if n <= 30 else 'N' if n <= 45 else 'G' if n <= 60 else 'O'
                mostrar_balota_lider(letra, n)
                # Cantado por voz
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{letra} {n}'));</script>", height=0)
                time.sleep(velocidad)
                st.rerun()
            else:
                st.rerun() # Reintenta si sale repetido por el generador
        else:
            st.success("¡Juego terminado!")
            st.session_state.corriendo = False

with col_tablero:
    st.subheader("📊 Tablero Real")
    # Ruta corregida (.png)
    bin_conteo = get_base64("assets/conteo.png")
    html_tablero = f"""
    <div style="position: relative; width: 100%; max-width: 600px; margin: auto;">
        <img src="data:image/png;base64,{bin_conteo}" style="width: 100%;">
        <div style="position: absolute; top: 7%; left: 0%; width: 100%; height: 91%;
                    display: grid; grid-template-columns: repeat(5, 1fr); grid-template-rows: repeat(15, 1fr);">
    """
    for fila in range(1, 16):
        for col in range(5):
            numero_celda = fila + (col * 15)
            if numero_celda in st.session_state.balotas:
                html_tablero += f'<div style="display: flex; justify-content: flex-end; align-items: center; padding-right: 12%;"><span style="color: #f1c40f; font-size: 1.2vw; text-shadow: 0 0 5px orange;">⭐</span></div>'
            else:
                html_tablero += "<div></div>"
    html_tablero += "</div></div>"
    st.markdown(html_tablero, unsafe_allow_html=True)

# --- SECCIÓN JUGADOR ---
st.divider()
c1, c2 = st.columns([2, 1])

with c2:
    st.metric("💰 Tus Créditos", f"{st.session_state.creditos}")
    if st.button("🎰 Comprar Cartón (50 cr)"):
        if st.session_state.creditos >= 50:
            st.session_state.creditos -= 50
            st.session_state.mi_carton = crear_carton_logica(st.session_state.bingo)
            st.success("¡Cartón generado!")
        else:
            st.error("Créditos insuficientes")
    
    st.markdown("---")
    if st.button("🔍 Verificar Ganador"):
        if st.session_state.mi_carton:
            st.info("Analizando patrones...")
            time.sleep(1)
            st.warning("Aún no tienes BINGO.")

with c1:
    if st.session_state.mi_carton:
        mostrar_carton_visual(st.session_state.mi_carton)
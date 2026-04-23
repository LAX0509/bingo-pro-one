import streamlit as st
import time
import base64
import os
import threading
from utils.aleatorios import LibreriaAleatoria

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="Bingo Pro Simulación", layout="wide", page_icon="🎰")

# --- CSS PROFESIONAL, ADAPTATIVO Y ANIMACIONES ---
st.markdown("""
        
    <style>
    /* --- ESTRUCTURA RESPONSIVA DE COLUMNAS --- */
    /* En PC: 5 columnas alineadas */
    [data-testid="column"] { 
        flex: 1 1 18% !important; 
        min-width: 18% !important; 
    }

            html {
    scroll-behavior: smooth;
}
            
    /* En MÓVIL (Pantallas menores a 768px) */
    @media (max-width: 768px) {
        /* Forzamos que las columnas no se rompan (importante para el cartón) */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
        }
        
        [data-testid="column"] { 
            min-width: 19% !important; 
            margin: 0 !important; 
            padding: 0px !important; 
        }

        /* Botones más pequeños en móvil para que quepan todos */
        .stButton > button { 
            font-size: 12px !important; 
            padding: 2px !important; 
            height: 35px !important;
        }
        
        /* Ajuste del título del login en móvil */
        h1 { font-size: 2rem !important; }
        .balota-header h1 { font-size: 35px !important; }
    }
    
    /* --- ANIMACIÓN DE PULSO (Nueva Balota) --- */
    @keyframes pulse-red {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
        50% { transform: scale(1.05); box-shadow: 0 0 20px 10px rgba(220, 38, 38, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    .nueva-balota-anim {
        animation: pulse-red 0.8s ease-in-out 3;
        border: 4px solid #ffffff !important;
    }

    /* --- ENCABEZADO DE BALOTA --- */
    .balota-header {
        text-align: center;
        background: linear-gradient(135deg, #1e3a8a, #dc2626);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }

    /* --- MEJORA DE MÉTRICA Y SIDEBAR --- */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 10px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stMetricValue"] { color: #1e3a8a !important; font-weight: bold !important; font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] p { color: #333333 !important; font-weight: 600 !important; }

    .sidebar-user-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #ffd700;
        margin-bottom: 15px;
    }
    .user-label { color: #ffd700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 0px; }
    .user-name { color: white; font-size: 1.2rem; font-weight: bold; }
            
    /* --- BOTONES DEL LÍDER (Adaptativos) --- */
    .stElementContainer:has(button[key*="btn_lider"]) button {
        height: auto !important;
        min-height: 50px !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        background-color: #1e3a8a !important;
        color: white !important;
        border: 2px solid #ffd700 !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DE SINCRONIZACIÓN ---
@st.cache_resource
def obtener_servidor_bingo():
    return {"salas": {}, "lock": threading.Lock()}

servidor = obtener_servidor_bingo()

# --- FUNCIONES DE APOYO ---
def get_base64(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def crear_carton_logica():
    gen = LibreriaAleatoria()
    carton = {
        'id': gen.generar_entero(1000, 9999),
        'B': gen.generar_lista_unica(5, 1, 15),
        'I': gen.generar_lista_unica(5, 16, 30),
        'N': gen.generar_lista_unica(4, 31, 45),
        'G': gen.generar_lista_unica(5, 46, 60),
        'O': gen.generar_lista_unica(5, 61, 75)
    }
    carton['N'].insert(2, "👑")
    return carton

def get_audio_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

def verificar_ganador(cartones, balotas_salidas):
    balotas_set = set(balotas_salidas)
    for c in cartones:
        todos_numeros = [n for col in "BINGO" for n in c[col] if n != "👑"]
        if all(num in balotas_set for num in todos_numeros):
            return c['id']
    return None

if 'user' not in st.session_state:
    st.session_state.user = {"nombre": "", "creditos": 100, "cartones": [], "sala_id": None, "rol": None}

# --- 1. LOGIN 
if not st.session_state.user["nombre"]:
    img_logo_b64 = get_base64("assets/logo.png")
    
    if img_logo_b64:
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 50px; margin-bottom: 30px;'>
                <img src='data:image/png;base64,{img_logo_b64}' width='180' style='border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);'>
                <h1 style='margin-top: 20px; font-size: 3rem; color: white; text-align: center; font-family: sans-serif;'>
                    Bingo Pro <br>
                    <span style='font-size: 1.5rem; opacity: 0.8;'>Simulación en Tiempo Real</span>
                </h1>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.title(" Bingo Pro: Simulación en Tiempo Real")
    
    col_login, _ = st.columns([2, 1])
    with col_login:
        nombre = st.text_input("Ingresa tu Apodo / ID de Estudiante:")
        if st.button("Ingresar al Sistema", use_container_width=True):
            if nombre:
                st.session_state.user["nombre"] = nombre
                st.rerun()

# 2. LOBBY 
elif not st.session_state.user["sala_id"]:
    st.header(f"👋 Bienvenido, {st.session_state.user['nombre']}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Modo Líder")
        if st.button("Crear Nueva Sala (ID Aleatorio)"):
            gen_sala = LibreriaAleatoria()
            cod = str(gen_sala.generar_entero(100, 999))
            with servidor["lock"]:
                servidor["salas"][cod] = {
                    "lider": st.session_state.user["nombre"],
                    "balotas_salidas": [],
                    "jugadores": {st.session_state.user["nombre"]: []},
                    "ver_mapa": False,
                    "reproduciendo_conteo": False
                }
            st.session_state.user.update({"sala_id": cod, "rol": "Lider"})
            st.rerun()
    with c2:
        st.subheader("Modo Jugador")
        cod_in = st.text_input("Código de Sala:")
        if st.button("Unirse a Sala"):
            if cod_in in servidor["salas"]:
                st.session_state.user.update({"sala_id": cod_in, "rol": "Jugador"})
                st.rerun()

# 3. TABLERO DE JUEGO
else:
    sala_id = st.session_state.user["sala_id"]
    sala = servidor["salas"].get(sala_id)
    
    if not sala:
        st.error("Sala finalizada.")
        if st.button("Volver"):
            st.session_state.user["sala_id"] = None
            st.rerun()
        st.stop()

    # INYECCIÓN DE MÚSICA DE FONDO
    audio_bg_b64 = get_audio_base64("assets/musica.mp3")
    if audio_bg_b64:
     st.components.v1.html(f"""
        <audio id="bg-music" loop autoplay>
            <source src="data:audio/mp3;base64,{audio_bg_b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("bg-music");
            audio.volume = 0.05; 
        </script>
    """, height=0)

    # SIDEBAR
    st.sidebar.title(f"📍 Sala: {sala_id}")
    st.sidebar.markdown(f"""
        <div class="sidebar-user-box">
            <p class="user-label">Jugador Activo</p>
            <p class="user-name">{st.session_state.user['nombre']}</p>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.metric("💰 Créditos", st.session_state.user["creditos"])
    if st.sidebar.button("🚪 Salir"):
        st.session_state.user["sala_id"] = None
        st.rerun()

    # AUDIO DE CONTEO GLOBAL
    if sala.get("reproduciendo_conteo"):
        balotas_ordenadas = sorted(sala["balotas_salidas"])
        txt_conteo = "Reconteo de balotas: " + ", ".join([str(b) for b in balotas_ordenadas])
        
        st.components.v1.html(f"""
            <script>
                window.speechSynthesis.cancel(); // Limpia antes de empezar
                var msg = new SpeechSynthesisUtterance('{txt_conteo}');
                msg.lang = 'es-ES';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
    else:
        # SCRIPT DE PARADA INMEDIATA
        st.components.v1.html("""
            <script>
                window.speechSynthesis.cancel(); // Esto mata cualquier voz activa al instante
            </script>
        """, height=0)

    # BALOTA ACTUAL CON ANIMACIÓN Y AUDIO SINCRONIZADO
    if sala["balotas_salidas"]:
        n = sala["balotas_salidas"][-1]
        letra = "BINGO"[(n-1)//15]
        
        # Detectamos si es una balota que no hemos "visto" en esta sesión
        es_nueva = st.session_state.get("last_val_anim") != n
        clase_anim = "nueva-balota-anim" if es_nueva else ""

        st.markdown(f"""
            <div class='balota-header {clase_anim}'>
                <p style='margin:0; font-weight:bold; opacity:0.8;'>ÚLTIMA BALOTA EXTRAÍDA</p>
                <h1 style='font-size: 60px; margin:0;'>👑 {letra} - {n} 👑</h1>
                <p style='margin:0;'>Simulación Activa: {len(sala['balotas_salidas'])}/75</p>
            </div>
        """, unsafe_allow_html=True)
        
        # SI ES NUEVA, DISPARAMOS EL SONIDO
        if es_nueva:
         audio_balota_b64 = get_audio_base64("assets/new_balota.mp3")
         if audio_balota_b64:
          st.components.v1.html(f"""
            <script>
                var audioBalota = new Audio("data:audio/mp3;base64,{audio_balota_b64}");
                audioBalota.volume = 0.7;
                audioBalota.play();
                
                setTimeout(function(){{
                    window.speechSynthesis.cancel();
                    var m = new SpeechSynthesisUtterance('{letra}, {n}');
                    m.lang = 'es-ES';
                    window.speechSynthesis.speak(m);
                }}, 1200); // Ajusta el tiempo según lo que dure tu mp3
            </script>
        """, height=0)
        st.session_state.last_val_anim = n

    # PANEL LÍDER
    if st.session_state.user["rol"] == "Lider":
        with st.expander("🎮 PANEL DE CONTROL (LÍDER)", expanded=True):
            col_b, col_m, col_c = st.columns(3)
            
            if col_b.button("⚜️ SORTEAR BALOTA ⚜️", key="btn_lider_sorteo", use_container_width=True):
                with servidor["lock"]:
                    if len(sala["balotas_salidas"]) < 75:
                        gen_balota = LibreriaAleatoria()
                        nueva = gen_balota.generar_entero(1, 75)
                        while nueva in sala["balotas_salidas"]:
                            nueva = gen_balota.generar_entero(1, 75)
                        sala["balotas_salidas"].append(nueva)
                        st.rerun()

            if col_m.button("📊 MAPA VISUAL", key="btn_lider_mapa", use_container_width=True):
                sala["ver_mapa"] = not sala.get("ver_mapa", False)
                st.rerun()

            btn_txt = "🛑 DETENER CONTEO" if sala.get("reproduciendo_conteo") else "🔊 INICIAR CONTEO"
            if col_c.button(btn_txt, key="btn_lider_conteo", use_container_width=True):
                sala["reproduciendo_conteo"] = not sala.get("reproduciendo_conteo", False)
                st.rerun()

    # MAPA VISUAL
    if sala.get("ver_mapa"):
        img_map = get_base64("assets/conteo.png")
        if img_map:
            puntos = ""
            for b in sala["balotas_salidas"]:
                c, f = (b-1)//15, (b-1)%15
                x, y = [20.0, 37.0, 54.0, 71.5, 90.0][c], 10.8 + (f * 6.1)
                puntos += f'<span style="position:absolute;top:{y}%;left:{x}%;transform:translate(-50%,-50%);font-size:14px;color:yellow;text-shadow:0 0 3px black;">⭐</span>'
            st.markdown(f'<div style="position:relative;width:100%;max-width:400px;margin:auto;"><img src="data:image/png;base64,{img_map}" style="width:100%;">{puntos}</div>', unsafe_allow_html=True)

    # GANADOR
    win_id = verificar_ganador(st.session_state.user["cartones"], sala["balotas_salidas"])
    if win_id:
        st.success(f"🎊 ¡BINGO! Cartón {win_id} GANADOR 🔥")
        st.balloons()

    # CARTONES
    st.divider()
    st.header("🎟️ Tus Cartones")
    if len(st.session_state.user["cartones"]) < 3:
        if st.button("🛒 Comprar Cartón (30 CR)"):
            if st.session_state.user["creditos"] >= 30:
                nuevo = crear_carton_logica()
                st.session_state.user["cartones"].append(nuevo)
                st.session_state.user["creditos"] -= 30
                with servidor["lock"]:
                    sala["jugadores"][st.session_state.user["nombre"]] = st.session_state.user["cartones"]
                st.rerun()

    for cart in st.session_state.user["cartones"]:
        st.subheader(f"🍀 Cartón: {cart['id']}")
        cols = st.columns(5, gap="small") 
        for i, L in enumerate("BINGO"):
            with cols[i]:
                st.button(L, key=f"h_{cart['id']}_{L}", disabled=True, use_container_width=True)
                for val in cart[L]:
                    m_key = f"mark_{cart['id']}_{val}"
                    if m_key not in st.session_state: st.session_state[m_key] = False
                    if val == "👑":
                        st.button("👑", key=f"f_{cart['id']}", disabled=True, use_container_width=True)
                    else:
                        lbl = f"✅ {val}" if st.session_state[m_key] else str(val)
                        if st.button(lbl, key=f"b_{cart['id']}_{val}", use_container_width=True):
                            st.session_state[m_key] = not st.session_state[m_key]
                            st.rerun()

    # AUTO-REFRESH SINCRO
    if st.session_state.user["rol"] == "Jugador":
        time.sleep(2)
        st.rerun()
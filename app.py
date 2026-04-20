import streamlit as st
import time
import base64
import os
from utils.aleatorios import LibreriaAleatoria

# 1. CONFIGURACIÓN E INTERFAZ BASE
st.set_page_config(page_title="Bingo Pro One", layout="wide", page_icon="🎰")

# --- MOTOR DE SINCRONIZACIÓN (MEMORIA COMPARTIDA) ---
@st.cache_resource
def obtener_servidor_bingo():
    return {"salas": {}}

servidor = obtener_servidor_bingo()

# --- FUNCIONES DE APOYO ---
def get_base64(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def crear_carton_logica(generador):
    id_carton = generador.generar_entero(1000, 9999)
    carton = {
        'id': id_carton,
        'B': generador.generar_lista_unica(5, 1, 15),
        'I': generador.generar_lista_unica(5, 16, 30),
        'N': generador.generar_lista_unica(4, 31, 45),
        'G': generador.generar_lista_unica(5, 46, 60),
        'O': generador.generar_lista_unica(5, 61, 75)
    }
    carton['N'].insert(2, "👑")
    return carton

# --- INICIALIZACIÓN DE SESIÓN LOCAL ---
if 'user' not in st.session_state:
    st.session_state.user = {"nombre": "", "creditos": 0, "cartones": [], "sala_id": None, "rol": None}

# --- 2. APARTADO DE REGISTRO ---
if not st.session_state.user["nombre"]:
    st.title("🎟️ Registro Bingo Pro One")
    st.image("assets/logo.png", width=300)
    nombre = st.text_input("Ingresa tu nombre para comenzar:")
    if st.button("Registrarme y recibir 100 créditos"):
        if nombre:
            st.session_state.user["nombre"] = nombre
            st.session_state.user["creditos"] = 100
            st.rerun()

# --- 3. LOBBY (UNIRSE O CREAR SALA) ---
elif not st.session_state.user["sala_id"]:
    st.title(f"👋 ¡Hola, {st.session_state.user['nombre']}!")
    st.sidebar.metric("💰 Créditos", st.session_state.user["creditos"])
    
    col_crear, col_unir = st.columns(2)
    
    with col_crear:
        st.subheader("👨‍🏫 Eres el Guía")
        if st.button("Crear Nueva Sala"):
            gen_temp = LibreriaAleatoria()
            codigo = f"SALA-{gen_temp.generar_entero(100, 999)}"
            servidor["salas"][codigo] = {
                "lider": st.session_state.user["nombre"],
                "balotas_salidas": [],
                "jugadores": {}, 
                "semilla": gen_temp.xo
            }
            st.session_state.user["sala_id"] = codigo
            st.session_state.user["rol"] = "Lider"
            st.rerun()
            
    with col_unir:
        st.subheader("🎮 Eres Jugador")
        codigo_input = st.text_input("Código de Sala:")
        if st.button("Unirse a la Partida"):
            if codigo_input in servidor["salas"]:
                st.session_state.user["sala_id"] = codigo_input
                st.session_state.user["rol"] = "Jugador"
                st.rerun()
            else:
                st.error("La sala no existe.")

# --- 4. INTERFAZ DE JUEGO ACTIVA ---
else:
    sala_id = st.session_state.user["sala_id"]
    sala = servidor["salas"][sala_id]
    rol = st.session_state.user["rol"]
    
    st.sidebar.title(f"📍 Sala: {sala_id}")
    st.sidebar.write(f"Rol: **{rol}**")
    
    if st.sidebar.button("🚪 Salir de la Sala"):
        st.session_state.user["sala_id"] = None
        st.session_state.user["cartones"] = []
        st.rerun()

    # ==========================================
    # PANEL DE CONTROL DEL LÍDER
    # ==========================================
    if rol == "Lider":
        st.header("🎮 Panel de Control del Líder")
    
        # --- MONITOREO DE GANADORES ---
        ganadores = []
        balotas_reales = set(sala["balotas_salidas"])

        for usuario, lista_cartones in sala["jugadores"].items():
            for carton in lista_cartones:
                # Aplanamos los números del cartón para verificar
                numeros_del_carton = []
                for letra in "BINGO":
                    for num in carton[letra]:
                        if num != "👑": numeros_del_carton.append(num)
                
                if all(n in balotas_reales for n in numeros_del_carton):
                    ganadores.append(f"¡{usuario} (ID: {carton['id']})!")

        if ganadores:
            st.success(f"🔥 BINGO DETECTADO: {', '.join(ganadores)}")
            st.balloons()
        else:
            st.info(f"Partida en curso. Balotas cantadas: {len(sala['balotas_salidas'])}/75")
        
        st.divider()
        
        # --- CONTROLES DE LANZAMIENTO ---
        c1, c2 = st.columns([1, 2])
        
        with c1:
            if st.button("🎰 Lanzar Siguiente Balota"):
                if len(sala["balotas_salidas"]) < 75:
                    import time
                    gen_sala = LibreriaAleatoria(int(time.time()))
                    encontrada = False
                    while not encontrada:
                        n = gen_sala.generar_entero(1, 75)
                        if n not in sala["balotas_salidas"]:
                            sala["balotas_salidas"].append(n)
                            encontrada = True
                            letra = 'B' if n <= 15 else 'I' if n <= 30 else 'N' if n <= 45 else 'G' if n <= 60 else 'O'
                            st.session_state.texto_a_decir = f"{letra} {n}"
                            time.sleep(1.0)
                    st.rerun()
                else:
                    st.warning("Ya salieron todas las balotas.")

            if sala["balotas_salidas"]:
                n_act = sala["balotas_salidas"][-1]
                letra_act = 'B' if n_act <= 15 else 'I' if n_act <= 30 else 'N' if n_act <= 45 else 'G' if n_act <= 60 else 'O'
                st.metric("Última Balota", f"{letra_act} {n_act}")

        with c2:
            if st.button("📊 Ver Conteo Global"):
                st.session_state.ver_conteo = not st.session_state.get("ver_conteo", False)
            
            if st.session_state.get("ver_conteo"):
                st.write("### 📊 Mapa de Balotas Oficiales")
                img_data = get_base64("assets/conteo.png")
                if img_data:
                    pos_x = [20.0, 37.0, 54.0, 71.5, 90.0] 
                    y_base = 10.8
                    dy = 6.1
                    puntos = ""
                    for n in sala["balotas_salidas"]:
                        c_idx = (n - 1) // 15
                        f_idx = (n - 1) % 15
                        x = pos_x[c_idx]
                        y = y_base + (f_idx * dy)
                        puntos += f'<span style="position:absolute;top:{y}%;left:{x}%;transform:translate(-50%,-50%);font-size:20px;text-shadow:0 0 8px #000;z-index:99;">⭐</span>'

                    html_final = f'<div style="position:relative;width:100%;max-width:500px;margin:0 auto;"><img src="data:image/png;base64,{img_data}" style="width:100%;display:block;border-radius:10px;">{puntos}</div>'
                    st.markdown(html_final, unsafe_allow_html=True)

        # --- CONTROLES DE AUDIO ---
        st.subheader("🔊 Controles de Voz")
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("🎤 Cantar Historial"):
                texto_historial = "Balotas que han salido: " + ", ".join(map(str, sorted(sala["balotas_salidas"])))
                st.session_state.texto_a_decir = texto_historial
                st.rerun()
        with ca2:
            if st.button("🛑 Detener Audio"):
                st.components.v1.html("<script>window.speechSynthesis.cancel();</script>", height=0)
        st.divider()

    # ==========================================
    # MANEJO CENTRAL DE AUDIO (JavaScript)
    # ==========================================
    if "texto_a_decir" in st.session_state:
        st.components.v1.html(f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{st.session_state.texto_a_decir}');
                msg.lang = 'es-ES';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
        del st.session_state.texto_a_decir

    # ==========================================
    # VISTA DE JUEGO (PARA TODOS)
    # ==========================================
    st.header("🃏 Tus Cartones")
    
    # Compra de cartones (Líder y Jugador pueden jugar)
    if len(st.session_state.user["cartones"]) < 3:
        if st.button(f"Comprar Cartón (30 CR) - Tienes {st.session_state.user['creditos']}"):
            if st.session_state.user["creditos"] >= 30:
                gen_c = LibreriaAleatoria()
                nuevo_c = crear_carton_logica(gen_c)
                st.session_state.user["cartones"].append(nuevo_c)
                st.session_state.user["creditos"] -= 30
                # Sincronizamos con el servidor para que el Líder detecte ganadores
                sala["jugadores"][st.session_state.user["nombre"]] = st.session_state.user["cartones"]
                st.rerun()

    if sala["balotas_salidas"]:
        n_j = sala["balotas_salidas"][-1]
        st.info(f"🚨 ÚLTIMA BALOTA: {n_j}")

    # Renderizar cartones
    for cart in st.session_state.user["cartones"]:
        st.divider()
        st.subheader(f"Cartón ID: {cart['id']}")
        cols = st.columns(5)
        letras = "BINGO"
        for i, L in enumerate(letras):
            with cols[i]:
                st.button(L, key=f"head_{cart['id']}_{L}", disabled=True, use_container_width=True)
                for val in cart[L]:
                    m_key = f"mark_{cart['id']}_{val}"
                    if val == "👑":
                        st.button("👑", key=m_key, disabled=True, use_container_width=True)
                    else:
                        if f"lista_marcados_{cart['id']}" not in st.session_state:
                            st.session_state[f"lista_marcados_{cart['id']}"] = set()
                        marcado = val in st.session_state[f"lista_marcados_{cart['id']}"]
                        label = "✅" if marcado else str(val)
                        if st.button(label, key=m_key, use_container_width=True):
                            if marcado: st.session_state[f"lista_marcados_{cart['id']}"].remove(val)
                            else: st.session_state[f"lista_marcados_{cart['id']}"].add(val)
                            st.rerun()
# 🎰 Bingo Pro One - Simulador Estocástico

Este proyecto es una aplicación de Bingo profesional desarrollada en **Python** y **Streamlit**, diseñada para funcionar como un sistema de sorteo en tiempo real con capacidad para múltiples jugadores simultáneos.

## 🚀 Características
* **Motor Aleatorio Propio:** Implementación de un Generador Congruencial Lineal (LGC).
* **Interfaz Dinámica:** Tablero de control real con marcado automático sobre imagen.
* **Sistema de Créditos:** Gestión de compra de cartones para jugadores.
* **Ambiente Profesional:** Incluye música de fondo y cantado de balotas por voz (TTS).

## 🧠 Sustento Técnico (Modelamiento y Simulación)
Para garantizar la equidad y aleatoriedad del juego, no se utilizó la librería estándar de Python. En su lugar, se implementó una **Librería Aleatoria** basada en el método de congruencia lineal:

$$X_{n+1} = (aX_n + c) \mod m$$

### Parámetros utilizados:
* **Semilla ($X_0$):** Dinámica, basada en el reloj del sistema (Unix timestamp en milisegundos).
* **Multiplicador ($a$):** 1103515245
* **Incremento ($c$):** 12345
* **Módulo ($m$):** $2^{31}$

Este modelo asegura una distribución uniforme y un periodo lo suficientemente largo para sesiones de juego extensas sin repeticiones cíclicas prematuras.

## 🛠️ Estructura del Proyecto
* `app.py`: Punto de entrada de la aplicación y lógica de interfaz.
* `utils/aleatorios.py`: Motor matemático del simulador.
* `assets/`: Recursos visuales y auditivos (Logo, Cartón, Tablero, Música).
* `.streamlit/config.toml`: Configuración estética del tema visual.

## 📦 Instalación y Despliegue
1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `streamlit run app.py`

Desarrollado para la clase de **Modelamiento y Simulación**.
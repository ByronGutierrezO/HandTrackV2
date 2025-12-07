# 🖱️ Sistema de Control Gestual Simulado para Interfaces Industriales usando OpenCV y Mediapipe

Autores: Byron Gutierrez -  Mauricio Pilapaña.

Un controlador de mouse sin contacto que utiliza visión por computadora y reconocimiento de gestos de mano. Este proyecto permite mover el cursor y hacer clic simplemente usando tu cámara web, ideal para presentaciones o interacciones sin contacto.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)

## 📋 Características

- **Rastreo de Mano en Tiempo Real:** Utiliza MediaPipe para una detección rápida y precisa de los puntos clave de la mano.
- **Movimiento Suave:** Implementa un algoritmo de suavizado (exponential moving average) para evitar que el cursor tiemble.
- **Mapeo de Pantalla Inteligente:** Usa un recuadro de control (padding) para que no tengas que estirar el brazo hasta los bordes de la cámara para alcanzar las esquinas del monitor.
- **Gesto de Clic:** Realiza un clic izquierdo haciendo un gesto de "pellizco" (unir pulgar e índice).
- **Prevención de Doble Clic:** Sistema de bloqueo (`click_lock`) para evitar clics múltiples accidentales.

## 🛠️ Requisitos Previos

Necesitas tener Python instalado (versión 3.11 o superior recomendada). Las librerías necesarias son:

- `opencv-python`: Para capturar el video y procesar imágenes.
- `mediapipe`: Para detectar la mano.
- `pyautogui`: Para controlar el mouse del sistema operativo.
- `numpy`: Para cálculos de mapeo de coordenadas.

## 🚀 Instalación

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/nombre-del-repo.git](https://github.com/TU_USUARIO/nombre-del-repo.git)
   cd nombre-del-repo

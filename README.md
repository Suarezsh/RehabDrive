# 🧠🚗 RehabDrive – Videojuego Terapéutico Asistido por IA

### 🎮 Rehabilitación cervical interactiva con control de cabeza e inteligencia artificial

**Autor:** [Suarez SH](https://sfysh.com/)  
**Repositorio:** [https://github.com/Suarezsh/RehabDrive](https://github.com/Suarezsh/RehabDrive)

---

## 🧩 Descripción General

**RehabDrive** es un videojuego terapéutico que combina movimiento físico, visión por computadora y asistencia virtual con IA, diseñado para apoyar la **rehabilitación cervical, motora y cognitiva**.  
El jugador controla un vehículo inclinando la cabeza hacia los lados, mientras esquiva obstáculos y avanza por diferentes niveles de dificultad.

El sistema mide métricas terapéuticas como asimetrías cervicales, tiempo de reacción y distancia recorrida.  
Además, incluye un **asistente inteligente “Doc IA”** que analiza el desempeño y brinda retroalimentación motivacional o recomendaciones terapéuticas.

---

## ⚙️ Tecnologías

- **Pygame:** motor del juego y control de colisiones.  
- **OpenCV + MediaPipe:** detección facial y cálculo de inclinación de cabeza.  
- **Gemini API (Google GenAI):** inteligencia artificial para análisis y consejos.  
- **NumPy:** cálculos y métricas.  
- **Asyncio:** asincronía entre el juego y la IA.

---

## 🧠 Fundamento Terapéutico

RehabDrive transforma la fisioterapia tradicional en una experiencia divertida e inmersiva.  
El movimiento natural de la cabeza se convierte en un control activo del juego, lo que estimula el entrenamiento motor, la coordinación y la postura.

### Beneficios terapéuticos:
- Mejora la movilidad y fuerza cervical.  
- Favorece la coordinación ojo-cabeza.  
- Corrige posturas y reduce tensión muscular.  
- Estimula la atención y la memoria motriz.  
- Acompaña emocionalmente al paciente mediante IA.

---

## ⚕️ Aplicaciones y Casos de Uso

RehabDrive puede aplicarse en rehabilitación y entrenamiento de:

- **Trastornos cervicales:** artrosis, contracturas, tortícolis.  
- **Rehabilitación neurológica:** ACV leve, parálisis facial, traumatismos craneales leves.  
- **Trastornos cognitivos:** TEA, TDAH (mejora de atención y coordinación).  
- **Equilibrio postural:** vértigo, inestabilidad vestibular.  
- **Prevención:** corrección de postura por uso prolongado de pantallas.

---

## 🎯 Características Destacadas

✅ Control del vehículo mediante inclinación de cabeza.  
✅ Retroalimentación inteligente con el asistente “Doc IA”.  
✅ Panel con métricas de desempeño y progreso.  
✅ Niveles progresivos: fácil, medio y difícil.  
✅ Análisis en tiempo real del movimiento y la simetría.  
✅ Diseño accesible y adaptable a distintas edades.  

---

## 🧩 Asistente Inteligente “Doc IA”

El módulo **Doc IA** utiliza la API de **Gemini** para analizar los datos del jugador y ofrecer comentarios personalizados.  
Puede detectar si existe una inclinación dominante, aconsejar sobre pausas activas y generar frases de motivación.

**Ejemplo de interacción:**  
> “Tu inclinación derecha está un poco más marcada. Intenta equilibrar ambos lados en la próxima sesión. ¡Excelente trabajo!”

---

## 📊 Métricas y Seguimiento

El sistema registra:
- Distancia recorrida.  
- Nivel de asimetría entre lados.  
- Tiempo de reacción ante estímulos.  
- Número total de movimientos.  
- Duración total de la sesión.  

Estas métricas pueden ser usadas por terapeutas para evaluar la evolución del paciente de forma continua.

---

## 🧠 Arquitectura del Sistema

```
┌──────────────────────────────┐
│          RehabDrive          │
├──────────────────────────────┤
│ 🎥 MediaPipe / OpenCV        │ → Detección facial y ángulos
│ 🎮 Pygame Engine             │ → Control del carro y colisiones
│ 📊 Monitor de progreso       │ → Métricas y análisis
│ 💬 Doc IA (Gemini)           │ → Asistente inteligente
└──────────────────────────────┘
```

---

## 🚀 Instalación y Ejecución

**Requisitos previos:**  
- Python 3.10 o superior  
- Cámara web funcional  
- Conexión a internet (para la IA)

**Instalación de dependencias:**  
```bash
pip install pygame opencv-python mediapipe google-generativeai numpy
```

**Ejecución del proyecto:**  
```bash
python rehabdrive.py
```

**Estructura de carpetas sugerida:**
```
RehabDrive/
├── img/
│   ├── coche.png
│   ├── coche2.png
│   ├── cocheyo.png
│   └── colision.png
├── rehabdrive.py
└── README.md
```

---

## 🌟 Futuras Mejoras

- Integración multiplataforma (Android y Windows).  
- Incorporación de sensores externos (IMU, giroscopio).  
- Registro de progreso en la nube.  
- Módulos de relajación y respiración guiada.  
- Expansión del sistema de niveles y escenarios.  

---

## 📜 Licencia

Este proyecto es de código abierto bajo la **licencia MIT**.  
Puede ser utilizado y adaptado para fines educativos, clínicos o de investigación con la debida atribución.

---

## 👨‍💻 Autor

**Desarrollado por:** [Suarez SH](https://sfysh.com/)  
**GitHub:** [@Suarezsh](https://github.com/Suarezsh)  

> “Conduce tu recuperación. La tecnología al servicio de la rehabilitación humana.”

---

### 🧩 Palabras Clave
rehabilitación digital · inteligencia artificial · mediapipe · neurorehabilitación · pygame · IA en salud · fisioterapia interactiva · rehabdrive · doc ia · videojuego terapéutico

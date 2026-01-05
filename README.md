# 🧠🚗 RehabDrive – Videojuego Terapéutico

### 🎮 Rehabilitación cervical interactiva con control de cabeza

**Repositorio:** [https://github.com/Suarezsh/RehabDrive](https://github.com/Suarezsh/RehabDrive)

---

## 🧩 Descripción General

**RehabDrive** es un videojuego terapéutico que combina movimiento físico y visión por computadora, diseñado para apoyar la **rehabilitación cervical, motora y cognitiva**.
El jugador controla un vehículo inclinando la cabeza hacia los lados, mientras esquiva obstáculos y avanza por diferentes niveles de dificultad.

El sistema mide métricas terapéuticas como asimetrías cervicales, tiempo de reacción y distancia recorrida para monitorear el progreso.

---

## ⚙️ Tecnologías

- **Pygame:** motor del juego y control de colisiones.
- **OpenCV + MediaPipe:** detección facial y cálculo de inclinación de cabeza.
- **NumPy:** cálculos y métricas.

---

## 🧠 Fundamento Terapéutico

RehabDrive transforma la fisioterapia tradicional en una experiencia divertida e inmersiva.
El movimiento natural de la cabeza se convierte en un control activo del juego, estimulando el entrenamiento motor, la coordinación y la postura.

### Beneficios terapéuticos:
- Mejora la movilidad y fuerza cervical.
- Favorece la coordinación ojo-cabeza.
- Corrige posturas y reduce tensión muscular.
- Estimula la atención y la memoria motriz.

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
✅ Panel con métricas de desempeño y progreso.
✅ Niveles progresivos: fácil, medio y difícil.
✅ Análisis en tiempo real del movimiento y la simetría.
✅ Diseño accesible y adaptable a distintas edades.
✅ Vista en vivo de la cámara facial.

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
└──────────────────────────────┘
```

---

## 🚀 Instalación y Ejecución

**Requisitos previos:**
- Python 3.10 o superior
- Cámara web funcional

**Instalación de dependencias:**
```bash
pip install pygame opencv-python mediapipe numpy
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

## 🎮 Cómo Jugar

1. Asegúrate de tener una cámara web conectada.
2. Ejecuta `python rehabdrive.py`.
3. Selecciona un nivel de dificultad (Fácil, Intermedio, Difícil).
4. Inclina la cabeza hacia la izquierda o derecha para mover el carro y esquivar obstáculos.
5. Evita colisiones para acumular distancia.
6. Monitorea tus métricas en el panel izquierdo y la vista facial en el derecho.

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
rehabilitación digital · mediapipe · neurorehabilitación · pygame · fisioterapia interactiva · rehabdrive · videojuego terapéutico

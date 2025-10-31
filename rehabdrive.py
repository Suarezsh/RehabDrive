import pygame
import random
import sys
import cv2
import numpy as np
import math
import mediapipe as mp
import os
import time 

import asyncio 
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor

GEMINI_API_TOKEN = "AIzaSyDCX3ll3Tethn62A1RRAW-POqKAnMLgaqQ" 
ASSISTANT_NAME = "Doc IA"

try:
    client = genai.Client(api_key=GEMINI_API_TOKEN)
    ia_conectada = True
except Exception as e:
    print(f"Error al inicializar el cliente Doc IA: {e}")
    ia_conectada = False

executor = ThreadPoolExecutor(max_workers=2)

SISTEMA_PROMPT = (
    f"Eres un Asistente IA terapéutico llamado '{ASSISTANT_NAME}' para un juego de rehabilitación cervical. "
    "Tu objetivo es: 1. Dar consejos breves y precisos (máximo 50 palabras) sobre el rendimiento del usuario, analizando **SOLO** la Distancia (km) y la Asimetría de Inclinación (conteo Izquierda/Derecha) de la última partida en un nivel específico. 2. Responder cualquier pregunta de cultura general o cualquier otro tema si la pregunta del usuario no es sobre el juego, en caso  te pregunten de tu creador es Suarez sh. "
    "Tu tono debe ser de apoyo y profesional. Los datos de juego a considerar son: Distancia, Nivel, Total_Mov_Izq, Total_Mov_Der."
)

ia_task_queue = None 
ia_response_queue = [] 
ia_escribiendo = False

records_metrics = {
    'FÁCIL': {'Distancia': 0.0, 'Total_Mov_Izq': 0, 'Total_Mov_Der': 0},
    'INTERMEDIO': {'Distancia': 0.0, 'Total_Mov_Izq': 0, 'Total_Mov_Der': 0},
    'DIFÍCIL': {'Distancia': 0.0, 'Total_Mov_Izq': 0, 'Total_Mov_Der': 0},
}

records = {'FÁCIL': 0, 'INTERMEDIO': 0, 'DIFÍCIL': 0}

def call_gemini_api(prompt, nivel_actual, last_metrics):
    if not ia_conectada:
        return f"ERROR: La API de Doc IA no está conectada. Revisa tu clave y conexión."
        
    metrica_contexto = (
        f"Última partida registrada en Nivel {nivel_actual}: "
        f"Distancia recorrida: {last_metrics['Distancia']:.1f} km, "
        f"Movimientos Izq: {last_metrics['Total_Mov_Izq']}, "
        f"Movimientos Der: {last_metrics['Total_Mov_Der']}."
    )
    
    full_prompt = (
        f"{SISTEMA_PROMPT}\n\n"
        f"Contexto de la última partida: {metrica_contexto}\n"
        f"Pregunta del usuario: {prompt}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error en la API: No pude obtener una respuesta. ({e})"

ANCHO_PANTALLA = 1500 
ALTO_PANTALLA = 800

ANCHO_CARRETERA = 400
ANCHO_COLUMNA = (ANCHO_PANTALLA - ANCHO_CARRETERA) // 2

POS_X_PANEL = 0
POS_X_CARRETERA = ANCHO_COLUMNA
POS_X_CAMARA = ANCHO_COLUMNA + ANCHO_CARRETERA 

ALTO_CAMARA_VIEW = 150 
Y_INICIO_CHAT = 220 
ALTO_AREA_CHAT = ALTO_PANTALLA - Y_INICIO_CHAT - 100 
ALTO_INPUT_CHAT = 40 

NEGRO = (15, 15, 15)
BLANCO = (240, 240, 240)
GRIS_CARRETERA = (100, 100, 100) 
AZUL_FONDO = (30, 30, 50) 
GRIS_PANEL = (50, 50, 70)
GRIS_CHAT = (70, 70, 90) 
ROJO_BTN = (200, 50, 50)
VERDE_BTN = (50, 200, 50)
AZUL_BTN = (50, 50, 200)

COLOR_BURBUJA_USER = (37, 211, 102)  
COLOR_BURBUJA_IA = (80, 80, 100)     

RUTA_IMAGENES = './img/'

DIFICULTADES = {
    'FÁCIL': {'velocidad_juego': 4, 'intervalo': 70, 'sensibilidad': 4.0},
    'INTERMEDIO': {'velocidad_juego': 7, 'intervalo': 50, 'sensibilidad': 6.0},
    'DIFÍCIL': {'velocidad_juego': 10, 'intervalo': 35, 'sensibilidad': 8.0},
}

pygame.init()
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Carrera Terapéutica con Asistente IA")
RELOJ = pygame.time.Clock()
FUENTE_TITULO = pygame.font.Font(None, 50)
FUENTE_SUBTITULO = pygame.font.Font(None, 35)
FUENTE_NORMAL = pygame.font.Font(None, 30)
FUENTE_SMALL = pygame.font.Font(None, 20) 

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
CAP = cv2.VideoCapture(0)

estado_juego = 'MENU'
nivel_actual = 'FÁCIL'
velocidad_carro = 10
UMBRAL_INCLINACION = DIFICULTADES[nivel_actual]['sensibilidad']

datos_analisis = {
    'tiempo_reaccion_total': 0,
    'contador_enemigos_creados': 0,
    'inclinacion_izq_total': 0,
    'inclinacion_der_total': 0,
    'movimientos_izq_count': 0,  
    'movimientos_der_count': 0,  
    'frames_neutros': 0,
    'frames_totales_juego': 0
}

def cargar_imagen(nombre_archivo, ancho, alto):
    ruta = os.path.join(RUTA_IMAGENES, nombre_archivo)
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.scale(imagen, (ancho, alto))
    except pygame.error:
        superficie_error = pygame.Surface([ancho, alto], pygame.SRCALPHA)
        superficie_error.fill((255, 0, 255, 150))
        return superficie_error

IMAGEN_CARRO_JUGADOR = cargar_imagen('cocheyo.png', 50, 90)
IMAGEN_COCHE_1 = cargar_imagen('coche.png', 50, 90)
IMAGEN_COCHE_2 = cargar_imagen('coche2.png', 50, 90)
IMAGEN_COLISION = cargar_imagen('colision.png', 80, 80)
IMAGENES_ENEMIGOS = [IMAGEN_COCHE_1, IMAGEN_COCHE_2]

class Carrito(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IMAGEN_CARRO_JUGADOR
        self.rect = self.image.get_rect()
        self.rect.x = POS_X_CARRETERA + ANCHO_CARRETERA // 2 - self.rect.width // 2
        self.rect.y = ALTO_PANTALLA - 120

    def mover(self, direccion):
        nueva_x = self.rect.x + direccion * velocidad_carro
        limite_izquierdo = POS_X_CARRETERA
        limite_derecho = POS_X_CARRETERA + ANCHO_CARRETERA - self.rect.width
        self.rect.x = max(limite_izquierdo, min(nueva_x, limite_derecho))

class CocheEnemigo(pygame.sprite.Sprite):
    def __init__(self, velocidad_juego):
        super().__init__()
        self.image = random.choice(IMAGENES_ENEMIGOS)
        self.rect = self.image.get_rect()
        self.velocidad = velocidad_juego
        min_x = POS_X_CARRETERA
        max_x = POS_X_CARRETERA + ANCHO_CARRETERA - self.rect.width
        self.rect.x = random.randint(min_x, max_x)
        self.rect.y = -self.rect.height
        self.frame_aparicion = pygame.time.get_ticks() 

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.y > ALTO_PANTALLA:
            self.kill()

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_base, color_hover, accion, grupo='NORMAL'):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.accion = accion
        self.color_actual = color_base
        self.grupo = grupo

    def dibujar(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.color_actual = self.color_hover
        else:
            self.color_actual = self.color_base
        pygame.draw.rect(pantalla, self.color_actual, self.rect, border_radius=5)
        texto_superficie = FUENTE_NORMAL.render(self.texto, True, BLANCO)
        texto_rect = texto_superficie.get_rect(center=self.rect.center)
        pantalla.blit(texto_superficie, texto_rect)

    def click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos):
            self.accion()
            return True
        return False


class InputBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w - 45, h)
        self.color = GRIS_PANEL
        self.text = ""
        self.activo = False
        self.btn_enviar_rect = pygame.Rect(x + w - 40, y, 40, h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) or self.btn_enviar_rect.collidepoint(event.pos):
                self.activo = True
            else:
                self.activo = False
        if event.type == pygame.KEYDOWN and self.activo:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if FUENTE_SMALL.size(self.text + event.unicode)[0] < self.rect.width - 10:
                    self.text += event.unicode
        return None

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect, border_radius=5)
        borde_color = AZUL_BTN if self.activo else GRIS_PANEL
        pygame.draw.rect(pantalla, borde_color, self.rect, 2, border_radius=5)
        txt_surface = FUENTE_SMALL.render(self.text, True, BLANCO)
        pantalla.blit(txt_surface, (self.rect.x + 5, self.rect.y + 10))
        pygame.draw.rect(pantalla, VERDE_BTN, self.btn_enviar_rect, border_radius=5)
        enviar_texto = FUENTE_SMALL.render("↑", True, BLANCO)
        pantalla.blit(enviar_texto, (self.btn_enviar_rect.x + 10, self.btn_enviar_rect.y + 7))

class ChatBox:
    def __init__(self, rect):
        self.rect = rect
        self.historial = []
        self.scroll_y = 0
        self.line_height = 20
        self.max_content_height = self.rect.height

    def añadir_mensaje(self, remitente, texto):
        palabras = texto.split()
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            if FUENTE_SMALL.size(linea_actual + " " + palabra)[0] < self.rect.width - 40:
                linea_actual += " " + palabra
            else:
                lineas.append(linea_actual.strip())
                linea_actual = palabra
        lineas.append(linea_actual.strip())
        for linea in lineas:
            self.historial.append({'remitente': remitente, 'texto': linea})
        total_content_height = len(self.historial) * self.line_height
        if total_content_height > self.max_content_height:
            self.scroll_y = self.max_content_height - total_content_height

    def dibujar(self, pantalla, ia_escribiendo):
        pygame.draw.rect(pantalla, GRIS_CHAT, self.rect, border_radius=5)
        inner_rect = self.rect.inflate(-10, -10)
        pantalla.set_clip(inner_rect)
        y_pos = inner_rect.y + self.scroll_y
        for mensaje in self.historial:
            remitente = mensaje['remitente']
            texto = mensaje['texto']
            color_fondo = COLOR_BURBUJA_USER if remitente == 'Usuario' else COLOR_BURBUJA_IA
            color_texto = NEGRO if remitente == 'Usuario' else BLANCO
            texto_superficie = FUENTE_SMALL.render(texto, True, color_texto)
            texto_rect = texto_superficie.get_rect()
            if remitente == ASSISTANT_NAME:
                texto_rect.x = inner_rect.x + 5
            else:
                texto_rect.right = inner_rect.right - 5
            texto_rect.y = y_pos
            burbuja_rect = texto_rect.inflate(10, 5)
            pygame.draw.rect(pantalla, color_fondo, burbuja_rect, border_radius=5)
            pantalla.blit(texto_superficie, texto_rect)
            y_pos += self.line_height
        if ia_escribiendo:
            texto_escribiendo = f"{ASSISTANT_NAME} escribiendo..."
            texto_surf = FUENTE_SMALL.render(texto_escribiendo, True, BLANCO)
            texto_rect = texto_surf.get_rect(x=inner_rect.x + 5, y=y_pos)
            burbuja_rect = texto_rect.inflate(10, 5)
            pygame.draw.rect(pantalla, COLOR_BURBUJA_IA, burbuja_rect, border_radius=5)
            pantalla.blit(texto_surf, texto_rect)
            if y_pos + self.line_height > inner_rect.y + inner_rect.height:
                self.scroll_y -= self.line_height
        pantalla.set_clip(None)

    def manejar_scroll(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos):
            total_content_height = len(self.historial) * self.line_height
            if ia_escribiendo:
                total_content_height += self.line_height
            if total_content_height > self.max_content_height:
                max_scroll = self.max_content_height - total_content_height
                if evento.button == 4:
                    self.scroll_y = min(self.scroll_y + self.line_height * 3, 0)
                elif evento.button == 5:
                    self.scroll_y = max(self.scroll_y - self.line_height * 3, max_scroll)

def dibujar_botones_juego(pantalla):
    global estado_juego
    botones_juego = []
    ancho_btn = ANCHO_COLUMNA - 40
    alto_btn = 50
    x_pos = POS_X_PANEL + 20
    y_pos = ALTO_PANTALLA - 150
    def iniciar_juego():
        global estado_juego
        estado_juego = 'JUGANDO'
    def pausar_juego():
        global estado_juego
        estado_juego = 'PAUSA'
    def reanudar_juego():
        global estado_juego
        estado_juego = 'JUGANDO'
    if estado_juego == 'MENU' or estado_juego == 'MUERTE':
        btn_iniciar = Boton(x_pos, y_pos, ancho_btn, alto_btn, "INICIAR JUEGO", VERDE_BTN, (0, 255, 0), iniciar_juego)
        botones_juego.append(btn_iniciar)
    elif estado_juego == 'JUGANDO':
        btn_pausa = Boton(x_pos, y_pos, ancho_btn, alto_btn, "PAUSA", ROJO_BTN, (255, 0, 0), pausar_juego)
        botones_juego.append(btn_pausa)
    elif estado_juego == 'PAUSA':
        btn_reanudar = Boton(x_pos, y_pos, ancho_btn, alto_btn, "REANUDAR", VERDE_BTN, (0, 255, 0), reanudar_juego)
        botones_juego.append(btn_reanudar)
    for btn in botones_juego:
        btn.dibujar(pantalla)
    return botones_juego

def dibujar_panel_control(pantalla, puntuacion, datos_analisis_final):
    global nivel_actual
    panel_rect = pygame.Rect(POS_X_PANEL, 0, ANCHO_COLUMNA, ALTO_PANTALLA)
    pygame.draw.rect(pantalla, GRIS_PANEL, panel_rect)
    titulo = FUENTE_TITULO.render("HUD DE CONTROL", True, BLANCO)
    pantalla.blit(titulo, (POS_X_PANEL + ANCHO_COLUMNA // 2 - titulo.get_width() // 2, 30))
    y_pos = 100
    texto_sub = FUENTE_SUBTITULO.render("MÉTRICAS DE DISTANCIA", True, BLANCO)
    pantalla.blit(texto_sub, (POS_X_PANEL + 20, y_pos))
    y_pos += 40
    texto_actual = FUENTE_NORMAL.render(f"  > Distancia Actual: {int(puntuacion)} km", True, BLANCO)
    pantalla.blit(texto_actual, (POS_X_PANEL + 20, y_pos))
    y_pos += 30
    texto_record = FUENTE_NORMAL.render(f"  > Récord ({nivel_actual}): {int(records[nivel_actual])} km", True, BLANCO)
    pantalla.blit(texto_record, (POS_X_PANEL + 20, y_pos))
    y_pos += 60
    texto_sub = FUENTE_SUBTITULO.render("ANÁLISIS CERVICAL", True, BLANCO)
    pantalla.blit(texto_sub, (POS_X_PANEL + 20, y_pos))
    y_pos += 40
    porc_izq = datos_analisis_final['Porc_Mov_Izq']
    porc_der = datos_analisis_final['Porc_Mov_Der']

    
    texto_asimetria_c = FUENTE_NORMAL.render(f"  > Asimetría C. (L/R): {porc_izq:.1f}% / {porc_der:.1f}%", True, BLANCO)
    pantalla.blit(texto_asimetria_c, (POS_X_PANEL + 20, y_pos))
    y_pos += 30

    texto_total_mov = FUENTE_NORMAL.render(f"  > Total Movimientos: {datos_analisis_final['Total_Movs']}", True, BLANCO)
    pantalla.blit(texto_total_mov, (POS_X_PANEL + 20, y_pos))
    y_pos += 30
    
    datos_mostrar_extra = {
        'T. Reacción Prom': (datos_analisis_final['T. Reacción'], " ms"), 
        'Asimetría (Grados)': (datos_analisis_final['Asimetría'], " °"),
    }
    for key, (value, unidad) in datos_mostrar_extra.items():
        texto_dato = FUENTE_NORMAL.render(f"  > {key}: {value:.1f}{unidad}", True, BLANCO)
        pantalla.blit(texto_dato, (POS_X_PANEL + 20, y_pos))
        y_pos += 30
    y_pos += 30
    
    texto_sub = FUENTE_SUBTITULO.render("DIFICULTAD", True, BLANCO)
    pantalla.blit(texto_sub, (POS_X_PANEL + 20, y_pos))
    y_pos += 40
    
    botones_nivel = []
    x_btn = POS_X_PANEL + 10
    ancho_btn = (ANCHO_COLUMNA - 40) // 3
    
    def cambiar_nivel(n):
        global nivel_actual, estado_juego, UMBRAL_INCLINACION
        nivel_actual = n
        UMBRAL_INCLINACION = DIFICULTADES[nivel_actual]['sensibilidad']
        if estado_juego == 'JUGANDO' or estado_juego == 'PAUSA':
            estado_juego = 'MENU'
    
    for nivel in DIFICULTADES.keys():
        color = VERDE_BTN if nivel == nivel_actual else AZUL_BTN
        
        btn = Boton(x_btn, y_pos, ancho_btn, 40, nivel, color, (color[0]+20, color[1]+20, color[2]+20), lambda n=nivel: cambiar_nivel(n), grupo='NIVEL')
        botones_nivel.append(btn)
        btn.dibujar(pantalla)
        x_btn += ancho_btn + 10
        
    y_pos += 60

    texto_sub = FUENTE_SUBTITULO.render("CONTROL FACIAL", True, BLANCO)
    pantalla.blit(texto_sub, (POS_X_PANEL + 20, y_pos))
    y_pos += 40
    
    texto_sens = FUENTE_NORMAL.render(f"  > Sensibilidad: {UMBRAL_INCLINACION}°", True, BLANCO)
    pantalla.blit(texto_sens, (POS_X_PANEL + 20, y_pos))
    
    return botones_nivel

def dibujar_escenario(pantalla, todos_los_sprites, velocidad_juego, estado_juego, colision_pos):
    
    carretera_rect = pygame.Rect(POS_X_CARRETERA, 0, ANCHO_CARRETERA, ALTO_PANTALLA)
    pygame.draw.rect(pantalla, GRIS_CARRETERA, carretera_rect)

    x_central = POS_X_CARRETERA + ANCHO_CARRETERA // 2
    
    if estado_juego == 'JUGANDO':
        velocidad_lineas = velocidad_juego * 10
        for i in range(0, ALTO_PANTALLA, 80):
            linea_y = (i + pygame.time.get_ticks() * velocidad_lineas // 100) % ALTO_PANTALLA
            pygame.draw.line(pantalla, BLANCO, (x_central, linea_y), (x_central, linea_y + 40), 5)
    
    pygame.draw.line(pantalla, NEGRO, (POS_X_CARRETERA, 0), (POS_X_CARRETERA, ALTO_PANTALLA), 10)
    pygame.draw.line(pantalla, NEGRO, (POS_X_CARRETERA + ANCHO_CARRETERA, 0), (POS_X_CARRETERA + ANCHO_CARRETERA, ALTO_PANTALLA), 10)

    todos_los_sprites.draw(pantalla)

   
    if estado_juego == 'MUERTE' and colision_pos != (0, 0):
        imagen_colision_rect = IMAGEN_COLISION.get_rect(center=colision_pos)
        pantalla.blit(IMAGEN_COLISION, imagen_colision_rect)


def dibujar_columna_derecha(pantalla, frame_visual_surf, chat_box, input_box, ia_escribiendo):
    
    
    camara_rect = pygame.Rect(POS_X_CAMARA, 0, ANCHO_COLUMNA, ALTO_PANTALLA)
    pygame.draw.rect(pantalla, AZUL_FONDO, camara_rect)
    
    titulo = FUENTE_TITULO.render(f"ASISTENTE {ASSISTANT_NAME}", True, BLANCO)
    pantalla.blit(titulo, (POS_X_CAMARA + ANCHO_COLUMNA // 2 - titulo.get_width() // 2, 30))
    
    estado_ia = "Doc IA Activa" if ia_conectada else "Doc IA Desconectada"
    color_ia = VERDE_BTN if ia_conectada else ROJO_BTN
    texto_ia = FUENTE_SMALL.render(f"Estado: {estado_ia}", True, color_ia)
    pantalla.blit(texto_ia, (POS_X_CAMARA + 20, 70))
    
    x_cam = POS_X_CAMARA + ANCHO_COLUMNA // 2 - frame_visual_surf.get_width() // 2
    y_cam = 90
    
    pygame.draw.rect(pantalla, NEGRO, (x_cam - 5, y_cam - 5, frame_visual_surf.get_width() + 10, frame_visual_surf.get_height() + 10), border_radius=5)
    pantalla.blit(frame_visual_surf, (x_cam, y_cam))
    
    chat_box.dibujar(pantalla, ia_escribiendo)
    
    input_box.dibujar(pantalla)


def get_head_tilt_mediapipe(frame):
    angle = 0
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, c = frame.shape
            p1 = face_landmarks.landmark[33]
            p2 = face_landmarks.landmark[263]
            x1, y1 = int(p1.x * w), int(p1.y * h)
            x2, y2 = int(p2.x * w), int(p2.y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            delta_y = y2 - y1
            delta_x = x2 - x1
            angle = math.atan2(delta_y, delta_x) * 180 / math.pi
            cv2.putText(frame, f"Angulo: {angle:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            return angle, frame
    return angle, frame


def juego_principal():
    global estado_juego, records, nivel_actual, UMBRAL_INCLINACION, datos_analisis, ia_task_queue, ia_escribiendo, records_metrics
    
    chat_rect = pygame.Rect(POS_X_CAMARA + 20, Y_INICIO_CHAT, ANCHO_COLUMNA - 40, ALTO_AREA_CHAT)
    chat_box = ChatBox(chat_rect)
    
    input_y = chat_rect.y + chat_rect.height + 10
    input_box = InputBox(POS_X_CAMARA + 20, input_y, ANCHO_COLUMNA - 40, ALTO_INPUT_CHAT)

    chat_box.añadir_mensaje(ASSISTANT_NAME, f"{ASSISTANT_NAME} listo. Puedes preguntar sobre tus resultados o cualquier otro tema.")
    
    todos_los_sprites = pygame.sprite.Group()
    grupo_enemigos = pygame.sprite.Group()
    carrito = Carrito()
    todos_los_sprites.add(carrito)

    puntuacion = 0
    colision_pos = (0, 0)
    contador_frames_coche = 0
    colision_time = 0 
    
    datos_analisis_final = {
        'Distancia': 0, 
        'T. Reacción': 0.0, 
        'Asimetría': 0.0,
        'Porc_Mov_Izq': 0.0,
        'Porc_Mov_Der': 0.0,
        'Total_Movs': 0,
    }

    while True:
        VELOCIDAD_JUEGO = DIFICULTADES[nivel_actual]['velocidad_juego']
        INTERVALO_COCHE = DIFICULTADES[nivel_actual]['intervalo']

        if ia_task_queue and ia_task_queue.done():
            ia_escribiendo = False 
            try:
                respuesta = ia_task_queue.result()
                chat_box.añadir_mensaje(ASSISTANT_NAME, respuesta)
            except Exception as e:
                chat_box.añadir_mensaje(ASSISTANT_NAME, f"ERROR de conexión de Doc IA.")
            ia_task_queue = None 

        ret, frame_camara = CAP.read()
        if not ret: 
            print("Error: No se puede acceder a la cámara.")
            break 
            
        frame_camara = cv2.flip(frame_camara, 1)
        angulo_inclinacion, frame_visual = get_head_tilt_mediapipe(frame_camara)
        
        frame_visual_surf = cv2.cvtColor(frame_visual, cv2.COLOR_BGR2RGB)
        frame_visual_surf = np.rot90(frame_visual_surf)
        frame_visual_surf = pygame.surfarray.make_surface(frame_visual_surf)
        frame_visual_surf = pygame.transform.scale(frame_visual_surf, (200, ALTO_CAMARA_VIEW))

        botones_nivel = dibujar_panel_control(PANTALLA, puntuacion, datos_analisis_final)
        botones_juego = dibujar_botones_juego(PANTALLA) 
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executor.shutdown(wait=False)
                CAP.release(); cv2.destroyAllWindows(); pygame.quit(); sys.exit()
            
            for btn in botones_nivel + botones_juego:
                if btn.click(evento):
                    if estado_juego == 'JUGANDO': 
                        puntuacion = 0 
                        todos_los_sprites.empty()
                        grupo_enemigos.empty()
                        carrito = Carrito()
                        todos_los_sprites.add(carrito)
                        datos_analisis = {k: 0 for k in datos_analisis}
                        enemigos_con_reaccion = {}
                        break

            texto_enviado = input_box.handle_event(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN and input_box.btn_enviar_rect.collidepoint(evento.pos):
                texto_enviado = input_box.text

            if texto_enviado and texto_enviado.strip():
                chat_box.añadir_mensaje('Usuario', texto_enviado)
                input_box.text = "" 
                
                if not ia_task_queue:
                    ia_escribiendo = True 
                    ia_task_queue = executor.submit(call_gemini_api, texto_enviado, nivel_actual, records_metrics[nivel_actual])
                
            chat_box.manejar_scroll(evento)


        if estado_juego == 'JUGANDO':
            
            datos_analisis['frames_totales_juego'] += 1
            
            direccion_movimiento = 0
            if angulo_inclinacion < -UMBRAL_INCLINACION: 
                carrito.mover(-1)
                datos_analisis['inclinacion_izq_total'] += abs(angulo_inclinacion)
                datos_analisis['movimientos_izq_count'] += 1 
                direccion_movimiento = -1
            elif angulo_inclinacion > UMBRAL_INCLINACION: 
                carrito.mover(1)
                datos_analisis['inclinacion_der_total'] += angulo_inclinacion
                datos_analisis['movimientos_der_count'] += 1 
                direccion_movimiento = 1
            else:
                 datos_analisis['frames_neutros'] += 1
            
            if direccion_movimiento != 0:
                for enemigo in grupo_enemigos:
                    if enemigo not in enemigos_con_reaccion:
                        tiempo_reaccion_ms = pygame.time.get_ticks() - enemigo.frame_aparicion
                        if tiempo_reaccion_ms < 5000: 
                            datos_analisis['tiempo_reaccion_total'] += tiempo_reaccion_ms
                            datos_analisis['contador_enemigos_creados'] += 1
                        enemigos_con_reaccion[enemigo] = True 
                        break

            todos_los_sprites.update() 
            puntuacion += VELOCIDAD_JUEGO / 8 
            
            contador_frames_coche += 1
            if contador_frames_coche >= INTERVALO_COCHE:
                coche_enemigo = CocheEnemigo(VELOCIDAD_JUEGO)
                todos_los_sprites.add(coche_enemigo)
                grupo_enemigos.add(coche_enemigo)
                contador_frames_coche = 0

            colisiones = pygame.sprite.spritecollide(carrito, grupo_enemigos, False)
            if colisiones:
                colision_pos = colisiones[0].rect.center
                colision_time = pygame.time.get_ticks() 
                
                if puntuacion > records[nivel_actual]:
                    records[nivel_actual] = int(puntuacion)
                
                records_metrics[nivel_actual]['Distancia'] = puntuacion
                records_metrics[nivel_actual]['Total_Mov_Izq'] = datos_analisis['movimientos_izq_count']
                records_metrics[nivel_actual]['Total_Mov_Der'] = datos_analisis['movimientos_der_count']
                
                estado_juego = 'MUERTE'
                grupo_enemigos.empty()
                puntuacion = 0 
        datos_analisis_final['Distancia'] = puntuacion
        
        if datos_analisis['contador_enemigos_creados'] > 0:
            datos_analisis_final['T. Reacción'] = datos_analisis['tiempo_reaccion_total'] / datos_analisis['contador_enemigos_creados']
        else:
            datos_analisis_final['T. Reacción'] = 0.0

        if datos_analisis['movimientos_izq_count'] > 0 and datos_analisis['movimientos_der_count'] > 0:
            avg_izq = datos_analisis['inclinacion_izq_total'] / datos_analisis['movimientos_izq_count']
            avg_der = datos_analisis['inclinacion_der_total'] / datos_analisis['movimientos_der_count']
            datos_analisis_final['Asimetría'] = abs(avg_izq - avg_der)
        else:
            datos_analisis_final['Asimetría'] = 0.0

        total_movs = datos_analisis['movimientos_izq_count'] + datos_analisis['movimientos_der_count']
        datos_analisis_final['Total_Movs'] = total_movs
        
        if total_movs > 0:
            datos_analisis_final['Porc_Mov_Izq'] = (datos_analisis['movimientos_izq_count'] / total_movs) * 100
            datos_analisis_final['Porc_Mov_Der'] = (datos_analisis['movimientos_der_count'] / total_movs) * 100
        else:
            datos_analisis_final['Porc_Mov_Izq'] = 0.0
            datos_analisis_final['Porc_Mov_Der'] = 0.0


        PANTALLA.fill(GRIS_PANEL)
        dibujar_escenario(PANTALLA, todos_los_sprites, VELOCIDAD_JUEGO, estado_juego, colision_pos)
        dibujar_panel_control(PANTALLA, puntuacion, datos_analisis_final)
        dibujar_botones_juego(PANTALLA)
        dibujar_columna_derecha(PANTALLA, frame_visual_surf, chat_box, input_box, ia_escribiendo)
        
        if estado_juego == 'MENU':
           
            todos_los_sprites.empty()
            grupo_enemigos.empty()
            carrito = Carrito()
            todos_los_sprites.add(carrito)
            
            texto_inicio = FUENTE_TITULO.render("Selecciona Nivel e Inicia", True, BLANCO)
            PANTALLA.blit(texto_inicio, (POS_X_CARRETERA + ANCHO_CARRETERA // 2 - texto_inicio.get_width() // 2, ALTO_PANTALLA // 2))

        elif estado_juego == 'MUERTE':
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - colision_time > 1500: 
                 colision_pos = (0, 0) 

            superficie_oscura = pygame.Surface((ANCHO_CARRETERA, ALTO_PANTALLA), pygame.SRCALPHA)
            superficie_oscura.fill((0, 0, 0, 180)) 
            PANTALLA.blit(superficie_oscura, (POS_X_CARRETERA, 0))

            texto_muerte = FUENTE_TITULO.render("¡ACCIDENTE! 🛑", True, (255, 50, 50))
            texto_record = FUENTE_NORMAL.render(f"Récord: {int(records[nivel_actual])} km", True, BLANCO)
            texto_reiniciar = FUENTE_NORMAL.render("Presiona INICIAR JUEGO para nuevo intento", True, BLANCO)
            
            centro_x = POS_X_CARRETERA + ANCHO_CARRETERA // 2
            
            PANTALLA.blit(texto_muerte, (centro_x - texto_muerte.get_width() // 2, ALTO_PANTALLA // 3 - 50))
            PANTALLA.blit(texto_record, (centro_x - texto_record.get_width() // 2, ALTO_PANTALLA // 3))
            PANTALLA.blit(texto_reiniciar, (centro_x - texto_reiniciar.get_width() // 2, ALTO_PANTALLA // 3 + 50))

        elif estado_juego == 'PAUSA':
            superficie_oscura = pygame.Surface((ANCHO_CARRETERA, ALTO_PANTALLA), pygame.SRCALPHA)
            superficie_oscura.fill((0, 0, 0, 120)) 
            PANTALLA.blit(superficie_oscura, (POS_X_CARRETERA, 0))
            
            texto_pausa = FUENTE_TITULO.render("JUEGO EN PAUSA", True, (255, 255, 0))
            PANTALLA.blit(texto_pausa, (POS_X_CARRETERA + ANCHO_CARRETERA // 2 - texto_pausa.get_width() // 2, ALTO_PANTALLA // 2))

        
        pygame.display.flip()
        RELOJ.tick(60)

try:
    if __name__ == '__main__':
        juego_principal()
except Exception as e:
    if 'CAP' in locals() and CAP.isOpened():
        CAP.release()
        cv2.destroyAllWindows()
    if 'executor' in locals():
        executor.shutdown(wait=False)
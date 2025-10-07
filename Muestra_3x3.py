import pygame
import random
import sys

# Inicializar pygame
pygame.init()

# Configuración
WIDTH, HEIGHT = 900, 560
GRID_SIZE = 80
MARGIN = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 100, 200)
YELLOW = (200, 200, 0)
GRAY = (240, 240, 240)
LIGHT_BLUE = (100, 150, 255)
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (255, 100, 100)

# Crear ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Instrucciones Matriciales")

# Función para cargar imagen de fondo
def cargar_fondo_imagen():
    try:
        imagen = pygame.image.load("fondo.jpeg").convert()
        imagen = pygame.transform.scale(imagen, (WIDTH, HEIGHT))
        print(" Imagen de fondo cargada correctamente")
        return imagen
    except pygame.error as e:
        print(f" No se pudo cargar la imagen de fondo: {e}")
        print(" Asegúrate de que 'fondo.jpeg' esté en la misma carpeta")
        print(" Usando fondo azul claro por defecto...")
        fondo = pygame.Surface((WIDTH, HEIGHT))
        fondo.fill((230, 240, 255))
        return fondo

# Función para cargar logo
def cargar_logo():
        return None

# Cargar el fondo y logo
fondo = cargar_fondo_imagen()
logo = cargar_logo()

# Posición inicial y objetivo
x, y = 0, 0
target_x, target_y = 2, 2

# --- Utilidades para movimiento y direcciones ---
DIRECCIONES = ["derecha", "izquierda", "arriba", "abajo"]

def pasos_y_direccion_x(start, end):
    delta = (end - start) % 3
    if delta == 0:
        return []
    if delta == 1:
        return ["derecha"]
    if delta == 2:
        return ["izquierda"]
    return []

def pasos_y_direccion_y(start, end):
    delta = (end - start) % 3
    if delta == 0:
        return []
    if delta == 1:
        return ["abajo"]
    if delta == 2:
        return ["arriba"]
    return []

def obtener_direccion(instr):
    """Obtiene la dirección de una instrucción (sea for o simple)"""
    if instr.startswith("for"):
        return instr.split(" : ")[1]
    else:
        return instr

# --- Generador de instrucciones mejorado ---
def generar_instrucciones():
    # Configuración de requisitos
    MIN_INSTRUCCIONES = 10
    MAX_INSTRUCCIONES = 15
    MIN_FOR = 3
    MIN_ITERACIONES_FOR = 2
    MAX_ITERACIONES_FOR = 3
    
    # Generar camino base hacia el objetivo
    base_moves = []
    base_moves.extend(pasos_y_direccion_x(0, target_x))
    base_moves.extend(pasos_y_direccion_y(0, target_y))
    
    # Si el camino base es muy corto, agregar movimientos extra
    while len(base_moves) < MIN_INSTRUCCIONES - 2:
        direccion_extra = random.choice(DIRECCIONES)
        base_moves.append(direccion_extra)
    
    # Expandir movimientos para alcanzar el mínimo
    instrucciones = []
    
    for move in base_moves:
        # Verificar si la dirección es igual a la anterior
        if instrucciones:
            direccion_anterior = obtener_direccion(instrucciones[-1])
            if move == direccion_anterior:
                # Cambiar la dirección para evitar repetición
                direcciones_posibles = [d for d in DIRECCIONES if d != direccion_anterior]
                if direcciones_posibles:
                    move = random.choice(direcciones_posibles)
        
        # Decidir si hacer for o simple
        if (random.random() < 0.4 and 
            sum(1 for instr in instrucciones if instr.startswith("for")) < MIN_FOR):
            iteraciones = random.randint(MIN_ITERACIONES_FOR, MAX_ITERACIONES_FOR)
            instrucciones.append(f"for {iteraciones} veces : {move}")
        else:
            instrucciones.append(move)
    
    # Asegurar al menos MIN_FOR instrucciones for
    while sum(1 for instr in instrucciones if instr.startswith("for")) < MIN_FOR:
        # Encontrar índices que no son for
        indices_no_for = [i for i, instr in enumerate(instrucciones) 
                         if not instr.startswith("for")]
        if indices_no_for:
            idx = random.choice(indices_no_for)
            move = instrucciones[idx]
            direccion_actual = obtener_direccion(move)
            
            # Verificar que no sea igual a la anterior ni a la siguiente
            direccion_anterior = None
            direccion_siguiente = None
            
            if idx > 0:
                direccion_anterior = obtener_direccion(instrucciones[idx-1])
            if idx < len(instrucciones) - 1:
                direccion_siguiente = obtener_direccion(instrucciones[idx+1])
            
            # Si la dirección actual causa repetición, cambiarla
            if direccion_actual == direccion_anterior or direccion_actual == direccion_siguiente:
                direcciones_posibles = [d for d in DIRECCIONES 
                                      if d != direccion_anterior and d != direccion_siguiente]
                if direcciones_posibles:
                    direccion_actual = random.choice(direcciones_posibles)
            
            iteraciones = random.randint(MIN_ITERACIONES_FOR, MAX_ITERACIONES_FOR)
            instrucciones[idx] = f"for {iteraciones} veces : {direccion_actual}"
    
    # Eliminar TODAS las instrucciones consecutivas con misma dirección
    i = 1
    while i < len(instrucciones):
        direccion_actual = obtener_direccion(instrucciones[i])
        direccion_anterior = obtener_direccion(instrucciones[i-1])
        
        if direccion_actual == direccion_anterior:
            # Encontrar una dirección diferente
            direcciones_posibles = [d for d in DIRECCIONES if d != direccion_anterior]
            if direcciones_posibles:
                nueva_direccion = random.choice(direcciones_posibles)
                
                # Decidir si mantener el tipo de instrucción o cambiarlo
                if instrucciones[i].startswith("for"):
                    # Mantener for pero cambiar dirección
                    iteraciones = int(instrucciones[i].split(" ")[1])
                    instrucciones[i] = f"for {iteraciones} veces : {nueva_direccion}"
                else:
                    # Cambiar instrucción simple
                    instrucciones[i] = nueva_direccion
            else:
                # Si no hay direcciones posibles (caso extremo), eliminar esta instrucción
                instrucciones.pop(i)
                continue
        i += 1
    
    # Ajustar longitud final
    while len(instrucciones) < MIN_INSTRUCCIONES:
        # Agregar instrucción que no sea igual a la anterior
        ultima = instrucciones[-1] if instrucciones else None
        direccion_ultima = obtener_direccion(ultima) if ultima else None
        
        direcciones_posibles = [d for d in DIRECCIONES if d != direccion_ultima]
        if not direcciones_posibles:
            direcciones_posibles = DIRECCIONES
        
        nueva_direccion = random.choice(direcciones_posibles)
        
        # Decidir si hacer for o simple
        if (sum(1 for instr in instrucciones if instr.startswith("for")) < MIN_FOR and
            random.random() < 0.5):
            iteraciones = random.randint(MIN_ITERACIONES_FOR, MAX_ITERACIONES_FOR)
            instrucciones.append(f"for {iteraciones} veces : {nueva_direccion}")
        else:
            instrucciones.append(nueva_direccion)
    
    # Recortar si hay demasiadas instrucciones
    if len(instrucciones) > MAX_INSTRUCCIONES:
        instrucciones = instrucciones[:MAX_INSTRUCCIONES]
    
    # Verificar que llegue al objetivo
    sim_x, sim_y = 0, 0
    
    def sim_move(sim_x, sim_y, dirc):
        if dirc == "derecha":
            sim_x = (sim_x + 1) % 3
        elif dirc == "izquierda":
            sim_x = (sim_x - 1) % 3
        elif dirc == "arriba":
            sim_y = (sim_y - 1) % 3
        elif dirc == "abajo":
            sim_y = (sim_y + 1) % 3
        return sim_x, sim_y
    
    # Simular todas las instrucciones
    for s in instrucciones:
        if s.startswith("for"):
            partes = s.split(" : ")
            veces = int(partes[0].split(" ")[1])
            dirc = partes[1]
            for _ in range(veces):
                sim_x, sim_y = sim_move(sim_x, sim_y, dirc)
        else:
            sim_x, sim_y = sim_move(sim_x, sim_y, s)
    
    # Si no llega al objetivo, agregar instrucciones correctivas
    safety_iters = 0
    while (sim_x, sim_y) != (target_x, target_y) and safety_iters < 5:
        safety_iters += 1
        
        if sim_x != target_x:
            if (target_x - sim_x) % 3 == 1:
                d = "derecha"
            else:
                d = "izquierda"
        elif sim_y != target_y:
            if (target_y - sim_y) % 3 == 1:
                d = "abajo"
            else:
                d = "arriba"
        
        # Agregar instrucción que no sea igual a la última
        ultima = instrucciones[-1] if instrucciones else None
        direccion_ultima = obtener_direccion(ultima) if ultima else None
        
        if d == direccion_ultima:
            # Encontrar dirección alternativa que también ayude
            if sim_x != target_x and sim_y != target_y:
                # Intentar con la otra coordenada
                if random.random() < 0.5:
                    if (target_y - sim_y) % 3 == 1:
                        d = "abajo"
                    else:
                        d = "arriba"
                else:
                    if (target_x - sim_x) % 3 == 1:
                        d = "derecha"
                    else:
                        d = "izquierda"
            else:
                # Si solo falta una coordenada, usar dirección diferente temporalmente
                direcciones_posibles = [dir_temp for dir_temp in DIRECCIONES 
                                      if dir_temp != direccion_ultima]
                if direcciones_posibles:
                    d = random.choice(direcciones_posibles)
        
        # Agregar la instrucción
        if (sum(1 for instr in instrucciones if instr.startswith("for")) < MIN_FOR and
            random.random() < 0.3):
            iteraciones = random.randint(MIN_ITERACIONES_FOR, MAX_ITERACIONES_FOR)
            instrucciones.append(f"for {iteraciones} veces : {d}")
            for _ in range(iteraciones):
                sim_x, sim_y = sim_move(sim_x, sim_y, d)
        else:
            instrucciones.append(d)
            sim_x, sim_y = sim_move(sim_x, sim_y, d)
    
    return instrucciones

# Movimiento
def procesar_movimiento(direccion):
    global x, y
    if direccion == "derecha":
        x = (x + 1) % 3
    elif direccion == "izquierda":
        x = (x - 1) % 3
    elif direccion == "arriba":
        y = (y - 1) % 3
    elif direccion == "abajo":
        y = (y + 1) % 3
    return x, y

def tecla_a_direccion(tecla):
    if tecla == pygame.K_RIGHT:
        return "derecha"
    elif tecla == pygame.K_LEFT:
        return "izquierda"
    elif tecla == pygame.K_UP:
        return "arriba"
    elif tecla == pygame.K_DOWN:
        return "abajo"
    return None

def movimiento_es_correcto(direccion_tecla):
    if instruccion_actual >= len(instrucciones):
        return False
    instruccion = instrucciones[instruccion_actual]
    if instruccion.startswith("for"):
        direccion_for = instruccion.split(" : ")[1]
        return direccion_tecla == direccion_for
    else:
        return direccion_tecla == instruccion

def verificar_estado_juego():
    global ganador, perdio
    if x == target_x and y == target_y and instruccion_actual >= len(instrucciones):
        ganador = True
        perdio = False
    elif instruccion_actual >= len(instrucciones) and (x != target_x or y != target_y):
        ganador = False
        perdio = True
    else:
        ganador = False
        perdio = False

# Dibujar matriz con fondo personalizado
def dibujar_matriz():
    # Dibujar la imagen de fondo
    screen.blit(fondo, (0, 0))
    
    # Dibujar logo en esquina superior izquierda
    if logo:
        screen.blit(logo, (10, 10))
    
    # Dibujar un panel semitransparente para el área del juego (mejor legibilidad)
    panel_juego = pygame.Surface((350, 350), pygame.SRCALPHA)
    panel_juego.fill((255, 255, 255, 180))  # Blanco semitransparente
    screen.blit(panel_juego, (MARGIN - 20, MARGIN + 30))
    
    font_titulo = pygame.font.SysFont('Arial', 28, bold=True)
    titulo = font_titulo.render("Juego de Instrucciones", True, BLACK)
    screen.blit(titulo, (300, 15))

    for i in range(3):
        for j in range(3):
            rect = pygame.Rect(MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE + 60, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 2)

    player_x = MARGIN + x * GRID_SIZE + GRID_SIZE // 2
    player_y = MARGIN + y * GRID_SIZE + GRID_SIZE // 2 + 60
    pygame.draw.circle(screen, BLUE, (player_x, player_y), 25)
    pygame.draw.circle(screen, WHITE, (player_x, player_y), 14)

# Mostrar interfaz
def mostrar_interfaz():
    font = pygame.font.SysFont('Arial', 16)
    font_bold = pygame.font.SysFont('Arial', 18, bold=True)
    font_large = pygame.font.SysFont('Arial', 32, bold=True)

    panel_x, panel_y, panel_w, panel_h = 420, 60, 450, 480
    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 2, 10)

    titulo = font_bold.render("INSTRUCCIONES:", True, BLACK)
    screen.blit(titulo, (panel_x + 16, panel_y + 12))

    max_lines = 14
    start_index = max(0, instruccion_actual - 4)
    end_index = min(len(instrucciones), start_index + max_lines)
    y_offset = panel_y + 45
    line_height = 26

    for idx in range(start_index, end_index):
        instr = instrucciones[idx]
        if idx < instruccion_actual:
            color = GREEN
        elif idx == instruccion_actual:
            color = RED
        else:
            color = BLACK

        if instr.startswith("for"):
            partes = instr.split(" : ")
            veces = partes[0].split(' ')[1]
            direccion = partes[1]
            if idx == instruccion_actual and contador_for > 0:
                texto_formateado = f"for {veces} veces: {direccion} ({contador_for}/{veces})"
            else:
                texto_formateado = f"for {veces} veces: {direccion}"
        else:
            texto_formateado = f"mover {instr}"

        texto = font.render(f"{idx+1:2d}. {texto_formateado}", True, color)
        screen.blit(texto, (panel_x + 16, y_offset + (idx - start_index) * line_height))

    estado_y = 420
    
    # Información del juego (solo se muestra si NO hay pantalla de resultado)
    if not ganador and not perdio and not fallo:
        estado = font.render("Usa las FLECHAS para seguir las instrucciones", True, BLUE)
        screen.blit(estado, (panel_x + 16, estado_y))
        
        instruccion_actual_text = font_bold.render(f"Instrucción actual: {instruccion_actual + 1}/{len(instrucciones)}", True, RED)
        screen.blit(instruccion_actual_text, (panel_x + 16, estado_y + 26))

    info_y = 360
    # Solo mostrar información de progreso si NO hay pantalla de resultado
    if not ganador and not perdio and not fallo:
        mov_text = font.render(f"Instrucciones completadas: {instruccion_actual}/{len(instrucciones)}", True, BLACK)
        screen.blit(mov_text, (50, info_y))

# Función para mostrar pantallas de resultado (se llama después de todo)
def mostrar_pantalla_resultado():
    if fallo or ganador or perdio:
        font_bold = pygame.font.SysFont('Arial', 18, bold=True)
        font_large = pygame.font.SysFont('Arial', 32, bold=True)
        font = pygame.font.SysFont('Arial', 16)
        
        # PANTALLAS CENTRALES PARA GANAR/PERDER/FALLAR
        popup_width, popup_height = 400, 250
        popup_x = (WIDTH - popup_width) // 2
        popup_y = (HEIGHT - popup_height) // 2
        
        # MOSTRAR PANTALLA DE FALLASTE SI HAY MOVIMIENTO INCORRECTO
        if fallo:
            # Pantalla de fallo CENTRAL
            pygame.draw.rect(screen, LIGHT_RED, (popup_x, popup_y, popup_width, popup_height), 0, 15)
            pygame.draw.rect(screen, RED, (popup_x, popup_y, popup_width, popup_height), 3, 15)
            
            fallaste_text = font_large.render("FALLASTE", True, RED)
            motivo_text = font_bold.render("Movimiento incorrecto", True, BLACK)
            instruccion_text = font.render("Presiona R para reintentar", True, BLACK)
            
            # Centrar textos horizontalmente
            screen.blit(fallaste_text, (popup_x + (popup_width - fallaste_text.get_width()) // 2, popup_y + 40))
            screen.blit(motivo_text, (popup_x + (popup_width - motivo_text.get_width()) // 2, popup_y + 100))
            screen.blit(instruccion_text, (popup_x + (popup_width - instruccion_text.get_width()) // 2, popup_y + 150))
            
        elif ganador:
            # Pantalla de victoria CENTRAL
            pygame.draw.rect(screen, LIGHT_GREEN, (popup_x, popup_y, popup_width, popup_height), 0, 15)
            pygame.draw.rect(screen, GREEN, (popup_x, popup_y, popup_width, popup_height), 3, 15)
            
            ganaste_text = font_large.render(" ¡GANASTE!", True, GREEN)
            instruccion_text = font.render("Presiona R para reiniciar", True, BLACK)
            
            # Centrar textos horizontalmente
            screen.blit(ganaste_text, (popup_x + (popup_width - ganaste_text.get_width()) // 2, popup_y + 60))
            screen.blit(instruccion_text, (popup_x + (popup_width - instruccion_text.get_width()) // 2, popup_y + 130))
            
        elif perdio:
            # Pantalla de derrota por no llegar al objetivo CENTRAL
            pygame.draw.rect(screen, LIGHT_RED, (popup_x, popup_y, popup_width, popup_height), 0, 15)
            pygame.draw.rect(screen, RED, (popup_x, popup_y, popup_width, popup_height), 3, 15)
            
            perdiste_text = font_large.render("Fallaste", True, RED)
            motivo_text = font.render("Completaste las instrucciones", True, BLACK)
            motivo2_text = font.render("pero no llegaste al objetivo", True, BLACK)
            instruccion_text = font.render("Presiona R para reintentar", True, BLACK)
            
            # Centrar textos horizontalmente
            screen.blit(perdiste_text, (popup_x + (popup_width - perdiste_text.get_width()) // 2, popup_y + 30))
            screen.blit(motivo_text, (popup_x + (popup_width - motivo_text.get_width()) // 2, popup_y + 90))
            screen.blit(motivo2_text, (popup_x + (popup_width - motivo2_text.get_width()) // 2, popup_y + 115))
            screen.blit(instruccion_text, (popup_x + (popup_width - instruccion_text.get_width()) // 2, popup_y + 160))

def reiniciar_juego():
    global x, y, instrucciones, instruccion_actual, ganador, perdio, contador_for, fallo
    x, y = 0, 0
    instrucciones = generar_instrucciones()
    instruccion_actual = 0
    ganador = False
    perdio = False
    fallo = False
    contador_for = 0

# Variables del juego
instrucciones = generar_instrucciones()
instruccion_actual = 0
ganador = False
perdio = False
fallo = False
contador_for = 0

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reiniciar_juego()
            elif not ganador and not perdio and not fallo and instruccion_actual < len(instrucciones):
                direccion = tecla_a_direccion(event.key)
                if direccion:
                    instruccion = instrucciones[instruccion_actual]
                    
                    if instruccion.startswith("for"):
                        if movimiento_es_correcto(direccion):
                            procesar_movimiento(direccion)
                            contador_for += 1
                            veces = int(instruccion.split(" ")[1])
                            if contador_for >= veces:
                                instruccion_actual += 1
                                contador_for = 0
                        else:
                            # MOVIMIENTO INCORRECTO - MOSTRAR PANTALLA DE FALLO
                            fallo = True
                    else:
                        if movimiento_es_correcto(direccion):
                            procesar_movimiento(direccion)
                            instruccion_actual += 1
                        else:
                            # MOVIMIENTO INCORRECTO - MOSTRAR PANTALLA DE FALLO
                            fallo = True
                    
                    verificar_estado_juego()

    verificar_estado_juego()
    
    # ORDEN CORRECTO DE DIBUJADO:
    dibujar_matriz()      # 1. Fondo y elementos del juego
    mostrar_interfaz()    # 2. Interfaz normal
    mostrar_pantalla_resultado()  # 3. Pantallas de resultado (SOBRE TODO)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

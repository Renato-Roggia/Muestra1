import pygame
import random
import sys

# Inicializar pygame
pygame.init()

# Configuración
WIDTH, HEIGHT = 800, 500
GRID_SIZE = 80
MARGIN = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 100, 200)
YELLOW = (200, 200, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (100, 150, 255)
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (255, 100, 100)

# Crear ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Juego de Instrucciones Matriciales")

# Posición inicial y objetivo
x, y = 0, 0
target_x, target_y = 2, 2

# Generar instrucciones aleatorias
def generar_instrucciones():
    instrucciones = []
    movimientos = random.randint(8, 12)
    
    for _ in range(movimientos):
        if random.random() < 0.3:  # 30% de probabilidad de instrucción for
            veces = random.randint(2, 3)
            direccion = random.choice(["derecha", "izquierda", "arriba", "abajo"])
            instrucciones.append(f"for {veces} veces : {direccion}")
        else:
            direccion = random.choice(["derecha", "izquierda", "arriba", "abajo"])
            instrucciones.append(direccion)
    
    return instrucciones

# Función para procesar movimiento con wrap-around
def procesar_movimiento(direccion):
    global x, y
    
    if direccion == "derecha":
        x = (x + 1) % 3
    elif direccion == "izquierda":
        x = (x - 1) % 3
        if x < 0: x = 2
    elif direccion == "arriba":
        y = (y - 1) % 3
        if y < 0: y = 2
    elif direccion == "abajo":
        y = (y + 1) % 3
    
    return x, y

# Convertir tecla a dirección
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

# Verificar si el movimiento es correcto según la instrucción actual
def movimiento_es_correcto(direccion_tecla):
    if instruccion_actual >= len(instrucciones):
        return False
    
    instruccion = instrucciones[instruccion_actual]
    
    if instruccion.startswith("for"):
        # Extraer la dirección del for
        direccion_for = instruccion.split(" : ")[1]
        return direccion_tecla == direccion_for
    else:
        # Instrucción simple
        return direccion_tecla == instruccion

# Verificar estado del juego
def verificar_estado_juego():
    global ganador, perdio
    
    # Verificar si ganó (llegó al objetivo y completó todas las instrucciones)
    if x == target_x and y == target_y and instruccion_actual >= len(instrucciones):
        ganador = True
        perdio = False
    # Verificar si perdió (completó todas las instrucciones pero no llegó al objetivo)
    elif instruccion_actual >= len(instrucciones) and (x != target_x or y != target_y):
        ganador = False
        perdio = True
    else:
        ganador = False
        perdio = False

# Dibujar la matriz
def dibujar_matriz():
    # Fondo
    screen.fill(WHITE)
    
    # Título
    font_titulo = pygame.font.SysFont('Arial', 28, bold=True)
    titulo = font_titulo.render("🎮 Juego de Instrucciones", True, BLUE)
    screen.blit(titulo, (50, 15))
    
    # Dibujar grid 3x3
    for i in range(3):
        for j in range(3):
            rect = pygame.Rect(MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE + 40, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            # Marcar la celda objetivo
            if j == target_x and i == target_y:
                pygame.draw.rect(screen, GREEN, rect.inflate(-10, -10), 3)
    
    # Dibujar jugador
    player_x = MARGIN + x * GRID_SIZE + GRID_SIZE // 2
    player_y = MARGIN + y * GRID_SIZE + GRID_SIZE // 2 + 40
    pygame.draw.circle(screen, BLUE, (player_x, player_y), 25)
    pygame.draw.circle(screen, WHITE, (player_x, player_y), 15)

# Mostrar instrucciones y estado
def mostrar_interfaz():
    font = pygame.font.SysFont('Arial', 18)
    font_bold = pygame.font.SysFont('Arial', 18, bold=True)
    font_large = pygame.font.SysFont('Arial', 32, bold=True)
    
    # Panel de instrucciones
    pygame.draw.rect(screen, GRAY, (400, 50, 350, 400), 0, 10)
    pygame.draw.rect(screen, BLACK, (400, 50, 350, 400), 2, 10)
    
    titulo = font_bold.render("📋 INSTRUCCIONES:", True, BLACK)
    screen.blit(titulo, (420, 70))
    
    # Mostrar instrucciones
    max_instrucciones = 12  # Máximo de instrucciones a mostrar
    start_index = max(0, instruccion_actual - 3)  # Mostrar instrucciones alrededor de la actual
    
    for i in range(start_index, min(len(instrucciones), start_index + max_instrucciones)):
        instr = instrucciones[i]
        
        # Determinar color según el estado
        if i < instruccion_actual:
            color = GREEN  # Completadas
        elif i == instruccion_actual:
            color = RED    # Actual
        else:
            color = BLACK  # Pendientes
        
        # Formatear mejor las instrucciones for
        if instr.startswith("for"):
            partes = instr.split(" : ")
            veces = partes[0].split(' ')[1]
            direccion = partes[1]
            if i == instruccion_actual and contador_for > 0:
                texto_formateado = f"for {veces} veces: {direccion} ({contador_for}/{veces})"
            else:
                texto_formateado = f"for {veces} veces: {direccion}"
        else:
            texto_formateado = f"mover {instr}"
        
        texto = font.render(f"{i+1:2d}. {texto_formateado}", True, color)
        screen.blit(texto, (420, 100 + (i - start_index) * 25))
    
    # Estado del juego - EVITAR SUPERPOSICIÓN
    estado_y = 380  # Posición fija para el estado
    
    if ganador:
        # Pantalla de victoria
        pygame.draw.rect(screen, LIGHT_GREEN, (50, 150, 300, 200), 0, 15)
        pygame.draw.rect(screen, GREEN, (50, 150, 300, 200), 3, 15)
        
        ganaste_text = font_large.render("🎉 ¡GANASTE!", True, GREEN)
        instruccion_text = font.render("Presiona R para reiniciar", True, BLACK)
        
        screen.blit(ganaste_text, (120, 200))
        screen.blit(instruccion_text, (100, 250))
        
    elif perdio:
        # Pantalla de derrota
        pygame.draw.rect(screen, LIGHT_RED, (50, 150, 300, 200), 0, 15)
        pygame.draw.rect(screen, RED, (50, 150, 300, 200), 3, 15)
        
        perdiste_text = font_large.render("❌ PERDISTE", True, RED)
        motivo_text = font.render("Completaste las instrucciones", True, BLACK)
        motivo2_text = font.render("pero no llegaste al objetivo", True, BLACK)
        instruccion_text = font.render("Presiona R para reintentar", True, BLACK)
        
        screen.blit(perdiste_text, (110, 170))
        screen.blit(motivo_text, (80, 220))
        screen.blit(motivo2_text, (80, 245))
        screen.blit(instruccion_text, (80, 280))
        
    else:
        # Juego en progreso
        estado = font.render("Usa las FLECHAS para seguir las instrucciones", True, BLUE)
        screen.blit(estado, (420, estado_y))
        
        # Mostrar instrucción actual destacada
        instruccion_actual_text = font_bold.render(f"Instrucción actual: {instruccion_actual + 1}/{len(instrucciones)}", True, RED)
        screen.blit(instruccion_actual_text, (420, estado_y + 30))
    
    # Información del juego (siempre visible)
    info_y = 300
    pos_text = font.render(f"Posición: ({x}, {y})", True, BLACK)
    screen.blit(pos_text, (50, info_y))
    
    obj_text = font.render(f"Objetivo: ({target_x}, {target_y})", True, GREEN)
    screen.blit(obj_text, (50, info_y + 30))
    
    mov_text = font.render(f"Instrucciones: {instruccion_actual}/{len(instrucciones)}", True, BLACK)
    screen.blit(mov_text, (50, info_y + 60))

# Reiniciar juego
def reiniciar_juego():
    global x, y, instrucciones, instruccion_actual, ganador, perdio, contador_for
    x, y = 0, 0
    instrucciones = generar_instrucciones()
    instruccion_actual = 0
    ganador = False
    perdio = False
    contador_for = 0

# Variables del juego
instrucciones = generar_instrucciones()
instruccion_actual = 0
ganador = False
perdio = False
contador_for = 0  # Para contar movimientos en instrucciones for

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reiniciar_juego()
            
            elif not ganador and not perdio and instruccion_actual < len(instrucciones):
                direccion = tecla_a_direccion(event.key)
                
                if direccion:
                    instruccion = instrucciones[instruccion_actual]
                    
                    if instruccion.startswith("for"):
                        # Instrucción for
                        if movimiento_es_correcto(direccion):
                            procesar_movimiento(direccion)
                            contador_for += 1
                            
                            # Verificar si completó todos los movimientos del for
                            veces = int(instruccion.split(" ")[1])
                            if contador_for >= veces:
                                instruccion_actual += 1
                                contador_for = 0
                        else:
                            # Movimiento incorrecto - reiniciar
                            reiniciar_juego()
                    
                    else:
                        # Instrucción simple
                        if movimiento_es_correcto(direccion):
                            procesar_movimiento(direccion)
                            instruccion_actual += 1
                        else:
                            # Movimiento incorrecto - reiniciar
                            reiniciar_juego()
                    
                    # Verificar estado después de cada movimiento
                    verificar_estado_juego()
    
    # Verificar estado continuamente (por si acaso)
    verificar_estado_juego()
    
    # Dibujar todo
    dibujar_matriz()
    mostrar_interfaz()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

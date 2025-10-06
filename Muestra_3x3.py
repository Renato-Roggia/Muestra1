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
pygame.display.set_caption("🎮 Juego de Instrucciones Matriciales (Corregido)")

# Posición inicial y objetivo
x, y = 0, 0
target_x, target_y = 2, 2

# --- Utilidades para movimiento y direcciones ---
DIRECCIONES = ["derecha", "izquierda", "arriba", "abajo"]

def movimiento_corto_entre(a, b, modulo=3):
    delta = (b - a) % modulo
    if delta == 0:
        return None, 0
    if delta <= modulo // 2:
        return delta
    else:
        return delta - modulo

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

# --- Generador de instrucciones ---
def generar_instrucciones():
    base_moves = []
    base_moves.extend(pasos_y_direccion_x(0, target_x))
    base_moves.extend(pasos_y_direccion_y(0, target_y))

    pasos = []
    for d in base_moves:
        rep = random.choice([1, 2, 3])
        pasos.extend([d] * rep)

    if not pasos:
        pasos = [random.choice(DIRECCIONES) for _ in range(random.randint(2, 4))]

    instrucciones = []
    i = 0
    for_count = 0
    while i < len(pasos):
        j = i
        while j < len(pasos) and pasos[j] == pasos[i]:
            j += 1
        run_length = j - i
        if run_length >= 2 and random.random() < 0.8:
            max_iter = min(4, run_length + random.choice([0, 1]))
            iter_count = random.randint(2, max_iter)
            instr = f"for {iter_count} veces : {pasos[i]}"
            if instrucciones and instrucciones[-1] == instr:
                instrucciones.append(pasos[i])
            else:
                instrucciones.append(instr)
                for_count += 1
            consume = min(iter_count, run_length)
            i += consume
        else:
            if instrucciones and instrucciones[-1] == pasos[i]:
                alt = random.choice([d for d in DIRECCIONES if d != pasos[i]])
                instrucciones.append(alt)
            instrucciones.append(pasos[i])
            i += 1

    attempts = 0
    while for_count < 2 and attempts < 10:
        attempts += 1
        idxs = [idx for idx, s in enumerate(instrucciones) if not s.startswith("for")]
        if not idxs:
            break
        idx = random.choice(idxs)
        direction = instrucciones[idx]
        prev_instr = instrucciones[idx - 1] if idx - 1 >= 0 else None
        next_instr = instrucciones[idx + 1] if idx + 1 < len(instrucciones) else None
        iter_count = random.randint(2, 4)
        candidate = f"for {iter_count} veces : {direction}"
        if candidate != prev_instr and candidate != next_instr:
            instrucciones[idx] = candidate
            for_count += 1

    for k in range(1, len(instrucciones)):
        if instrucciones[k] == instrucciones[k - 1]:
            instr = instrucciones[k]
            if instr.startswith("for"):
                direccion = instr.split(" : ")[1]
                alternativas = [d for d in DIRECCIONES if d != direccion and d != instrucciones[k-1]]
                instrucciones[k] = alternativas[0] if alternativas else direccion
            else:
                alternativas = [d for d in DIRECCIONES if d != instrucciones[k-1]]
                instrucciones[k] = alternativas[0] if alternativas else instrucciones[k]

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

    for s in instrucciones:
        if s.startswith("for"):
            partes = s.split(" : ")
            veces = int(partes[0].split(" ")[1])
            dirc = partes[1]
            for _ in range(veces):
                sim_x, sim_y = sim_move(sim_x, sim_y, dirc)
        else:
            sim_x, sim_y = sim_move(sim_x, sim_y, s)

    safety_iters = 0
    while (sim_x, sim_y) != (target_x, target_y) and safety_iters < 10:
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
        else:
            break

        if instrucciones and instrucciones[-1] == d:
            if not instrucciones[-1].startswith("for"):
                alt = next((a for a in DIRECCIONES if a != d and a != instrucciones[-1]), None)
                if alt:
                    instrucciones.append(alt)
                    sim_x, sim_y = sim_move(sim_x, sim_y, alt)
                    continue
            alternativas = [a for a in DIRECCIONES if a != instrucciones[-1]]
            instrucciones.append(alternativas[0])
            sim_x, sim_y = sim_move(sim_x, sim_y, alternativas[0])
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

# Dibujar matriz sin el cuadrado verde
def dibujar_matriz():
    screen.fill(WHITE)
    font_titulo = pygame.font.SysFont('Arial', 28, bold=True)
    titulo = font_titulo.render("🎮 Juego de Instrucciones", True, BLUE)
    screen.blit(titulo, (50, 15))

    for i in range(3):
        for j in range(3):
            rect = pygame.Rect(MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE + 60, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 2)

    player_x = MARGIN + x * GRID_SIZE + GRID_SIZE // 2
    player_y = MARGIN + y * GRID_SIZE + GRID_SIZE // 2 + 60
    pygame.draw.circle(screen, BLUE, (player_x, player_y), 25)
    pygame.draw.circle(screen, WHITE, (player_x, player_y), 14)

# Mostrar interfaz sin línea de objetivo
def mostrar_interfaz():
    font = pygame.font.SysFont('Arial', 16)
    font_bold = pygame.font.SysFont('Arial', 18, bold=True)
    font_large = pygame.font.SysFont('Arial', 28, bold=True)

    panel_x, panel_y, panel_w, panel_h = 420, 40, 450, 480
    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 2, 10)

    titulo = font_bold.render("📋 INSTRUCCIONES:", True, BLACK)
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
    if ganador:
        pygame.draw.rect(screen, LIGHT_GREEN, (60, 210, 320, 180), 0, 15)
        pygame.draw.rect(screen, GREEN, (60, 210, 320, 180), 3, 15)
        ganaste_text = font_large.render("🎉 ¡GANASTE!", True, GREEN)
        instruccion_text = font.render("Presiona R para reiniciar", True, BLACK)
        screen.blit(ganaste_text, (120, 260))
        screen.blit(instruccion_text, (110, 305))
    elif perdio:
        pygame.draw.rect(screen, LIGHT_RED, (60, 210, 320, 180), 0, 15)
        pygame.draw.rect(screen, RED, (60, 210, 320, 180), 3, 15)
        perdiste_text = font_large.render("❌ PERDISTE", True, RED)
        motivo_text = font.render("Completaste las instrucciones", True, BLACK)
        motivo2_text = font.render("pero no llegaste al objetivo", True, BLACK)
        instruccion_text = font.render("Presiona R para reintentar", True, BLACK)
        screen.blit(perdiste_text, (110, 240))
        screen.blit(motivo_text, (80, 280))
        screen.blit(motivo2_text, (80, 305))
        screen.blit(instruccion_text, (80, 335))
    else:
        estado = font.render("Usa las FLECHAS para seguir las instrucciones", True, BLUE)
        screen.blit(estado, (panel_x + 16, estado_y))
        instruccion_actual_text = font_bold.render(f"Instrucción actual: {instruccion_actual + 1}/{len(instrucciones)}", True, RED)
        screen.blit(instruccion_actual_text, (panel_x + 16, estado_y + 26))

    info_y = 360
    pos_text = font.render(f"Posición: ({x}, {y})", True, BLACK)
    screen.blit(pos_text, (50, info_y))
    mov_text = font.render(f"Instrucciones completadas: {instruccion_actual}/{len(instrucciones)}", True, BLACK)
    screen.blit(mov_text, (50, info_y + 48))

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
            elif not ganador and not perdio and instruccion_actual < len(instrucciones):
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
                            reiniciar_juego()
                    else:
                        if movimiento_es_correcto(direccion):
                            procesar_movimiento(direccion)
                            instruccion_actual += 1
                        else:
                            reiniciar_juego()
                    verificar_estado_juego()

    verificar_estado_juego()
    dibujar_matriz()
    mostrar_interfaz()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

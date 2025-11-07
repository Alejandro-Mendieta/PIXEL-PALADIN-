import pygame
import random
import math
import sys
import os
from enum import Enum

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Paladín: La Maldición Glitch")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
PURPURA = (128, 0, 128)
AMARILLO = (255, 255, 0)
CIAN = (0, 255, 255)
NARANJA = (255, 165, 0)

# Colores de interfaz retro
COLOR_FONDO = (10, 10, 20)
COLOR_INTERFAZ = (20, 20, 40)
COLOR_TEXTO = (0, 255, 0)
COLOR_TEXTO_GLITCH = (255, 0, 255)

# Estados del juego
class EstadoJuego(Enum):
    MENU = 0
    JUGANDO = 1
    PAUSA = 2
    GAME_OVER = 3
    INVENTARIO = 4
    HABILIDADES = 5
    SELECCION_NIVEL = 6
    VICTORIA = 7

# Sistema de niveles
class Nivel:
    def __init__(self, numero, nombre, descripcion, enemigos_requeridos, tiempo_limite=None, dificultad=1):
        self.numero = numero
        self.nombre = nombre
        self.descripcion = descripcion
        self.enemigos_requeridos = enemigos_requeridos
        self.tiempo_limite = tiempo_limite
        self.dificultad = dificultad
        self.desbloqueado = numero == 1  # Solo el primer nivel está desbloqueado inicialmente
        self.estrellas = 0  # 0-3 estrellas
        self.mejor_puntuacion = 0
        self.completado = False
    
    def calcular_estrellas(self, enemigos_eliminados, tiempo_restante, vida_restante):
        estrellas = 0
        
        # Estrella por completar el nivel
        if enemigos_eliminados >= self.enemigos_requeridos:
            estrellas += 1
            
            # Estrella por tiempo (si aplica)
            if self.tiempo_limite and tiempo_restante > self.tiempo_limite * 0.3:
                estrellas += 1
                
            # Estrella por vida
            if vida_restante >= 70:  # Al menos 70% de vida
                estrellas += 1
                
        self.estrellas = max(self.estrellas, estrellas)
        return estrellas

# Configuración de niveles
niveles = [
    Nivel(1, "SISTEMA CORRUPTO", "Elimina 10 enemigos para estabilizar el sistema", 10, 120, 1),
    Nivel(2, "FRAGMENTACIÓN", "Destruye 15 enemigos antes de que el tiempo se agote", 15, 90, 2),
    Nivel(3, "CÓDIGO MALICIOSO", "Derrota 20 enemigos manteniendo alta salud", 20, 120, 3),
    Nivel(4, "VIRUS GLITCH", "Elimina 25 enemigos en tiempo récord", 25, 75, 4),
    Nivel(5, "NÚCLEO CORRUPTO", "Enfrenta la corrupción final - 30 enemigos", 30, 150, 5)
]

# Fuentes retro
try:
    fuente_pequena = pygame.font.SysFont("courier", 12)
    fuente_media = pygame.font.SysFont("courier", 16)
    fuente_grande = pygame.font.SysFont("courier", 24)
    fuente_titulo = pygame.font.SysFont("courier", 36, bold=True)
    fuente_enorme = pygame.font.SysFont("courier", 48, bold=True)
except:
    # Fuentes de respaldo
    fuente_pequena = pygame.font.Font(None, 12)
    fuente_media = pygame.font.Font(None, 16)
    fuente_grande = pygame.font.Font(None, 24)
    fuente_titulo = pygame.font.Font(None, 36)
    fuente_enorme = pygame.font.Font(None, 48)

# Sistema de partículas
particulas = []

class Particula:
    def __init__(self, x, y, tipo="brillo", color=None):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.life = random.uniform(60, 120)
        self.size = random.randint(2, 6)
        
        # Configurar propiedades según el tipo de efecto
        if tipo == "brillo":
            self.color = color or (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200))
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self.gravity = 0.05
        elif tipo == "humo":
            self.color = (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-2, -1)
            self.gravity = -0.02
            self.size = random.randint(3, 8)
        elif tipo == "chispas":
            self.color = color or (random.randint(200, 255), random.randint(100, 200), random.randint(0, 100))
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-5, -2)
            self.gravity = 0.3
        elif tipo == "estrellas":
            self.color = color or (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200))
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            self.gravity = 0.1
            self.rotation = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-5, 5)
        else:  # confeti por defecto
            self.color = color or random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-8, -2)
            self.gravity = 0.2
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        
        if self.tipo == "estrellas":
            self.rotation += self.rotation_speed
            
        self.life -= 1
        return self.life > 0
        
    def draw(self, pantalla):
        if self.tipo == "estrellas":
            # Dibujar estrella giratoria
            points = []
            for i in range(5):
                angle = self.rotation + i * 72
                rad = math.radians(angle)
                x = self.x + math.cos(rad) * self.size
                y = self.y + math.sin(rad) * self.size
                points.append((x, y))
                
                inner_angle = angle + 36
                inner_rad = math.radians(inner_angle)
                inner_x = self.x + math.cos(inner_rad) * (self.size / 2)
                inner_y = self.y + math.sin(inner_rad) * (self.size / 2)
                points.append((inner_x, inner_y))
                
            pygame.draw.polygon(pantalla, self.color, points)
            
        elif self.tipo in ["brillo", "humo"]:
            # Efecto de desvanecimiento para brillos y humo
            alpha = min(255, int(self.life * 2))
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            if self.tipo == "brillo":
                pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
            else:  # humo
                pygame.draw.circle(surf, (*self.color, alpha // 2), (self.size, self.size), self.size)
            pantalla.blit(surf, (self.x - self.size, self.y - self.size))
            
        elif self.tipo == "chispas":
            # Chispas con cola
            tail_length = 5
            for i in range(tail_length):
                alpha = 255 - (i * 50)
                if alpha > 0:
                    pos_x = self.x - (self.vx * i * 0.5)
                    pos_y = self.y - (self.vy * i * 0.5)
                    size = max(1, self.size - i)
                    pygame.draw.circle(pantalla, (*self.color, alpha), (int(pos_x), int(pos_y)), size)
        else:
            # Confeti normal
            pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.size, self.size))

def crear_particulas(x, y, cantidad=50, tipo="confeti", color=None):
    for _ in range(cantidad):
        particulas.append(Particula(x, y, tipo, color))

# Clase para efectos de glitch
class GlitchEffect:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.type = None
        
    def trigger(self, effect_type):
        self.active = True
        self.timer = 10  # Duración del efecto en frames
        self.type = effect_type
        
    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
                
    def apply(self, surface):
        if self.active:
            if self.type == "screen_shake":
                # En una implementación completa, esto movería toda la pantalla
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                surface_copy = surface.copy()
                surface.fill(NEGRO)
                surface.blit(surface_copy, (offset_x, offset_y))
            elif self.type == "color_shift":
                # Cambiar paleta de colores
                shift_surface = surface.copy()
                r = random.randint(0, 50)
                g = random.randint(0, 50)
                b = random.randint(0, 50)
                shift_surface.fill((r, g, b), special_flags=pygame.BLEND_RGB_ADD)
                surface.blit(shift_surface, (0, 0))
            elif self.type == "scan_lines":
                # Dibujar líneas de escaneo
                for y in range(0, HEIGHT, 4):
                    pygame.draw.line(surface, NEGRO, (0, y), (WIDTH, y), 1)
            elif self.type == "pixel_glitch":
                # Efecto de píxeles corruptos
                for _ in range(100):
                    x = random.randint(0, WIDTH - 1)
                    y = random.randint(0, HEIGHT - 1)
                    size = random.randint(1, 3)
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    pygame.draw.rect(surface, color, (x, y, size, size))

# Función para crear sprites pixelados
def crear_sprite_pixelado(ancho, alto, colores, patron):
    sprite = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y, fila in enumerate(patron):
        for x, pixel in enumerate(fila):
            if pixel != 0:
                pygame.draw.rect(sprite, colores[pixel-1], (x*4, y*4, 4, 4))
    return sprite

# Clase del jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Patrón de píxeles para el jugador (caballero)
        patron_jugador = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 2, 2, 2, 2, 2, 2, 0],
            [0, 2, 3, 2, 2, 3, 2, 0],
            [0, 2, 2, 2, 2, 2, 2, 0],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 2, 2, 2, 2, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 4, 4, 1, 0, 0],
            [0, 0, 1, 4, 4, 1, 0, 0],
            [0, 0, 1, 4, 4, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0]
        ]
        
        colores_jugador = [
            (0, 0, 150),   # Azul oscuro (armadura)
            (0, 100, 200), # Azul medio (detalles)
            (50, 50, 50),  # Gris (visor)
            (220, 220, 0)  # Amarillo (accesorios)
        ]
        
        self.image = crear_sprite_pixelado(32, 48, colores_jugador, patron_jugador)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.gold = 0
        self.code_fragments = 0
        self.inventory = []
        self.skills = ["Reiniciar Entidad", "Desfragmentar Área", "Revertir Estado"]
        self.selected_skill = 0
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.attack_power = 10
        self.defense = 5
        
    def update(self, keys, platforms):
        # Movimiento
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            
        # Limitar al área de juego
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))
        
        # Colisión con plataformas
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Resolver colisión (simple)
                if self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                elif self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                elif self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
    
    def use_skill(self, enemies, projectiles):
        if self.mana >= 10:
            skill = self.skills[self.selected_skill]
            if skill == "Reiniciar Entidad" and enemies:
                enemy = random.choice(enemies)
                enemy.stun()
                self.mana -= 10
                crear_particulas(enemy.rect.centerx, enemy.rect.centery, 20, "brillo", CIAN)
            elif skill == "Desfragmentar Área":
                projectiles.empty()
                self.mana -= 10
                crear_particulas(self.rect.centerx, self.rect.centery, 30, "estrellas", AMARILLO)
            elif skill == "Revertir Estado":
                self.health = min(self.max_health, self.health + 10)
                self.mana -= 10
                crear_particulas(self.rect.centerx, self.rect.centery, 20, "brillo", VERDE)
            return True
        return False
                
    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense // 2)
        self.health -= actual_damage
        crear_particulas(self.rect.centerx, self.rect.centery, 10, "chispas", ROJO)
        if self.health <= 0:
            self.health = 0
            return True  # Jugador muerto
        return False
    
    def add_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Mejoras al subir de nivel
        self.max_health += 10
        self.health = self.max_health
        self.max_mana += 5
        self.mana = self.max_mana
        self.attack_power += 2
        self.defense += 1
        
        crear_particulas(self.rect.centerx, self.rect.centery, 50, "estrellas", AMARILLO)

# Clase de enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, nivel_dificultad=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, 36, 36)
        
        # Configurar propiedades según el tipo de enemigo
        if enemy_type == "slime":
            self.create_slime()
            self.health = 20 + nivel_dificultad * 5
            self.attack_power = 5 + nivel_dificultad
            self.exp_value = 10 + nivel_dificultad * 2
        elif enemy_type == "skeleton":
            self.create_skeleton()
            self.health = 15 + nivel_dificultad * 4
            self.attack_power = 8 + nivel_dificultad
            self.exp_value = 15 + nivel_dificultad * 3
        elif enemy_type == "bat":
            self.create_bat()
            self.health = 10 + nivel_dificultad * 3
            self.attack_power = 3 + nivel_dificultad
            self.exp_value = 8 + nivel_dificultad * 2
    
    def create_slime(self):
        # Patrón de píxeles para slime
        patron_slime = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 2, 1, 1, 2, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]
        
        colores_slime = [
            (0, 150, 0),   # Verde oscuro
            (50, 200, 50)  # Verde claro
        ]
        
        self.image = crear_sprite_pixelado(32, 36, colores_slime, patron_slime)
    
    def create_skeleton(self):
        # Patrón de píxeles para esqueleto
        patron_skeleton = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 2, 2, 2, 2, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 2, 1, 1, 2, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
        
        colores_skeleton = [
            (200, 200, 200),  # Blanco hueso
            (50, 50, 50)      # Negro (ojos)
        ]
        
        self.image = crear_sprite_pixelado(32, 40, colores_skeleton, patron_skeleton)
    
    def create_bat(self):
        # Patrón de píxeles para murciélago
        patron_bat = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 2, 1, 1, 2, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
        
        colores_bat = [
            (80, 0, 80),    # Púrpura oscuro
            (255, 0, 0)     # Rojo (ojos)
        ]
        
        self.image = crear_sprite_pixelado(32, 32, colores_bat, patron_bat)
    
    def update(self, player):
        # Movimiento simple hacia el jugador
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Normalizar y mover
        self.rect.x += (dx / dist) * 2
        self.rect.y += (dy / dist) * 2
    
    def take_damage(self, amount):
        self.health -= amount
        crear_particulas(self.rect.centerx, self.rect.centery, 5, "chispas", ROJO)
        return self.health <= 0
    
    def stun(self):
        # Efecto de aturdimiento
        crear_particulas(self.rect.centerx, self.rect.centery, 10, "brillo", CIAN)

# Clase de proyectiles
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_player=False, power=10):
        super().__init__()
        self.rect = pygame.Rect(x, y, 12, 12)
        self.speed = 7
        self.direction = direction
        self.is_player = is_player
        self.power = power
        
        if is_player:
            # Proyectil del jugador - bola de energía
            patron_proyectil_jugador = [
                [0, 0, 1, 1, 0, 0],
                [0, 1, 2, 2, 1, 0],
                [1, 2, 3, 3, 2, 1],
                [1, 2, 3, 3, 2, 1],
                [0, 1, 2, 2, 1, 0],
                [0, 0, 1, 1, 0, 0]
            ]
            
            colores_proyectil_jugador = [
                (0, 0, 200),   # Azul oscuro
                (0, 100, 255), # Azul medio
                (100, 200, 255) # Azul claro
            ]
            
            self.image = crear_sprite_pixelado(24, 24, colores_proyectil_jugador, patron_proyectil_jugador)
        else:
            # Proyectil enemigo - orbe de energía oscura
            patron_proyectil_enemigo = [
                [0, 0, 1, 1, 0, 0],
                [0, 1, 2, 2, 1, 0],
                [1, 2, 3, 3, 2, 1],
                [1, 2, 3, 3, 2, 1],
                [0, 1, 2, 2, 1, 0],
                [0, 0, 1, 1, 0, 0]
            ]
            
            colores_proyectil_enemigo = [
                (100, 0, 0),   # Rojo oscuro
                (200, 0, 0),   # Rojo
                (255, 100, 0)  # Naranja
            ]
            
            self.image = crear_sprite_pixelado(24, 24, colores_proyectil_enemigo, patron_proyectil_enemigo)
    
    def update(self):
        self.rect.x += self.direction * self.speed
        
        # Eliminar si sale de la pantalla
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Clase de plataformas
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, glitchy=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        
        # Crear textura de plataforma pixelada
        for i in range(0, width, 4):
            for j in range(0, height, 4):
                color_variation = random.randint(-10, 10)
                base_color = (80, 80, 80) if not glitchy else (100, 80, 100)
                color = (
                    max(0, min(255, base_color[0] + color_variation)),
                    max(0, min(255, base_color[1] + color_variation)),
                    max(0, min(255, base_color[2] + color_variation))
                )
                pygame.draw.rect(self.image, color, (i, j, 4, 4))
        
        # Borde de la plataforma
        pygame.draw.rect(self.image, (120, 120, 120), (0, 0, width, height), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.glitchy = glitchy
        self.visible = True
        self.glitch_timer = 0
        
    def update(self):
        if self.glitchy:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.visible = not self.visible
                self.glitch_timer = random.randint(30, 120)  # Cambio cada 0.5-2 segundos

# Clase para efectos de texto flotante
class TextoFlotante:
    def __init__(self, texto, x, y, color=BLANCO, duracion=1500):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.tiempo_inicio = pygame.time.get_ticks()
        self.duracion = duracion
    
    def actualizar(self):
        return pygame.time.get_ticks() - self.tiempo_inicio < self.duracion
    
    def dibujar(self, pantalla, fuente):
        tiempo = pygame.time.get_ticks() - self.tiempo_inicio
        progreso = tiempo / self.duracion
        
        alpha = int(255 * (1 - progreso))
        y_offset = -50 * progreso
        
        texto_surf = fuente.render(self.texto, True, self.color)
        texto_surf.set_alpha(alpha)
        
        pantalla.blit(texto_surf, (self.x - texto_surf.get_width() // 2, 
                                 self.y + y_offset - texto_surf.get_height() // 2))

# Clase para efectos especiales
class EfectosEspeciales:
    def __init__(self):
        self.animaciones = []
    
    def agregar_explosion(self, x, y, tipo="normal", color=None):
        if tipo == "normal":
            crear_particulas(x, y, 20, "chispas", color or ROJO)
        elif tipo == "magica":
            crear_particulas(x, y, 30, "estrellas", color or AZUL)
        elif tipo == "curacion":
            crear_particulas(x, y, 25, "brillo", color or VERDE)
    
    def agregar_texto_flotante(self, texto, x, y, color=BLANCO):
        self.animaciones.append(TextoFlotante(texto, x, y, color))
    
    def actualizar(self):
        self.animaciones = [anim for anim in self.animaciones if anim.actualizar()]
    
    def dibujar(self, pantalla, fuente):
        for anim in self.animaciones:
            anim.dibujar(pantalla, fuente)

# Función para generar nivel procedural
def generate_level(nivel_actual):
    platforms = pygame.sprite.Group()
    
    # Plataformas básicas
    platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))  # Suelo
    
    # Diferentes configuraciones según el nivel
    if nivel_actual == 1:
        platforms.add(Platform(100, 400, 200, 20))
        platforms.add(Platform(400, 300, 150, 20))
        platforms.add(Platform(200, 200, 100, 20))
    elif nivel_actual == 2:
        platforms.add(Platform(100, 400, 200, 20))
        platforms.add(Platform(400, 300, 150, 20))
        platforms.add(Platform(200, 200, 100, 20))
        platforms.add(Platform(500, 450, 100, 20, True))
    elif nivel_actual == 3:
        platforms.add(Platform(100, 400, 200, 20))
        platforms.add(Platform(400, 300, 150, 20))
        platforms.add(Platform(200, 200, 100, 20))
        platforms.add(Platform(500, 450, 100, 20, True))
        platforms.add(Platform(300, 150, 80, 20, True))
    elif nivel_actual >= 4:
        platforms.add(Platform(100, 400, 200, 20))
        platforms.add(Platform(400, 300, 150, 20))
        platforms.add(Platform(200, 200, 100, 20))
        platforms.add(Platform(500, 450, 100, 20, True))
        platforms.add(Platform(300, 150, 80, 20, True))
        platforms.add(Platform(600, 350, 120, 20, True))
    
    return platforms

# Función para dibujar HUD con efectos de glitch
def draw_hud(screen, player, glitch_effect, estado_juego, nivel_actual, enemigos_eliminados, tiempo_restante):
    # Fondo del HUD
    hud_bg = pygame.Surface((WIDTH, 80))
    hud_bg.fill(COLOR_INTERFAZ)
    screen.blit(hud_bg, (0, 0))
    
    # Efectos de glitch en el HUD
    if random.random() < 0.05 and estado_juego == EstadoJuego.JUGANDO:  # 5% de probabilidad de glitch por frame
        glitch_offset = random.randint(-2, 2)
        glitch_color = COLOR_TEXTO_GLITCH
    else:
        glitch_offset = 0
        glitch_color = COLOR_TEXTO
        
    # Información del nivel
    if nivel_actual:
        nivel_text = fuente_media.render(f"NIVEL: {nivel_actual.numero} - {nivel_actual.nombre}", True, glitch_color)
        screen.blit(nivel_text, (10 + glitch_offset, 10))
        
        # Progreso del nivel
        progreso_text = fuente_media.render(f"ENEMIGOS: {enemigos_eliminados}/{nivel_actual.enemigos_requeridos}", True, glitch_color)
        screen.blit(progreso_text, (10 + glitch_offset, 30))
        
        # Tiempo restante (si aplica)
        if nivel_actual.tiempo_limite:
            tiempo_text = fuente_media.render(f"TIEMPO: {tiempo_restante}s", True, glitch_color)
            screen.blit(tiempo_text, (10 + glitch_offset, 50))
    
    # Salud
    health_text = fuente_media.render(f"SALUD: {player.health}/{player.max_health}", True, glitch_color)
    screen.blit(health_text, (WIDTH - 200 + glitch_offset, 10))
    
    # Barra de salud
    health_width = 150
    health_ratio = player.health / player.max_health
    pygame.draw.rect(screen, ROJO, (WIDTH - 200, 25, health_width, 10))
    pygame.draw.rect(screen, VERDE, (WIDTH - 200, 25, health_width * health_ratio, 10))
    
    # Maná
    mana_text = fuente_media.render(f"MANÁ: {player.mana}/{player.max_mana}", True, glitch_color)
    screen.blit(mana_text, (WIDTH - 200 + glitch_offset, 40))
    
    # Barra de maná
    mana_width = 150
    mana_ratio = player.mana / player.max_mana
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 200, 55, mana_width, 10))
    pygame.draw.rect(screen, AZUL, (WIDTH - 200, 55, mana_width * mana_ratio, 10))
    
    # Habilidad seleccionada
    skill_text = fuente_media.render(f"HABILIDAD: {player.skills[player.selected_skill]}", True, glitch_color)
    screen.blit(skill_text, (WIDTH // 2 - skill_text.get_width() // 2 + glitch_offset, 10))
    
    # Instrucciones
    if estado_juego == EstadoJuego.JUGANDO:
        instructions = fuente_pequena.render("Flechas/WASD: Movimiento | Espacio: Atacar | 1-3: Cambiar habilidad | Q: Usar habilidad | I: Inventario | ESC: Pausa", True, glitch_color)
        screen.blit(instructions, (10, HEIGHT - 20))

# Función para dibujar el menú principal
def draw_main_menu(screen, glitch_effect):
    screen.fill(COLOR_FONDO)
    
    # Título con efecto de glitch
    titulo = fuente_titulo.render("PIXEL PALADÍN", True, COLOR_TEXTO)
    subtitulo = fuente_grande.render("La Maldición Glitch", True, COLOR_TEXTO_GLITCH)
    
    # Aplicar efecto de glitch al título
    if random.random() < 0.1:
        titulo_offset = random.randint(-2, 2)
    else:
        titulo_offset = 0
        
    screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2 + titulo_offset, 150))
    screen.blit(subtitulo, (WIDTH//2 - subtitulo.get_width()//2 + titulo_offset, 200))
    
    # Botones del menú
    boton_jugar = pygame.Rect(WIDTH//2 - 100, 300, 200, 50)
    boton_niveles = pygame.Rect(WIDTH//2 - 100, 370, 200, 50)
    boton_salir = pygame.Rect(WIDTH//2 - 100, 440, 200, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Dibujar botón jugar
    color_jugar = VERDE if boton_jugar.collidepoint(mouse_pos) else (0, 200, 0)
    pygame.draw.rect(screen, color_jugar, boton_jugar, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_jugar, 2, border_radius=5)
    
    texto_jugar = fuente_media.render("JUGAR", True, BLANCO)
    screen.blit(texto_jugar, (boton_jugar.centerx - texto_jugar.get_width()//2, 
                             boton_jugar.centery - texto_jugar.get_height()//2))
    
    # Dibujar botón niveles
    color_niveles = AZUL if boton_niveles.collidepoint(mouse_pos) else (0, 0, 200)
    pygame.draw.rect(screen, color_niveles, boton_niveles, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_niveles, 2, border_radius=5)
    
    texto_niveles = fuente_media.render("SELECCIONAR NIVEL", True, BLANCO)
    screen.blit(texto_niveles, (boton_niveles.centerx - texto_niveles.get_width()//2, 
                               boton_niveles.centery - texto_niveles.get_height()//2))
    
    # Dibujar botón salir
    color_salir = ROJO if boton_salir.collidepoint(mouse_pos) else (200, 0, 0)
    pygame.draw.rect(screen, color_salir, boton_salir, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_salir, 2, border_radius=5)
    
    texto_salir = fuente_media.render("SALIR", True, BLANCO)
    screen.blit(texto_salir, (boton_salir.centerx - texto_salir.get_width()//2, 
                             boton_salir.centery - texto_salir.get_height()//2))
    
    # Instrucciones
    instrucciones = fuente_pequena.render("Usa el mouse para seleccionar una opción", True, COLOR_TEXTO)
    screen.blit(instrucciones, (WIDTH//2 - instrucciones.get_width()//2, 520))
    
    # Efectos de partículas ocasionales
    if random.random() < 0.02:
        crear_particulas(random.randint(0, WIDTH), random.randint(0, HEIGHT//2), 5, "estrellas")
    
    return boton_jugar, boton_niveles, boton_salir

# Función para dibujar la selección de niveles
def draw_level_selection(screen, niveles):
    screen.fill(COLOR_FONDO)
    
    # Título
    titulo = fuente_titulo.render("SELECCIONAR NIVEL", True, COLOR_TEXTO)
    screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))
    
    # Dibujar niveles
    nivel_buttons = []
    for i, nivel in enumerate(niveles):
        fila = i // 3
        columna = i % 3
        
        x = WIDTH//4 + columna * 300
        y = 150 + fila * 200
        
        # Crear botón de nivel
        nivel_rect = pygame.Rect(x - 100, y - 50, 200, 150)
        nivel_buttons.append((nivel_rect, nivel))
        
        # Dibujar el botón según si está desbloqueado o no
        if nivel.desbloqueado:
            color_fondo = (50, 50, 100)  # Azul oscuro
            color_borde = AZUL
        else:
            color_fondo = (50, 50, 50)   # Gris oscuro
            color_borde = (100, 100, 100)  # Gris
        
        pygame.draw.rect(screen, color_fondo, nivel_rect, border_radius=10)
        pygame.draw.rect(screen, color_borde, nivel_rect, 3, border_radius=10)
        
        # Número de nivel
        num_text = fuente_titulo.render(str(nivel.numero), True, BLANCO)
        screen.blit(num_text, (x - num_text.get_width()//2, y - 30))
        
        # Nombre del nivel
        nombre_text = fuente_media.render(nivel.nombre, True, BLANCO)
        screen.blit(nombre_text, (x - nombre_text.get_width()//2, y))
        
        # Estrellas
        if nivel.desbloqueado:
            for j in range(3):
                star_x = x - 30 + j * 30
                if j < nivel.estrellas:
                    pygame.draw.polygon(screen, AMARILLO, [
                        (star_x, y + 30), 
                        (star_x + 10, y + 40),
                        (star_x, y + 50),
                        (star_x - 10, y + 40)
                    ])
                else:
                    pygame.draw.polygon(screen, (100, 100, 100), [
                        (star_x, y + 30), 
                        (star_x + 10, y + 40),
                        (star_x, y + 50),
                        (star_x - 10, y + 40)
                    ])
        
        # Cadena si no está desbloqueado
        if not nivel.desbloqueado:
            # Dibujar cadena
            pygame.draw.circle(screen, (150, 150, 150), (x, y + 60), 15, 2)
            pygame.draw.circle(screen, (150, 150, 150), (x - 20, y + 60), 10, 2)
            pygame.draw.circle(screen, (150, 150, 150), (x + 20, y + 60), 10, 2)
            
            # Texto de bloqueado
            bloqueado_text = fuente_pequena.render("BLOQUEADO", True, ROJO)
            screen.blit(bloqueado_text, (x - bloqueado_text.get_width()//2, y + 80))
    
    # Botón de regreso
    boton_regreso = pygame.Rect(50, HEIGHT - 80, 150, 50)
    mouse_pos = pygame.mouse.get_pos()
    
    color_regreso = (100, 100, 100) if boton_regreso.collidepoint(mouse_pos) else (70, 70, 70)
    pygame.draw.rect(screen, color_regreso, boton_regreso, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_regreso, 2, border_radius=5)
    
    texto_regreso = fuente_media.render("REGRESAR", True, BLANCO)
    screen.blit(texto_regreso, (boton_regreso.centerx - texto_regreso.get_width()//2, 
                               boton_regreso.centery - texto_regreso.get_height()//2))
    
    return nivel_buttons, boton_regreso

# Función para dibujar pantalla de victoria
def draw_victory_screen(screen, nivel, estrellas_obtenidas, enemigos_eliminados, tiempo_restante):
    # Fondo semitransparente
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    
    # Panel de victoria
    panel_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
    pygame.draw.rect(screen, COLOR_INTERFAZ, panel_rect, border_radius=10)
    pygame.draw.rect(screen, VERDE, panel_rect, 3, border_radius=10)
    
    # Título
    texto_victoria = fuente_titulo.render("¡NIVEL COMPLETADO!", True, VERDE)
    screen.blit(texto_victoria, (WIDTH//2 - texto_victoria.get_width()//2, HEIGHT//2 - 180))
    
    # Información del nivel
    nivel_text = fuente_grande.render(f"Nivel {nivel.numero}: {nivel.nombre}", True, BLANCO)
    screen.blit(nivel_text, (WIDTH//2 - nivel_text.get_width()//2, HEIGHT//2 - 120))
    
    # Estrellas obtenidas
    estrellas_text = fuente_grande.render("Estrellas obtenidas:", True, AMARILLO)
    screen.blit(estrellas_text, (WIDTH//2 - estrellas_text.get_width()//2, HEIGHT//2 - 70))
    
    # Dibujar estrellas
    for i in range(3):
        star_x = WIDTH//2 - 60 + i * 60
        if i < estrellas_obtenidas:
            pygame.draw.polygon(screen, AMARILLO, [
                (star_x, HEIGHT//2 - 20), 
                (star_x + 20, HEIGHT//2),
                (star_x, HEIGHT//2 + 20),
                (star_x - 20, HEIGHT//2)
            ])
        else:
            pygame.draw.polygon(screen, (100, 100, 100), [
                (star_x, HEIGHT//2 - 20), 
                (star_x + 20, HEIGHT//2),
                (star_x, HEIGHT//2 + 20),
                (star_x - 20, HEIGHT//2)
            ])
    
    # Estadísticas
    stats = [
        f"Enemigos eliminados: {enemigos_eliminados}/{nivel.enemigos_requeridos}",
        f"Tiempo restante: {tiempo_restante}s" if nivel.tiempo_limite else "",
        f"Mejor puntuación: {nivel.mejor_puntuacion}"
    ]
    
    y_offset = HEIGHT//2 + 30
    for stat in stats:
        if stat:  # Solo mostrar si no está vacío
            texto = fuente_media.render(stat, True, BLANCO)
            screen.blit(texto, (WIDTH//2 - texto.get_width()//2, y_offset))
            y_offset += 30
    
    # Botones
    boton_siguiente = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 150, 200, 50)
    boton_repetir = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 150, 200, 50)
    boton_menu = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 200, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Botón siguiente nivel (solo si no es el último nivel)
    if nivel.numero < len(niveles):
        color_siguiente = VERDE if boton_siguiente.collidepoint(mouse_pos) else (0, 200, 0)
        pygame.draw.rect(screen, color_siguiente, boton_siguiente, border_radius=5)
        pygame.draw.rect(screen, BLANCO, boton_siguiente, 2, border_radius=5)
        
        texto_siguiente = fuente_media.render("SIGUIENTE NIVEL", True, BLANCO)
        screen.blit(texto_siguiente, (boton_siguiente.centerx - texto_siguiente.get_width()//2, 
                                     boton_siguiente.centery - texto_siguiente.get_height()//2))
    
    # Botón repetir
    color_repetir = AZUL if boton_repetir.collidepoint(mouse_pos) else (0, 0, 200)
    pygame.draw.rect(screen, color_repetir, boton_repetir, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_repetir, 2, border_radius=5)
    
    texto_repetir = fuente_media.render("REPETIR NIVEL", True, BLANCO)
    screen.blit(texto_repetir, (boton_repetir.centerx - texto_repetir.get_width()//2, 
                               boton_repetir.centery - texto_repetir.get_height()//2))
    
    # Botón menú principal
    color_menu = (150, 150, 150) if boton_menu.collidepoint(mouse_pos) else (100, 100, 100)
    pygame.draw.rect(screen, color_menu, boton_menu, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_menu, 2, border_radius=5)
    
    texto_menu = fuente_media.render("MENÚ PRINCIPAL", True, BLANCO)
    screen.blit(texto_menu, (boton_menu.centerx - texto_menu.get_width()//2, 
                            boton_menu.centery - texto_menu.get_height()//2))
    
    return boton_siguiente, boton_repetir, boton_menu

# Función para dibujar menú de pausa
def draw_pause_menu(screen):
    # Fondo semitransparente
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    
    # Panel de pausa
    panel_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 200)
    pygame.draw.rect(screen, COLOR_INTERFAZ, panel_rect, border_radius=10)
    pygame.draw.rect(screen, BLANCO, panel_rect, 2, border_radius=10)
    
    # Título
    texto_pausa = fuente_titulo.render("PAUSA", True, COLOR_TEXTO)
    screen.blit(texto_pausa, (WIDTH//2 - texto_pausa.get_width()//2, HEIGHT//2 - 80))
    
    # Opciones
    boton_continuar = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40)
    boton_menu = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 40)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Botón continuar
    color_continuar = VERDE if boton_continuar.collidepoint(mouse_pos) else (0, 200, 0)
    pygame.draw.rect(screen, color_continuar, boton_continuar, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_continuar, 2, border_radius=5)
    
    texto_continuar = fuente_media.render("CONTINUAR", True, BLANCO)
    screen.blit(texto_continuar, (boton_continuar.centerx - texto_continuar.get_width()//2, 
                                 boton_continuar.centery - texto_continuar.get_height()//2))
    
    # Botón menú principal
    color_menu = AZUL if boton_menu.collidepoint(mouse_pos) else (0, 0, 200)
    pygame.draw.rect(screen, color_menu, boton_menu, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_menu, 2, border_radius=5)
    
    texto_menu = fuente_media.render("MENÚ PRINCIPAL", True, BLANCO)
    screen.blit(texto_menu, (boton_menu.centerx - texto_menu.get_width()//2, 
                            boton_menu.centery - texto_menu.get_height()//2))
    
    return boton_continuar, boton_menu

# Función para dibujar pantalla de game over
def draw_game_over(screen, player, puntuacion, nivel_actual):
    # Fondo semitransparente
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    
    # Panel de game over
    panel_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
    pygame.draw.rect(screen, COLOR_INTERFAZ, panel_rect, border_radius=10)
    pygame.draw.rect(screen, ROJO, panel_rect, 3, border_radius=10)
    
    # Título
    texto_game_over = fuente_titulo.render("GAME OVER", True, ROJO)
    screen.blit(texto_game_over, (WIDTH//2 - texto_game_over.get_width()//2, HEIGHT//2 - 120))
    
    # Información del nivel
    if nivel_actual:
        nivel_text = fuente_grande.render(f"Nivel {nivel_actual.numero}: {nivel_actual.nombre}", True, BLANCO)
        screen.blit(nivel_text, (WIDTH//2 - nivel_text.get_width()//2, HEIGHT//2 - 70))
    
    # Estadísticas
    stats = [
        f"Puntuación: {puntuacion}",
        f"Nivel alcanzado: {player.level}",
        f"Fragmentos de código: {player.code_fragments}",
        f"Oro recolectado: {player.gold}"
    ]
    
    for i, stat in enumerate(stats):
        texto = fuente_media.render(stat, True, BLANCO)
        screen.blit(texto, (WIDTH//2 - texto.get_width()//2, HEIGHT//2 - 30 + i * 30))
    
    # Botones
    boton_reiniciar = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 + 80, 170, 50)
    boton_menu = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 80, 170, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Botón reiniciar
    color_reiniciar = VERDE if boton_reiniciar.collidepoint(mouse_pos) else (0, 200, 0)
    pygame.draw.rect(screen, color_reiniciar, boton_reiniciar, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_reiniciar, 2, border_radius=5)
    
    texto_reiniciar = fuente_media.render("REINICIAR NIVEL", True, BLANCO)
    screen.blit(texto_reiniciar, (boton_reiniciar.centerx - texto_reiniciar.get_width()//2, 
                                 boton_reiniciar.centery - texto_reiniciar.get_height()//2))
    
    # Botón menú principal
    color_menu = AZUL if boton_menu.collidepoint(mouse_pos) else (0, 0, 200)
    pygame.draw.rect(screen, color_menu, boton_menu, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_menu, 2, border_radius=5)
    
    texto_menu = fuente_media.render("MENÚ PRINCIPAL", True, BLANCO)
    screen.blit(texto_menu, (boton_menu.centerx - texto_menu.get_width()//2, 
                            boton_menu.centery - texto_menu.get_height()//2))
    
    return boton_reiniciar, boton_menu

# Función para dibujar el inventario
def draw_inventory(screen, player):
    # Fondo semitransparente
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    
    # Panel del inventario
    panel_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
    pygame.draw.rect(screen, COLOR_INTERFAZ, panel_rect, border_radius=10)
    pygame.draw.rect(screen, BLANCO, panel_rect, 2, border_radius=10)
    
    # Título
    texto_inventario = fuente_titulo.render("INVENTARIO", True, COLOR_TEXTO)
    screen.blit(texto_inventario, (WIDTH//2 - texto_inventario.get_width()//2, HEIGHT//2 - 180))
    
    # Información del personaje
    stats = [
        f"Nivel: {player.level}",
        f"EXP: {player.exp}/{player.exp_to_next_level}",
        f"Ataque: {player.attack_power}",
        f"Defensa: {player.defense}",
        f"Vida: {player.health}/{player.max_health}",
        f"Maná: {player.mana}/{player.max_mana}"
    ]
    
    for i, stat in enumerate(stats):
        texto = fuente_media.render(stat, True, BLANCO)
        screen.blit(texto, (WIDTH//2 - 200, HEIGHT//2 - 120 + i * 30))
    
    # Objetos del inventario
    texto_objetos = fuente_grande.render("OBJETOS:", True, COLOR_TEXTO)
    screen.blit(texto_objetos, (WIDTH//2 - 200, HEIGHT//2 + 60))
    
    if player.inventory:
        for i, item in enumerate(player.inventory[:5]):  # Mostrar solo los primeros 5 objetos
            texto_item = fuente_media.render(f"- {item}", True, BLANCO)
            screen.blit(texto_item, (WIDTH//2 - 180, HEIGHT//2 + 100 + i * 25))
    else:
        texto_vacio = fuente_media.render("El inventario está vacío", True, BLANCO)
        screen.blit(texto_vacio, (WIDTH//2 - 180, HEIGHT//2 + 100))
    
    # Botón cerrar
    boton_cerrar = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 230, 100, 40)
    mouse_pos = pygame.mouse.get_pos()
    
    color_cerrar = ROJO if boton_cerrar.collidepoint(mouse_pos) else (200, 0, 0)
    pygame.draw.rect(screen, color_cerrar, boton_cerrar, border_radius=5)
    pygame.draw.rect(screen, BLANCO, boton_cerrar, 2, border_radius=5)
    
    texto_cerrar = fuente_media.render("CERRAR", True, BLANCO)
    screen.blit(texto_cerrar, (boton_cerrar.centerx - texto_cerrar.get_width()//2, 
                              boton_cerrar.centery - texto_cerrar.get_height()//2))
    
    return boton_cerrar

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    running = True
    
    # Estado del juego
    estado_juego = EstadoJuego.MENU
    puntuacion = 0
    nivel_actual = None
    enemigos_eliminados = 0
    tiempo_inicio_nivel = 0
    tiempo_restante = 0
    
    # Grupos de sprites
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_projectiles = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    
    # Crear jugador
    player = Player()
    
    # Efectos de glitch
    glitch_effect = GlitchEffect()
    efectos_especiales = EfectosEspeciales()
    
    # Temporizador para pantalla azul
    blue_screen_timer = 0
    
    # Temporizador para spawn de enemigos
    spawn_timer = 0
    
    # Bucle principal del juego
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if estado_juego == EstadoJuego.JUGANDO:
                    if event.key == pygame.K_ESCAPE:
                        estado_juego = EstadoJuego.PAUSA
                    
                    elif event.key == pygame.K_SPACE:
                        # Disparar proyectil
                        projectile = Projectile(player.rect.centerx, player.rect.centery, 1, True, player.attack_power)
                        player_projectiles.add(projectile)
                        all_sprites.add(projectile)
                        efectos_especiales.agregar_explosion(player.rect.centerx, player.rect.centery, "magica", AZUL)
                    
                    elif event.key == pygame.K_q:
                        # Usar habilidad
                        if player.use_skill(enemies, enemy_projectiles):
                            efectos_especiales.agregar_texto_flotante(
                                player.skills[player.selected_skill], 
                                player.rect.centerx, player.rect.centery,
                                CIAN
                            )
                    
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        # Cambiar habilidad
                        player.selected_skill = event.key - pygame.K_1
                        efectos_especiales.agregar_texto_flotante(
                            f"Habilidad: {player.skills[player.selected_skill]}", 
                            player.rect.centerx, player.rect.centery,
                            AMARILLO
                        )
                    
                    elif event.key == pygame.K_i:
                        # Abrir inventario
                        estado_juego = EstadoJuego.INVENTARIO
                
                elif estado_juego == EstadoJuego.PAUSA:
                    if event.key == pygame.K_ESCAPE:
                        estado_juego = EstadoJuego.JUGANDO
                
                elif estado_juego == EstadoJuego.INVENTARIO:
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        estado_juego = EstadoJuego.JUGANDO
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if estado_juego == EstadoJuego.MENU:
                    boton_jugar, boton_niveles, boton_salir = draw_main_menu(screen, glitch_effect)
                    if boton_jugar.collidepoint(mouse_pos):
                        # Comenzar desde el primer nivel desbloqueado
                        for nivel in niveles:
                            if nivel.desbloqueado:
                                nivel_actual = nivel
                                break
                        
                        if nivel_actual:
                            estado_juego = EstadoJuego.JUGANDO
                            # Reiniciar juego para el nivel
                            player = Player()
                            all_sprites = pygame.sprite.Group()
                            enemies = pygame.sprite.Group()
                            player_projectiles = pygame.sprite.Group()
                            enemy_projectiles = pygame.sprite.Group()
                            
                            all_sprites.add(player)
                            platforms = generate_level(nivel_actual.numero)
                            all_sprites.add(platforms)
                            
                            # Inicializar contadores del nivel
                            enemigos_eliminados = 0
                            tiempo_inicio_nivel = pygame.time.get_ticks()
                            tiempo_restante = nivel_actual.tiempo_limite if nivel_actual.tiempo_limite else 0
                            
                            # Crear enemigos iniciales
                            for i in range(5 + nivel_actual.dificultad):
                                enemy_type = random.choice(["slime", "skeleton", "bat"])
                                enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), enemy_type, nivel_actual.dificultad)
                                enemies.add(enemy)
                                all_sprites.add(enemy)
                            
                            puntuacion = 0
                    
                    elif boton_niveles.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.SELECCION_NIVEL
                    
                    elif boton_salir.collidepoint(mouse_pos):
                        running = False
                
                elif estado_juego == EstadoJuego.SELECCION_NIVEL:
                    nivel_buttons, boton_regreso = draw_level_selection(screen, niveles)
                    
                    if boton_regreso.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.MENU
                    
                    for nivel_rect, nivel in nivel_buttons:
                        if nivel_rect.collidepoint(mouse_pos) and nivel.desbloqueado:
                            nivel_actual = nivel
                            estado_juego = EstadoJuego.JUGANDO
                            
                            # Reiniciar juego para el nivel seleccionado
                            player = Player()
                            all_sprites = pygame.sprite.Group()
                            enemies = pygame.sprite.Group()
                            player_projectiles = pygame.sprite.Group()
                            enemy_projectiles = pygame.sprite.Group()
                            
                            all_sprites.add(player)
                            platforms = generate_level(nivel_actual.numero)
                            all_sprites.add(platforms)
                            
                            # Inicializar contadores del nivel
                            enemigos_eliminados = 0
                            tiempo_inicio_nivel = pygame.time.get_ticks()
                            tiempo_restante = nivel_actual.tiempo_limite if nivel_actual.tiempo_limite else 0
                            
                            # Crear enemigos iniciales
                            for i in range(5 + nivel_actual.dificultad):
                                enemy_type = random.choice(["slime", "skeleton", "bat"])
                                enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), enemy_type, nivel_actual.dificultad)
                                enemies.add(enemy)
                                all_sprites.add(enemy)
                            
                            puntuacion = 0
                
                elif estado_juego == EstadoJuego.PAUSA:
                    boton_continuar, boton_menu = draw_pause_menu(screen)
                    if boton_continuar.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.JUGANDO
                    elif boton_menu.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.MENU
                
                elif estado_juego == EstadoJuego.GAME_OVER:
                    boton_reiniciar, boton_menu = draw_game_over(screen, player, puntuacion, nivel_actual)
                    if boton_reiniciar.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.JUGANDO
                        # Reiniciar nivel
                        player = Player()
                        all_sprites = pygame.sprite.Group()
                        enemies = pygame.sprite.Group()
                        player_projectiles = pygame.sprite.Group()
                        enemy_projectiles = pygame.sprite.Group()
                        
                        all_sprites.add(player)
                        platforms = generate_level(nivel_actual.numero)
                        all_sprites.add(platforms)
                        
                        # Reiniciar contadores del nivel
                        enemigos_eliminados = 0
                        tiempo_inicio_nivel = pygame.time.get_ticks()
                        tiempo_restante = nivel_actual.tiempo_limite if nivel_actual.tiempo_limite else 0
                        
                        for i in range(5 + nivel_actual.dificultad):
                            enemy_type = random.choice(["slime", "skeleton", "bat"])
                            enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), enemy_type, nivel_actual.dificultad)
                            enemies.add(enemy)
                            all_sprites.add(enemy)
                        
                        puntuacion = 0
                    
                    elif boton_menu.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.MENU
                
                elif estado_juego == EstadoJuego.VICTORIA:
                    boton_siguiente, boton_repetir, boton_menu = draw_victory_screen(screen, nivel_actual, nivel_actual.estrellas, enemigos_eliminados, tiempo_restante)
                    
                    if boton_siguiente.collidepoint(mouse_pos) and nivel_actual.numero < len(niveles):
                        # Desbloquear siguiente nivel
                        siguiente_nivel = niveles[nivel_actual.numero]  # El índice es nivel.numero - 1
                        siguiente_nivel.desbloqueado = True
                        
                        # Ir al siguiente nivel
                        nivel_actual = siguiente_nivel
                        estado_juego = EstadoJuego.JUGANDO
                        
                        # Reiniciar juego para el nuevo nivel
                        player = Player()
                        all_sprites = pygame.sprite.Group()
                        enemies = pygame.sprite.Group()
                        player_projectiles = pygame.sprite.Group()
                        enemy_projectiles = pygame.sprite.Group()
                        
                        all_sprites.add(player)
                        platforms = generate_level(nivel_actual.numero)
                        all_sprites.add(platforms)
                        
                        # Inicializar contadores del nivel
                        enemigos_eliminados = 0
                        tiempo_inicio_nivel = pygame.time.get_ticks()
                        tiempo_restante = nivel_actual.tiempo_limite if nivel_actual.tiempo_limite else 0
                        
                        # Crear enemigos iniciales
                        for i in range(5 + nivel_actual.dificultad):
                            enemy_type = random.choice(["slime", "skeleton", "bat"])
                            enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), enemy_type, nivel_actual.dificultad)
                            enemies.add(enemy)
                            all_sprites.add(enemy)
                        
                        puntuacion = 0
                    
                    elif boton_repetir.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.JUGANDO
                        # Reiniciar nivel actual
                        player = Player()
                        all_sprites = pygame.sprite.Group()
                        enemies = pygame.sprite.Group()
                        player_projectiles = pygame.sprite.Group()
                        enemy_projectiles = pygame.sprite.Group()
                        
                        all_sprites.add(player)
                        platforms = generate_level(nivel_actual.numero)
                        all_sprites.add(platforms)
                        
                        # Reiniciar contadores del nivel
                        enemigos_eliminados = 0
                        tiempo_inicio_nivel = pygame.time.get_ticks()
                        tiempo_restante = nivel_actual.tiempo_limite if nivel_actual.tiempo_limite else 0
                        
                        for i in range(5 + nivel_actual.dificultad):
                            enemy_type = random.choice(["slime", "skeleton", "bat"])
                            enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), enemy_type, nivel_actual.dificultad)
                            enemies.add(enemy)
                            all_sprites.add(enemy)
                        
                        puntuacion = 0
                    
                    elif boton_menu.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.MENU
                
                elif estado_juego == EstadoJuego.INVENTARIO:
                    boton_cerrar = draw_inventory(screen, player)
                    if boton_cerrar.collidepoint(mouse_pos):
                        estado_juego = EstadoJuego.JUGANDO
        
        # Actualizar
        if estado_juego == EstadoJuego.JUGANDO and nivel_actual:
            # Actualizar tiempo restante
            if nivel_actual.tiempo_limite:
                tiempo_transcurrido = (pygame.time.get_ticks() - tiempo_inicio_nivel) // 1000
                tiempo_restante = max(0, nivel_actual.tiempo_limite - tiempo_transcurrido)
                
                # Verificar si se acabó el tiempo
                if tiempo_restante <= 0:
                    estado_juego = EstadoJuego.GAME_OVER
            
            keys = pygame.key.get_pressed()
            player.update(keys, platforms)
            
            # Actualizar enemigos
            for enemy in enemies:
                enemy.update(player)
                
                # Los enemigos disparan ocasionalmente
                if random.random() < 0.01:  # 1% de probabilidad por frame
                    dx = player.rect.centerx - enemy.rect.centerx
                    direction = 1 if dx > 0 else -1
                    projectile = Projectile(enemy.rect.centerx, enemy.rect.centery, direction, False, enemy.attack_power)
                    enemy_projectiles.add(projectile)
                    all_sprites.add(projectile)
            
            # Actualizar proyectiles
            player_projectiles.update()
            enemy_projectiles.update()
            
            # Actualizar plataformas
            platforms.update()
            
            # Actualizar efectos de glitch
            glitch_effect.update()
            
            # Actualizar efectos especiales
            efectos_especiales.actualizar()
            
            # Detectar colisiones entre proyectiles del jugador y enemigos
            for projectile in player_projectiles:
                enemy_hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in enemy_hits:
                    if enemy.take_damage(projectile.power):
                        enemy.kill()
                        player.gold += random.randint(1, 5)
                        player.code_fragments += random.randint(0, 1)
                        player.add_exp(enemy.exp_value)
                        puntuacion += enemy.exp_value * 10
                        enemigos_eliminados += 1
                        efectos_especiales.agregar_texto_flotante(
                            f"+{enemy.exp_value} EXP", 
                            enemy.rect.centerx, enemy.rect.centery,
                            AMARILLO
                        )
                        efectos_especiales.agregar_explosion(enemy.rect.centerx, enemy.rect.centery, "normal", ROJO)
                    projectile.kill()
            
            # Detectar colisiones entre proyectiles enemigos y el jugador
            for projectile in enemy_projectiles:
                if projectile.rect.colliderect(player.rect):
                    if player.take_damage(projectile.power):
                        # Jugador muerto
                        estado_juego = EstadoJuego.GAME_OVER
                        efectos_especiales.agregar_explosion(player.rect.centerx, player.rect.centery, "normal", ROJO)
                    projectile.kill()
            
            # Detectar colisiones entre jugador y enemigos
            enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in enemy_hits:
                if player.take_damage(enemy.attack_power // 2):
                    estado_juego = EstadoJuego.GAME_OVER
                    efectos_especiales.agregar_explosion(player.rect.centerx, player.rect.centery, "normal", ROJO)
            
            # Verificar si se completó el nivel
            if enemigos_eliminados >= nivel_actual.enemigos_requeridos:
                # Calcular estrellas obtenidas
                estrellas_obtenidas = nivel_actual.calcular_estrellas(
                    enemigos_eliminados, 
                    tiempo_restante, 
                    player.health / player.max_health * 100
                )
                
                # Actualizar mejor puntuación
                nivel_actual.mejor_puntuacion = max(nivel_actual.mejor_puntuacion, puntuacion)
                nivel_actual.completado = True
                
                # Desbloquear siguiente nivel si existe
                if nivel_actual.numero < len(niveles):
                    siguiente_nivel = niveles[nivel_actual.numero]  # El índice es nivel.numero - 1
                    siguiente_nivel.desbloqueado = True
                
                estado_juego = EstadoJuego.VICTORIA
            
            # Efectos de glitch aleatorios
            if random.random() < 0.01:  # 1% de probabilidad por frame
                glitch_effect.trigger(random.choice(["screen_shake", "color_shift", "scan_lines", "pixel_glitch"]))
            
            # Pantalla azul ocasional
            if blue_screen_timer <= 0 and random.random() < 0.002:  # 0.2% de probabilidad por frame
                blue_screen_timer = 30  # Mostrar durante 30 frames
                glitch_effect.trigger("color_shift")
            elif blue_screen_timer > 0:
                blue_screen_timer -= 1
            
            # Spawn de nuevos enemigos
            spawn_timer += 1
            if spawn_timer >= 300:  # Cada 5 segundos aproximadamente
                spawn_timer = 0
                if len(enemies) < 10 + nivel_actual.dificultad:  # Máximo enemigos según dificultad
                    enemy_type = random.choice(["slime", "skeleton", "bat"])
                    # Spawn en los bordes de la pantalla
                    side = random.choice(["left", "right", "top", "bottom"])
                    if side == "left":
                        x = 0
                        y = random.randint(0, HEIGHT)
                    elif side == "right":
                        x = WIDTH
                        y = random.randint(0, HEIGHT)
                    elif side == "top":
                        x = random.randint(0, WIDTH)
                        y = 0
                    else:  # bottom
                        x = random.randint(0, WIDTH)
                        y = HEIGHT
                    
                    enemy = Enemy(x, y, enemy_type, nivel_actual.dificultad)
                    enemies.add(enemy)
                    all_sprites.add(enemy)
                    efectos_especiales.agregar_explosion(x, y, "magica", PURPURA)
        
        # Dibujar
        screen.fill(COLOR_FONDO)
        
        if estado_juego == EstadoJuego.MENU:
            draw_main_menu(screen, glitch_effect)
            
        elif estado_juego == EstadoJuego.SELECCION_NIVEL:
            draw_level_selection(screen, niveles)
            
        elif estado_juego == EstadoJuego.JUGANDO:
            # Dibujar sprites
            for platform in platforms:
                if platform.visible:
                    screen.blit(platform.image, platform.rect)
                    
            for sprite in all_sprites:
                if sprite not in platforms or (sprite in platforms and sprite.visible):
                    if sprite != player or blue_screen_timer <= 0:  # No dibujar jugador durante pantalla azul
                        screen.blit(sprite.image, sprite.rect)
            
            # Aplicar efectos de glitch
            glitch_effect.apply(screen)
            
            # Dibujar HUD
            draw_hud(screen, player, glitch_effect, estado_juego, nivel_actual, enemigos_eliminados, tiempo_restante)
            
            # Dibujar efectos especiales
            efectos_especiales.dibujar(screen, fuente_media)
            
            # Mostrar pantalla azul si está activa
            if blue_screen_timer > 0:
                blue_screen = pygame.Surface((WIDTH, HEIGHT))
                blue_screen.fill((0, 0, 170))  # Azul de pantalla de error
                error_text = fuente_grande.render("ERROR DEL SISTEMA", True, BLANCO)
                blue_screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 - 50))
                
                details_text = fuente_media.render("SISTEMA RECUPERÁNDOSE...", True, BLANCO)
                blue_screen.blit(details_text, (WIDTH//2 - details_text.get_width()//2, HEIGHT//2))
                
                code_text = fuente_pequena.render(f"Error: 0x{random.randint(0x1000, 0xFFFF):04X}", True, BLANCO)
                blue_screen.blit(code_text, (WIDTH//2 - code_text.get_width()//2, HEIGHT//2 + 50))
                
                screen.blit(blue_screen, (0, 0))
                
        elif estado_juego == EstadoJuego.PAUSA:
            # Dibujar juego en pausa
            for platform in platforms:
                if platform.visible:
                    screen.blit(platform.image, platform.rect)
                    
            for sprite in all_sprites:
                if sprite not in platforms or (sprite in platforms and sprite.visible):
                    screen.blit(sprite.image, sprite.rect)
            
            draw_hud(screen, player, glitch_effect, estado_juego, nivel_actual, enemigos_eliminados, tiempo_restante)
            draw_pause_menu(screen)
            
        elif estado_juego == EstadoJuego.GAME_OVER:
            # Dibujar juego con filtro oscuro
            for platform in platforms:
                if platform.visible:
                    screen.blit(platform.image, platform.rect)
                    
            for sprite in all_sprites:
                if sprite not in platforms or (sprite in platforms and sprite.visible):
                    screen.blit(sprite.image, sprite.rect)
            
            # Aplicar filtro oscuro
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            screen.blit(s, (0, 0))
            
            draw_game_over(screen, player, puntuacion, nivel_actual)
            
        elif estado_juego == EstadoJuego.VICTORIA:
            # Dibujar juego con filtro de victoria
            for platform in platforms:
                if platform.visible:
                    screen.blit(platform.image, platform.rect)
                    
            for sprite in all_sprites:
                if sprite not in platforms or (sprite in platforms and sprite.visible):
                    screen.blit(sprite.image, sprite.rect)
            
            # Aplicar filtro de victoria
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 50, 0, 100))  # Verde semitransparente
            screen.blit(s, (0, 0))
            
            draw_victory_screen(screen, nivel_actual, nivel_actual.estrellas, enemigos_eliminados, tiempo_restante)
            
        elif estado_juego == EstadoJuego.INVENTARIO:
            # Dibujar juego
            for platform in platforms:
                if platform.visible:
                    screen.blit(platform.image, platform.rect)
                    
            for sprite in all_sprites:
                if sprite not in platforms or (sprite in platforms and sprite.visible):
                    screen.blit(sprite.image, sprite.rect)
            
            draw_hud(screen, player, glitch_effect, estado_juego, nivel_actual, enemigos_eliminados, tiempo_restante)
            draw_inventory(screen, player)
        
        # Dibujar partículas
        for particula in particulas:
            particula.draw(screen)
        
        pygame.display.flip()
        
        # Controlar FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
import pygame
import math
from pgzero.builtins import images
from src.animation import SpriteAnimation
from src.settings import GRID_SIZE, GREEN

class Hero:
    def __init__(self, x, y, dungeon):
        self.grid_x = x                # Posição do personagem no grid (coluna)
        self.grid_y = y                # Posição do personagem no grid (linha)
        self.pixel_x = x * GRID_SIZE   # Posição em pixels no eixo X (para desenhar na tela)
        self.pixel_y = y * GRID_SIZE   # Posição em pixels no eixo Y (para desenhar na tela)
        self.target_x = self.pixel_x   # Destino em pixels no eixo X (usado para animação de movimento)
        self.target_y = self.pixel_y   # Destino em pixels no eixo Y (usado para animação de movimento)
        self.moving = False            # Indica se o personagem está se movendo
        self.move_speed = 200          # Velocidade de movimento em pixels por segundo
        self.dungeon = dungeon

        # Animações do herói
        self.idle_animation = SpriteAnimation([
            images.hero_idle0,
            images.hero_idle1
        ], 0.5)
        self.idle_animation_right = SpriteAnimation([
            images.hero_walk_right0,
            images.hero_walk_right1,
        ], 0.15)
        self.idle_animation_left = SpriteAnimation([
            images.hero_walk_left0,
            images.hero_walk_left1,
        ], 0.15)
        self.victory_animation = SpriteAnimation([
            images.hero_victory0,
            images.hero_victory1
        ], 0.4)
        self.current_animation = self.idle_animation
        # Vida do herói
        self.health = 100
        self.max_health = 100

    def can_move_to(self, x, y):
        # Outros inimigos não podem passar por paredes
        return not self.dungeon.is_wall(x, y)

    def move(self, dx, dy, is_bomb_at):
        # Só permite iniciar o movimento se o herói não estiver se movendo atualmente
        if not self.moving:
            new_x = self.grid_x + dx  # Calcula a nova posição no grid (coluna)
            new_y = self.grid_y + dy  # Calcula a nova posição no grid (linha)

            # Verifica se pode mover para a nova posição (não é parede e não tem bomba)
            if self.can_move_to(new_x, new_y) and not is_bomb_at(new_x, new_y):
                self.grid_x = new_x  # Atualiza a posição do herói no grid
                self.grid_y = new_y
                self.target_x = new_x * GRID_SIZE  # Define o destino em pixels (usado para animação)
                self.target_y = new_y * GRID_SIZE
                self.moving = True  # Marca que o herói está em movimento
                # Atualiza direção e animação do herói
                if dx > 0:
                    self.current_animation = self.idle_animation_right
                elif dx < 0:
                    self.current_animation = self.idle_animation_left
                else:
                    self.current_animation = self.idle_animation

    def update(self, dt):
        # Atualizar movimento
        if self.moving:
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y
            distance = math.sqrt(dx*dx + dy*dy)
            move_distance = self.move_speed * dt

            if distance <= move_distance:  # Chegou ao destino
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.current_animation = self.idle_animation
                self.current_animation.current_frame = 0
                self.current_animation.time_since_last_frame = 0
            else:
                # Mover em direção ao alvo
                move_distance = self.move_speed * dt
                self.pixel_x += (dx / distance) * move_distance
                self.pixel_y += (dy / distance) * move_distance

    # Atualizar animação, mesmo parado
        if self.current_animation:
            self.current_animation.update(dt)
    
    def draw(self, screen):
        # Obtém o frame atual da animação do herói
        frame = self.current_animation.get_current_frame()
        # Desenha o frame do herói na posição em pixels
        screen.blit(frame, (self.pixel_x, self.pixel_y))

        # Desenhar barra de vida acima do herói
        health_width = int((self.health / self.max_health) * GRID_SIZE)  # Calcula largura proporcional à vida
        health_rect = pygame.Rect(self.pixel_x, self.pixel_y - 8, health_width, 4)  # Retângulo da barra de vida
        screen.draw.filled_rect(health_rect, GREEN)  # Desenha a barra de vida em verde

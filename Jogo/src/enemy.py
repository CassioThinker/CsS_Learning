import pygame
import math
import random
from pgzero.actor import Actor
from src.animation import SpriteAnimation
from src.settings import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, RED

class Enemy:
    def __init__(self, x, y, enemy_type, dungeon, hero):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * GRID_SIZE
        self.pixel_y = y * GRID_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.moving = False
        self.enemy_type = enemy_type
        self.facing_right = True
        self.dungeon = dungeon
        self.hero = hero

        if enemy_type == "slime":
            self.move_speed = 80
            self.health = 30
            self.max_health = 30
            self.damage = 10
            self.move_timer = 0
            self.move_interval = 2.0
            self.actor = Actor("slime_idle0", (self.pixel_x + GRID_SIZE // 2, self.pixel_y + GRID_SIZE // 2))
            # Animações do slime
            self.idle_animation = SpriteAnimation(['slime_idle0', 'slime_idle1'], 0.8)
            self.idle_animation_right = SpriteAnimation(['slime_walk_right0', 'slime_walk_right1'], 0.3)
            self.idle_animation_left = SpriteAnimation(['slime_walk_left0', 'slime_walk_left1'], 0.3)
            self.current_animation = self.idle_animation

        elif enemy_type == "golem":
            self.move_speed = 40
            self.health = 80
            self.max_health = 80
            self.damage = 25
            self.move_timer = 0
            self.move_interval = 3.0
            self.actor = Actor("golem_idle0", (self.pixel_x + GRID_SIZE // 2, self.pixel_y + GRID_SIZE // 2))
            # Animações do golem
            self.idle_animation = SpriteAnimation(['golem_idle0', 'golem_idle1'], 0.8)
            self.idle_animation_right = SpriteAnimation(['golem_walk_right0', 'golem_walk_right1'], 0.3)
            self.idle_animation_left = SpriteAnimation(['golem_walk_left0', 'golem_walk_left1'], 0.3)
            self.current_animation = self.idle_animation

        elif enemy_type == "specter":
            self.move_speed = 120
            self.health = 20
            self.max_health = 20
            self.damage = 15
            self.move_timer = 0
            self.move_interval = 1.5
            self.can_pass_walls = True
            self.actor = Actor("specter_idle0", (self.pixel_x + GRID_SIZE // 2, self.pixel_y + GRID_SIZE // 2))
            # Animações do specter
            self.idle_animation = SpriteAnimation(['specter_idle0', 'specter_idle1'], 0.8)
            self.idle_animation_right = SpriteAnimation(['specter_walk_right0', 'specter_walk_right1'], 0.8)
            self.idle_animation_left = SpriteAnimation(['specter_walk_left0', 'specter_walk_left1'], 0.8)
            self.current_animation = self.idle_animation

        # Território de patrulha
        self.patrol_center_x = x
        self.patrol_center_y = y
        self.patrol_radius = 3
    
    def can_move_to(self, x, y):
        # Verificar limites
        if not (0 < x < GRID_WIDTH - 1 and 0 < y < GRID_HEIGHT - 1):
            return False
        
        # Espectros podem passar por paredes
        if hasattr(self, 'can_pass_walls') and self.can_pass_walls:
            return True
        
        # Outros inimigos não podem passar por paredes
        return not self.dungeon.is_wall(x, y)
    
    def move(self, dx, dy, is_bomb_at):
        # Só permite iniciar o movimento se o inimigo não estiver se movendo atualmente
        if not self.moving:
            new_x = self.grid_x + dx  # Calcula a nova posição no grid (coluna)
            new_y = self.grid_y + dy  # Calcula a nova posição no grid (linha)

            # Verifica se pode mover para a nova posição (não é parede e não tem bomba)
            if self.can_move_to(new_x, new_y) and not is_bomb_at(new_x, new_y):
                self.grid_x = new_x  # Atualiza a posição do inimigo no grid
                self.grid_y = new_y
                self.target_x = new_x * GRID_SIZE  # Define o destino em pixels (usado para animação)
                self.target_y = new_y * GRID_SIZE
                self.moving = True  # Marca que o inimigo está em movimento
                # Atualiza direção e animação conforme o movimento
                if self.enemy_type in ("slime", "golem", "specter"):
                    if dx > 0:
                        self.facing_right = True
                        self.current_animation = self.idle_animation_right
                    elif dx < 0:
                        self.facing_right = False
                        self.current_animation = self.idle_animation_left

    def update(self, dt):
        # Atualizar movimento
        if self.moving:
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 2:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.current_animation = self.idle_animation
            else:
                move_distance = self.move_speed * dt
                self.pixel_x += (dx / distance) * move_distance
                self.pixel_y += (dy / distance) * move_distance

        # Atualizar animação SEMPRE, mesmo parado
        if self.current_animation:
            self.current_animation.update(dt)
            if self.actor:
                frame_name = self.current_animation.get_current_frame()
                self.actor.image = frame_name
                self.actor.pos = (self.pixel_x + GRID_SIZE // 2, self.pixel_y + GRID_SIZE // 2)

        # IA de movimento
        self.move_timer += dt
        if self.move_timer >= self.move_interval and not self.moving:
            self.move_timer = 0
            self.ai_move()
        
        
    def ai_move(self):
        # Verificar se o herói está próximo
        hero_distance = math.sqrt((self.grid_x - self.hero.grid_x)**2 + (self.grid_y - self.hero.grid_y)**2)
        
        if hero_distance <= 4:
            # Persegue o herói se estiver próximo
            dx = self.hero.grid_x - self.grid_x
            dy = self.hero.grid_y - self.grid_y
            # Move na direção do herói (prioridade para eixo X)
            if abs(dx) > abs(dy):
                step_x = 1 if dx > 0 else -1
                step_y = 0
            else:
                step_x = 0
                step_y = 1 if dy > 0 else -1
            # Só move se não estiver na mesma célula
            if self.grid_x != self.hero.grid_x or self.grid_y != self.hero.grid_y:
                self.move(step_x, step_y, lambda x, y: False) # Inimigos não se importam com bombas ao se mover
            else:
                self.attack_hero()
        else:
            self.patrol()
    
    def patrol(self):
        # Movimento aleatório dentro do território de patrulha do inimigo
        possible_moves = []
        # Testa os quatro movimentos possíveis: baixo, cima, direita, esquerda
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            
            # Verifica se a nova posição está dentro do raio de patrulha e se é possível mover para lá
            distance_from_center = math.sqrt((new_x - self.patrol_center_x)**2 + (new_y - self.patrol_center_y)**2)
            if distance_from_center <= self.patrol_radius and self.can_move_to(new_x, new_y):
                possible_moves.append((dx, dy))
        
        # Se houver movimentos possíveis, escolhe um aleatoriamente e move o inimigo
        if possible_moves:
            dx, dy = random.choice(possible_moves)
            self.move(dx, dy, lambda x, y: False)
    
    def attack_hero(self):
        # Função chamada quando o inimigo ataca o herói
        self.hero.health -= self.damage  # Diminui a vida do herói de acordo com o dano do inimigo
    
    def draw(self, screen):
        # Desenha o inimigo na tela
        if self.enemy_type in ("slime", "golem", "specter") and self.actor:
            self.actor.draw()  # Desenha o sprite do inimigo

        # Barra de vida do inimigo
        health_width = int((self.health / self.max_health) * GRID_SIZE)  # Calcula a largura proporcional à vida
        health_rect = pygame.Rect(self.pixel_x, self.pixel_y - 8, health_width, 4)  # Retângulo da barra de vida
        screen.draw.filled_rect(health_rect, RED)  # Desenha a barra de vida

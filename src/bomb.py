import pygame
from pgzero.builtins import sounds
from src.settings import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT

class Bomb:
    def __init__(self, x, y, rounds_to_explode=2, radius=2):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * GRID_SIZE
        self.pixel_y = y * GRID_SIZE
        self.rounds_to_explode = rounds_to_explode  # Rodadas até explodir
        self.radius = radius
        self.exploded = False
        self.explosion_timer = 0  # Tempo que a explosão fica visível

    def update(self, dt):
        if self.exploded:
            self.explosion_timer -= dt  # Conta o tempo da explosão

    def tick_round(self, dungeon, enemies, play_sound):
        # Se a bomba ainda não explodiu, diminui o contador de rodadas até explodir.
        if not self.exploded:
            self.rounds_to_explode -= 1
            # Quando o contador chega a zero ou menos, a bomba explode.
            if self.rounds_to_explode <= 0:
                self.explode(dungeon, enemies, play_sound)

    def explode(self, dungeon, enemies, play_sound):
        self.exploded = True
        self.explosion_timer = 0.4  # explosão visível por 0.4 segundos

        # Toca o som de explosão
        play_sound('explosion') 

        # Explode no centro
        self._explode_cell(self.grid_x, self.grid_y, dungeon, enemies)

        # Explode nos eixos X e Y
        for d in range(1, self.radius + 1):
            # Direita
            self._explode_cell(self.grid_x + d, self.grid_y, dungeon, enemies)
            # Esquerda
            self._explode_cell(self.grid_x - d, self.grid_y, dungeon, enemies)
            # Baixo
            self._explode_cell(self.grid_x, self.grid_y + d, dungeon, enemies)
            # Cima
            self._explode_cell(self.grid_x, self.grid_y - d, dungeon, enemies)

    def _explode_cell(self, x, y, dungeon, enemies):
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            # Não destruir paredes das bordas
            if (x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1):
                return
            if dungeon.grid[y][x] == 1:  # Se for parede interna
                dungeon.grid[y][x] = 0  # Remove parede
            # Causar dano em inimigos
            for enemy in enemies:
                if enemy.grid_x == x and enemy.grid_y == y:
                    enemy.health -= 50

    def draw(self, screen):
        if not self.exploded:
            rect = pygame.Rect(self.pixel_x, self.pixel_y, GRID_SIZE, GRID_SIZE)
            screen.draw.filled_rect(rect, (200, 200, 0))
        elif self.explosion_timer > 0:
            # Cor da explosão: laranja
            explosion_color = (255, 140, 0)
            # Centro
            rect = pygame.Rect(self.pixel_x, self.pixel_y, GRID_SIZE, GRID_SIZE)
            screen.draw.filled_rect(rect, explosion_color)
            # Eixos
            for d in range(1, self.radius + 1):
                # Direita
                rect = pygame.Rect(self.pixel_x + d * GRID_SIZE, self.pixel_y, GRID_SIZE, GRID_SIZE)
                screen.draw.filled_rect(rect, explosion_color)
                # Esquerda
                rect = pygame.Rect(self.pixel_x - d * GRID_SIZE, self.pixel_y, GRID_SIZE, GRID_SIZE)
                screen.draw.filled_rect(rect, explosion_color)
                # Baixo
                rect = pygame.Rect(self.pixel_x, self.pixel_y + d * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                screen.draw.filled_rect(rect, explosion_color)
                # Cima
                rect = pygame.Rect(self.pixel_x, self.pixel_y - d * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                screen.draw.filled_rect(rect, explosion_color)

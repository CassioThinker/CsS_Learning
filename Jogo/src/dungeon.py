import pygame
import random
from src.settings import GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, BROWN, BLACK

class Dungeon:
    def __init__(self):
        # Cria uma matriz (lista de listas) representando o grid do labirinto, preenchida inicialmente com zeros (células livres)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generate_dungeon()  # Chama o método para gerar o labirinto, preenchendo a matriz com paredes e caminhos
    
    def generate_dungeon(self):
        # Gerar um labirinto simples
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Paredes nas bordas
                if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                    self.grid[y][x] = 1
                # Algumas paredes internas aleatórias
                elif random.random() < 0.2:
                    self.grid[y][x] = 1
                else:
                    self.grid[y][x] = 0
        
        # Garantir que a posição inicial do herói esteja livre
        self.grid[1][1] = 0  # Porta de entrada sempre livre
        # Garante pelo menos uma saída para o herói (direita e/ou baixo)
        self.grid[1][2] = 0  # Libera célula à direita do herói
        self.grid[2][1] = 0  # Libera célula abaixo do herói
        self.grid[GRID_HEIGHT-2][GRID_WIDTH-2] = 0  # Porta de saída sempre livre

        # Garante pelo menos uma saída para a porta de saída (direita e/ou cima)
        self.grid[GRID_HEIGHT-2][GRID_WIDTH-3] = 0  # Libera célula à esquerda da saída
        self.grid[GRID_HEIGHT-3][GRID_WIDTH-2] = 0  # Libera célula acima da saída
    
    def is_wall(self, x, y):
        # Verifica se a posição (x, y) está dentro dos limites do grid
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            # Retorna True se a célula for uma parede (valor 1 na matriz)
            return self.grid[y][x] == 1
        # Fora dos limites do grid é considerado parede
        return True
    
    def draw(self, screen):
        # Percorre todas as células do grid do labirinto
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.grid[y][x] == 1:  # Se for parede
                    screen.draw.filled_rect(rect, BROWN)  # Desenha a parede
                    screen.draw.rect(rect, BLACK)         # Desenha a borda da parede
                else:  # Se for chão
                    screen.draw.filled_rect(rect, (40, 40, 40))  # Desenha

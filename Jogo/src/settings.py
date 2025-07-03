# Configurações da tela
WIDTH = 800
HEIGHT = 600
TITLE = "O Labirinto Místico"

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3
NEXT_STAGE = 4

# Variáveis globais de turno
PLAYER_TURN = 0
ENEMY_TURN = 1
ENEMY_TURN_DELAY = 0.7  # segundos entre cada inimigo agir

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)

# Configurações do grid
GRID_SIZE = 32
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Posição da porta de entrada (onde o herói começa)
door_in_x, door_in_y = 1, 1

# Posição da porta de saída (lado oposto do mapa)
door_out_x, door_out_y = GRID_WIDTH - 2, GRID_HEIGHT - 2

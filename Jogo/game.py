import pgzrun
import pygame
import math
import random
from pgzero.builtins import sounds, music, images
from pgzero.actor import Actor

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

# Variáveis globais
game_state = MENU
music_enabled = True
sound_enabled = True
stage = 1
next_stage_timer = 0
game_over_sound_played = False
victory_anim_timer = 0

# Variável global para posição do mouse
mouse_pos = (0, 0)

# Variáveis globais de turno
PLAYER_TURN = 0
ENEMY_TURN = 1
turn = PLAYER_TURN
enemy_turn_index = 0  # Índice do inimigo que está jogando
ENEMY_TURN_DELAY = 0.7  # segundos entre cada inimigo agir
enemy_turn_timer = 0

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

# Mensagem de feedback para o jogador
feedback_message = ""
feedback_timer = 0

# Posição da porta de entrada (onde o herói começa)
door_in_x, door_in_y = 1, 1

# Posição da porta de saída (lado oposto do mapa)
door_out_x, door_out_y = GRID_WIDTH - 2, GRID_HEIGHT - 2

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def is_bomb_at(x, y):
    """
    Verifica se existe uma bomba não explodida na posição (x, y) do grid.

    Retorna True se encontrar uma bomba na lista global 'bombs' cuja posição coincide com (x, y)
    e que ainda não explodiu. Caso contrário, retorna False.

    Também garante que a posição consultada está dentro dos limites do grid.
    """
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return False
    for bomb in bombs:
        if bomb.grid_x == x and bomb.grid_y == y and not bomb.exploded:
            return True
    return False

def is_adjacent(x1, y1, x2, y2):
    """Determina se duas posições em uma grade estão diretamente próximas uma da outra, 
    seja horizontalmente ou verticalmente."""
    return abs(x1 - x2) + abs(y1 - y2) == 1

class SpriteAnimation:
    def __init__(self, frames, frame_duration=0.2):
        # Lista de imagens (frames) que compõem a animação
        self.frames = frames
        # Duração de cada frame em segundos
        self.frame_duration = frame_duration
        # Índice do frame atual da animação
        self.current_frame = 0
        # Tempo acumulado desde a última troca de frame
        self.time_since_last_frame = 0

    def update(self, dt):
        # Atualiza o tempo acumulado com o tempo decorrido desde o último frame
        self.time_since_last_frame += dt
        # Se passou o tempo suficiente, avança para o próximo frame
        if self.time_since_last_frame >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.time_since_last_frame = 0

    def get_current_frame(self):
        # Retorna o frame (imagem) atual da animação
        return self.frames[self.current_frame]

class Hero:
    def __init__(self, x, y):
        self.grid_x = x                # Posição do personagem no grid (coluna)
        self.grid_y = y                # Posição do personagem no grid (linha)
        self.pixel_x = x * GRID_SIZE   # Posição em pixels no eixo X (para desenhar na tela)
        self.pixel_y = y * GRID_SIZE   # Posição em pixels no eixo Y (para desenhar na tela)
        self.target_x = self.pixel_x   # Destino em pixels no eixo X (usado para animação de movimento)
        self.target_y = self.pixel_y   # Destino em pixels no eixo Y (usado para animação de movimento)
        self.moving = False            # Indica se o personagem está se movendo
        self.move_speed = 200          # Velocidade de movimento em pixels por segundo

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
        return not dungeon.is_wall(x, y)

    def move(self, dx, dy):
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

            if distance < 1:  # Chegou ao destino
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

class Button:
    def __init__(self, x, y, width, height, text, color=GRAY):
        # Cria um retângulo para representar a área do botão na tela
        self.rect = pygame.Rect(x, y, width, height)
        # Texto que será exibido no botão
        self.text = text
        # Cor padrão do botão
        self.color = color
        # Cor do botão quando o mouse está sobre ele (hover)
        self.hover_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        # Indica se o mouse está atualmente sobre o botão
        self.is_hovered = False
        # Indica se o mouse estava sobre o botão no frame anterior
        self.was_hovered = False

    def update(self, mouse_pos):
        # Atualiza o estado de hover do botão
        self.was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        # Se o mouse acabou de passar pelo botão, toca um som
        if self.is_hovered and not self.was_hovered:
            try:
                sounds.hover_sound.play()
            except:
                pass

    def draw(self, screen):
        # Escolhe a cor do botão dependendo se está em hover ou não
        color = self.hover_color if self.is_hovered else self.color
        # Desenha o retângulo do botão preenchido
        screen.draw.filled_rect(self.rect, color)
        # Desenha a borda do botão
        screen.draw.rect(self.rect, BLACK)
        # Desenha o texto centralizado no botão
        screen.draw.text(self.text, center=self.rect.center, fontsize=24, color=BLACK)

    def is_clicked(self, mouse_pos):
        # Retorna True se o mouse clicou dentro da área do botão
        return self.rect.collidepoint(mouse_pos)

# Botões do menu
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Começar o Jogo", GREEN)
music_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "Música: ON", BLUE)
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "Sair", RED)

# Objetos do jogo
hero = Hero(1, 1)
dungeon = Dungeon()
enemies = []
bombs = []
last_time = 0

class Enemy:
    def __init__(self, x, y, enemy_type="slime"):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * GRID_SIZE
        self.pixel_y = y * GRID_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.moving = False
        self.enemy_type = enemy_type
        self.facing_right = True

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
        return not dungeon.is_wall(x, y)
    
    def move(self, dx, dy):
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
        hero_distance = math.sqrt((self.grid_x - hero.grid_x)**2 + (self.grid_y - hero.grid_y)**2)
        
        if hero_distance <= 4:
            # Persegue o herói se estiver próximo
            dx = hero.grid_x - self.grid_x
            dy = hero.grid_y - self.grid_y
            # Move na direção do herói (prioridade para eixo X)
            if abs(dx) > abs(dy):
                step_x = 1 if dx > 0 else -1
                step_y = 0
            else:
                step_x = 0
                step_y = 1 if dy > 0 else -1
            # Só move se não estiver na mesma célula
            if self.grid_x != hero.grid_x or self.grid_y != hero.grid_y:
                self.move(step_x, step_y)
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
            self.move(dx, dy)
    
    def attack_hero(self):
        # Função chamada quando o inimigo ataca o herói
        global game_state
        hero.health -= self.damage  # Diminui a vida do herói de acordo com o dano do inimigo
        if hero.health <= 0:
            game_state = GAME_OVER  # Se a vida do herói chegar a zero, muda o estado do jogo para GAME OVER
    
    def draw(self, screen):
        # Desenha o inimigo na tela
        if self.enemy_type in ("slime", "golem", "specter") and self.actor:
            self.actor.draw()  # Desenha o sprite do inimigo

        # Barra de vida do inimigo
        health_width = int((self.health / self.max_health) * GRID_SIZE)  # Calcula a largura proporcional à vida
        health_rect = pygame.Rect(self.pixel_x, self.pixel_y - 8, health_width, 4)  # Retângulo da barra de vida
        screen.draw.filled_rect(health_rect, RED)  # Desenha a barra de vida

def remove_dead_enemies():
    """Remove todos os inimigos com vida menor ou igual a zero da lista global enemies."""
    global enemies
    enemies = [enemy for enemy in enemies if enemy.health > 0]

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

    def tick_round(self):
        # Se a bomba ainda não explodiu, diminui o contador de rodadas até explodir.
        if not self.exploded:
            self.rounds_to_explode -= 1
            # Quando o contador chega a zero ou menos, a bomba explode.
            if self.rounds_to_explode <= 0:
                self.explode()

    def explode(self):
        self.exploded = True
        self.explosion_timer = 0.4  # explosão visível por 0.4 segundos

        # Toca o som de explosão
        play_sound('explosion') 

        # Explode no centro
        self._explode_cell(self.grid_x, self.grid_y)

        # Explode nos eixos X e Y
        for d in range(1, self.radius + 1):
            # Direita
            self._explode_cell(self.grid_x + d, self.grid_y)
            # Esquerda
            self._explode_cell(self.grid_x - d, self.grid_y)
            # Baixo
            self._explode_cell(self.grid_x, self.grid_y + d)
            # Cima
            self._explode_cell(self.grid_x, self.grid_y - d)

    def _explode_cell(self, x, y):
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
        remove_dead_enemies()

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

# Função para avançar as bombas ao início do turno do jogador
def start_player_turn():
    global enemy_turn_timer
    for bomb in bombs:
        bomb.tick_round()
    bombs[:] = [b for b in bombs if not (b.exploded and b.explosion_timer <= 0)]
    enemy_turn_timer = 0  # zera o timer ao voltar para o jogador

def get_random_free_cell(exclude_cells=None):
    """
    Retorna uma célula aleatória livre do labirinto, excluindo as células passadas em exclude_cells.

    Percorre todas as células do grid (exceto as bordas) e adiciona à lista free_cells aquelas que:
    - Não são parede (dungeon.is_wall(x, y) == False)
    - Não estão na lista de exclusão (exclude_cells)

    Se houver células livres, retorna uma delas aleatoriamente.
    Caso contrário, retorna (1, 1) como posição padrão.
    """
    if exclude_cells is None:
        exclude_cells = []
    free_cells = []
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):
            if not dungeon.is_wall(x, y) and (x, y) not in exclude_cells:
                free_cells.append((x, y))
    return random.choice(free_cells) if free_cells else (1, 1)

def spawn_enemies():
    global enemies
    enemies = []
    used_cells = [(hero.grid_x, hero.grid_y)]
    # Sempre 1 slime, 1 golem, 1 specter
    x1, y1 = get_random_free_cell(used_cells)
    enemies.append(Enemy(x1, y1, "slime"))  # Adiciona um slime em uma célula livre
    used_cells.append((x1, y1))
    x2, y2 = get_random_free_cell(used_cells)
    enemies.append(Enemy(x2, y2, "golem"))  # Adiciona um golem em uma célula livre
    used_cells.append((x2, y2))
    x3, y3 = get_random_free_cell(used_cells)
    enemies.append(Enemy(x3, y3, "specter"))  # Adiciona um specter em uma célula livre
    used_cells.append((x3, y3))
    # A cada fase, adicione mais inimigos variados
    enemy_types = ["slime", "golem", "specter"]

    # Para fases acima da 2, adiciona inimigos extras de tipos aleatórios
    for i in range(max(0, stage - 2)):
        x, y = get_random_free_cell(used_cells)
        enemy_type = random.choice(enemy_types)  # Escolhe aleatoriamente o tipo do inimigo extra
        enemies.append(Enemy(x, y, enemy_type))  # Adiciona o inimigo extra
        used_cells.append((x, y))  # Marca a célula como ocupada

def process_enemy_turn():
    global turn, enemy_turn_index
    # Remove inimigos mortos antes de processar o turno
    remove_dead_enemies()
    # Se não houver mais inimigos, volta para o jogador
    if len(enemies) == 0:
        turn = PLAYER_TURN
        enemy_turn_index = 0
        start_player_turn()
        return
    # Verifica se ainda há inimigos para agir nesta rodada
    if enemy_turn_index < len(enemies):
        enemy = enemies[enemy_turn_index]
        # Só age se não estiver morto
        if enemy.health > 0:
            enemy.ai_move()  # Executa a ação do inimigo (mover ou atacar)
        enemy_turn_index += 1
        if enemy_turn_index < len(enemies):
            turn = ENEMY_TURN  # Próximo inimigo age
        else:
            turn = PLAYER_TURN  # Volta para o jogador
            enemy_turn_index = 0
            start_player_turn()  # Inicia o turno do jogador (atualiza bombas, etc)
    else:
        # Se não houver mais inimigos para agir, volta para o jogador
        turn = PLAYER_TURN
        enemy_turn_index = 0
        start_player_turn()  # Inicia o turno

def start_stage():
    global hero, dungeon, enemies, bombs, game_state, turn, enemy_turn_index, game_over_sound_played
    game_over_sound_played = False
    # Toca o som de preparação ao iniciar a fase
    if sound_enabled:
        try:
            play_sound('prepare_yourself')
        except:
            pass
    hero.grid_x = 1
    hero.grid_y = 1
    hero.pixel_x = GRID_SIZE
    hero.pixel_y = GRID_SIZE
    hero.target_x = hero.pixel_x
    hero.target_y = hero.pixel_y
    hero.moving = False
    hero.health = hero.max_health
    # Reset da animação do herói para idle
    hero.current_animation = hero.idle_animation
    hero.current_animation.current_frame = 0
    hero.current_animation.time_since_last_frame = 0
    dungeon.generate_dungeon()
    bombs.clear()
    spawn_enemies()
    turn = PLAYER_TURN
    enemy_turn_index = 0
    game_state = PLAYING

def update(dt):
    global game_state, music_enabled, sound_enabled, last_time, mouse_pos, turn, feedback_message, feedback_timer, enemy_turn_index
    global next_stage_timer, game_over_sound_played, enemy_turn_timer, victory_anim_timer

    if feedback_message:
        feedback_timer -= dt
        if feedback_timer <= 0:
            feedback_message = ""

    if game_state == MENU:
        start_button.update(mouse_pos)
        music_button.update(mouse_pos)
        exit_button.update(mouse_pos)
        music_text = f"Música: {'ON' if music_enabled else 'OFF'}"
        music_button.text = music_text

    elif game_state == PLAYING:
        hero.update(dt)
        # Atualizar bombas (apenas explosão visual)
        for bomb in bombs:
            bomb.update(dt)
        bombs[:] = [b for b in bombs if not (b.exploded and b.explosion_timer <= 0)]

        # Sistema de rodadas dos inimigos com delay
        if turn == ENEMY_TURN and enemy_turn_index < len(enemies):
            enemy_turn_timer += dt
            if enemy_turn_timer >= ENEMY_TURN_DELAY:
                enemy = enemies[enemy_turn_index]
                enemy.update(dt)
                if not enemy.moving:
                    enemy.ai_move()
                    enemy.move_timer = 0
                    process_enemy_turn()
                enemy_turn_timer = 0  # reseta o timer após cada ação de inimigo

    # Atualizar animação de TODOS os inimigos SEMPRE (mas NÃO mover todos!)
    for idx, enemy in enumerate(enemies):
        # Atualiza movimento do inimigo se estiver se movendo
        if enemy.moving:
            enemy.update(dt)
        # Atualiza animação do inimigo (mesmo parado)
        enemy.current_animation.update(dt)
        if enemy.actor:
            frame_name = enemy.current_animation.get_current_frame()
            enemy.actor.image = frame_name
            enemy.actor.pos = (enemy.pixel_x + GRID_SIZE // 2, enemy.pixel_y + GRID_SIZE // 2)

    # Verificar colisão com inimigos
    for enemy in enemies:
        if hero.grid_x == enemy.grid_x and hero.grid_y == enemy.grid_y:
            hero.health -= 0.9
            if hero.health <= 0:
                game_state = GAME_OVER
                if sound_enabled and not game_over_sound_played:
                    play_sound('you_lose')
                    game_over_sound_played = True

    # Verificar dano de bomba ao herói
    for bomb in bombs:
        # Verifica se a bomba já explodiu e se a explosão ainda está visível
        if bomb.exploded and bomb.explosion_timer > 0:
            explosion_cells = [(bomb.grid_x, bomb.grid_y)]  # Célula central da explosão
            # Adiciona todas as células atingidas pela explosão nos eixos
            for d in range(1, bomb.radius + 1):
                explosion_cells.append((bomb.grid_x + d, bomb.grid_y))      # Direita
                explosion_cells.append((bomb.grid_x - d, bomb.grid_y))      # Esquerda
                explosion_cells.append((bomb.grid_x, bomb.grid_y + d))      # Baixo
                explosion_cells.append((bomb.grid_x, bomb.grid_y - d))      # Cima
            # Se o herói estiver em alguma dessas células, ele recebe dano
            if (hero.grid_x, hero.grid_y) in explosion_cells:
                hero.health -= 10
                # Se a vida do herói chegar a zero ou menos, o jogo termina
                if hero.health <= 0:
                    game_state = GAME_OVER
                    if sound_enabled and not game_over_sound_played:
                        play_sound('you_lose')
                        game_over_sound_played = True

    # Checar vitória ao chegar na porta de saída
    if hero.grid_x == door_out_x and hero.grid_y == door_out_y and game_state == PLAYING:
        global stage, next_stage_timer
        stage += 1
        game_state = NEXT_STAGE
        next_stage_timer = 4  # segundos na tela de parabéns
        if sound_enabled:
            try:
                play_sound('you_win')
            except:
                pass

    if game_state == NEXT_STAGE:
        next_stage_timer -= dt
        victory_anim_timer += dt
        # Atualiza animação de vitória do herói
        hero.victory_animation.update(dt)
        if next_stage_timer <= 0:
            start_stage()

def draw():
    screen.clear() # type: ignore
    
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    elif game_state == VICTORY:
        draw_victory()
    elif game_state == NEXT_STAGE:
        draw_next_stage()

def draw_menu():
    # Desenha o background centralizado (ou ajustado ao tamanho da tela)
    screen.blit(images.background, (0, 0))  # type: ignore

    # Título do jogo
    title_y = HEIGHT // 4
    screen.draw.text(TITLE, center=(WIDTH//2, title_y), fontsize=48, color=WHITE) # type: ignore

    # Subtítulo
    subtitle_y = title_y + 55
    screen.draw.text("O Despertar do Arcano: Sobreviva ao Labirinto", center=(WIDTH//2, subtitle_y), fontsize=22, color=WHITE) # type: ignore

    # Espaçamento entre subtítulo e botões
    buttons_start_y = subtitle_y + 60

    # Desenhar botões centralizados verticalmente
    btn_height = 50
    btn_spacing = 20
    start_button.rect.centery = buttons_start_y
    music_button.rect.centery = buttons_start_y + btn_height + btn_spacing
    exit_button.rect.centery = buttons_start_y + 2 * (btn_height + btn_spacing)

    start_button.draw(screen) # type: ignore
    music_button.draw(screen) # type: ignore
    exit_button.draw(screen) # type: ignore

    # Instruções (mais próximas do rodapé)
    instr_y = HEIGHT - 70
    screen.draw.text("Use LMB para mover e RMB para posicionar a bomba", center=(WIDTH//2, instr_y), fontsize=16, color=WHITE) # type: ignore
    screen.draw.text("Explore o labirinto, derrote os inimigos e encontre a saída", center=(WIDTH//2, instr_y + 25), fontsize=16, color=WHITE) # type: ignore

def draw_game():
    screen.fill((20, 20, 20))  # Cor de fundo da masmorra # type: ignore
    
    # Desenhar masmorra
    dungeon.draw(screen) # type: ignore
    
    # Desenhar portas
    door_in_rect = pygame.Rect(door_in_x * GRID_SIZE, door_in_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    door_out_rect = pygame.Rect(door_out_x * GRID_SIZE, door_out_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    screen.draw.filled_rect(door_in_rect, (0, 150, 255))  # Porta de entrada: azul # type: ignore
    screen.draw.filled_rect(door_out_rect, (255, 215, 0)) # Porta de saída: dourada # type: ignore
    screen.draw.rect(door_in_rect, WHITE) # type: ignore
    screen.draw.rect(door_out_rect, WHITE) # type: ignore

    # Destaque visual no grid sob o mouse (apenas no turno do jogador)
    if game_state == PLAYING and turn == PLAYER_TURN:
        grid_x = mouse_pos[0] // GRID_SIZE
        grid_y = mouse_pos[1] // GRID_SIZE
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            is_valid = (
                hero.can_move_to(grid_x, grid_y)
                and is_adjacent(hero.grid_x, hero.grid_y, grid_x, grid_y)
                and not hero.moving
            )
            border_color = (0, 255, 0) if is_valid else (255, 0, 0)
            rect = pygame.Rect(grid_x * GRID_SIZE, grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if is_valid:
                screen.draw.filled_rect(rect, (0, 255, 0))  # Verde opaco para célula válida # type: ignore
            else:
                screen.draw.filled_rect(rect, (255, 0, 0))  # Vermelho opaco para célula inválida # type: ignore
            screen.draw.rect(rect, border_color) # type: ignore

    # Desenhar inimigos
    for enemy in enemies:
        enemy.draw(screen) # type: ignore
    
    # Desenhar herói
    hero.draw(screen) # type: ignore
    
    # Desenhar bombas
    for bomb in bombs:
        bomb.draw(screen) # type: ignore
    
    # --- HUD refinado ---
    hud_width = 220
    hud_height = 80
    hud_x = WIDTH - hud_width - 16
    hud_y = 16

    # Painel de fundo
    hud_rect = pygame.Rect(hud_x, hud_y, hud_width, hud_height)
    screen.draw.filled_rect(hud_rect, (30, 30, 30))  # Fundo escuro # type: ignore
    screen.draw.rect(hud_rect, WHITE)  # Borda branca   # type: ignore

    # Barra de vida com fundo e borda
    bar_x = hud_x + 16
    bar_y = hud_y + 16
    bar_width = 160
    bar_height = 18
    # Fundo da barra
    bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    screen.draw.filled_rect(bar_bg_rect, (60, 60, 60))  # Fundo cinza escuro # type: ignore
    # Barra de vida
    health_ratio = hero.health / hero.max_health
    bar_fg_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_ratio), bar_height)
    screen.draw.filled_rect(bar_fg_rect, (0, 200, 0))   # Barra de vida verde # type: ignore
    # Borda da barra
    screen.draw.rect(bar_bg_rect, WHITE)    # type: ignore
    # Texto da vida
    screen.draw.text(f"{int(hero.health)}/{int(hero.max_health)}", center=(bar_x + bar_width // 2, bar_y + bar_height // 2 + 1), fontsize=18, color=WHITE)  # type: ignore

    # Inimigos restantes
    screen.draw.text(f"Inimigos: {len(enemies)}", (hud_x + 16, hud_y + 46), fontsize=20, color=(255, 80, 80))   # type: ignore
    # Fase atual
    screen.draw.text(f"Fase: {stage}", (hud_x + 120, hud_y + 46), fontsize=20, color=(255, 215, 0)) # type: ignore

    # Dica de tecla
    screen.draw.text("ESC: Menu", (hud_x + 120, hud_y + 68), fontsize=14, color=(180, 180, 180))    # type: ignore

    # --- Mensagem de feedback ---
    if feedback_message:
        box_width = 420
        box_height = 40
        box_x = (WIDTH - box_width) // 2
        box_y = 8  # Bem no topo, acima das paredes do mapa
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        screen.draw.filled_rect(box_rect, RED)  # Fundo vermelho para destaque # type: ignore
        screen.draw.text(   # type: ignore
            feedback_message,
            center=(box_x + box_width // 2, box_y + box_height // 2),
            fontsize=20,
            color=WHITE
        )

def draw_game_over():
    # Preenche a tela com preto
    screen.fill(BLACK) # type: ignore
    # Escreve "GAME OVER" centralizado na tela, em vermelho
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=48, color=RED) # type: ignore
    # Escreve instrução para voltar ao menu, logo abaixo, em branco
    screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=16, color=WHITE) # type: ignore

def draw_victory():
    # Preenche a tela com um tom de azul escuro
    screen.fill((30, 30, 60))  # type: ignore
    # Desenha o herói (com animação de vitória)
    hero.draw(screen) # type: ignore
    # Escreve "VOCÊ VENCEU!" centralizado, em verde
    screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=48, color=GREEN) # type: ignore
    # Escreve instrução para voltar ao menu, logo abaixo, em branco
    screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=24, color=WHITE) # type: ignore

def draw_next_stage():
    # Preenche a tela com um tom de azul escuro
    screen.fill((30, 30, 60)) # type: ignore

    # Troca temporariamente a animação do herói para vitória
    old_animation = hero.current_animation
    hero.current_animation = hero.victory_animation
    hero.draw(screen)   # type: ignore
    hero.current_animation = old_animation  # Restaura a animação anterior

    # Escreve "Parabéns!" centralizado, em verde
    screen.draw.text("Parabéns!", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=60, color=GREEN) # type: ignore
    # Mensagem de chegada à porta de saída
    screen.draw.text(f"Você chegou à porta de saída!", center=(WIDTH//2, HEIGHT//2 + 10), fontsize=32, color=WHITE) # type: ignore
    # Mensagem informando que a próxima fase começará em instantes
    screen.draw.text(f"Fase {stage} começará em instantes...", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=28, color=WHITE) # type: ignore

def on_mouse_down(pos, button):
    global game_state, music_enabled, sound_enabled, turn, feedback_message, feedback_timer

    # Clique direito para plantar bomba durante o jogo
    if game_state == PLAYING and turn == PLAYER_TURN and button == mouse.RIGHT: # type: ignore
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        if grid_x == hero.grid_x and grid_y == hero.grid_y and not is_bomb_at(hero.grid_x, hero.grid_y):
            bombs.append(Bomb(hero.grid_x, hero.grid_y))
            return  # Não processa movimento nesse clique

    # Se estiver no menu principal
    if game_state == MENU:
        # Se clicou no botão de começar, inicia o jogo
        if start_button.is_clicked(pos):
            start_stage()

        # Se clicou no botão de música, alterna entre ligar/desligar música
        elif music_button.is_clicked(pos):
            music_enabled = not music_enabled
            if music_enabled:
                try:
                    music.play('background_music')
                except:
                    pass
            else:
                try:
                    music.stop()
                except:
                    pass
        # Se clicou no botão de sair, fecha o jogo
        elif exit_button.is_clicked(pos):
            exit()
            
    elif game_state == PLAYING and turn == PLAYER_TURN:
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        # Só permite mover para célula adjacente e livre
        if hero.can_move_to(grid_x, grid_y) and is_adjacent(hero.grid_x, hero.grid_y, grid_x, grid_y) and not hero.moving:
            hero.move(grid_x - hero.grid_x, grid_y - hero.grid_y)
            feedback_message = ""  # Limpa mensagem se movimento for válido
            if len(enemies) > 0:
                turn = ENEMY_TURN
                enemy_turn_index = 0   # Começa a rodada dos inimigos
            else:
                start_player_turn()
                turn = PLAYER_TURN  # Mantém o turno do jogador se não houver inimigos
        else:
            feedback_message = "Só é possível mover para uma célula adjacente e livre!"
            feedback_timer = 2.5  # segundos

def on_key_down(key):
    global game_state, stage, feedback_message, feedback_timer, game_over_sound_played
    if key == key.ESCAPE:
        if game_state == PLAYING or game_state == GAME_OVER or game_state == VICTORY:
            game_state = MENU
            # Resetar variáveis do jogo ao voltar ao menu
            bombs.clear()
            enemies.clear()
            hero.moving = False
            hero.current_animation = hero.idle_animation
            hero.current_animation.current_frame = 0
            hero.current_animation.time_since_last_frame = 0
            feedback_message = ""
            feedback_timer = 0

def play_sound(sound_name):
    """Toca um som se o áudio estiver habilitado, sem travar o jogo se der erro."""
    if sound_enabled:
        try:
            getattr(sounds, sound_name).play()
        except Exception as e:
            print(f"Erro ao tocar som '{sound_name}': {e}")

# Inicializar música de fundo
def init_music():
    global music_enabled
    if music_enabled:
        try:
            music.set_volume(0.2)  # Define o volume para 80%
            music.play('background_music')
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

# Inicializar música automaticamente
init_music()

pgzrun.go()

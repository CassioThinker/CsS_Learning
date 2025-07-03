import pgzrun
import pygame
import random
from pgzero.builtins import sounds, music, images, mouse

from src.settings import *
from src.hero import Hero
from src.dungeon import Dungeon
from src.button import Button
from src.enemy import Enemy
from src.bomb import Bomb
from src.utils import is_bomb_at, is_adjacent, remove_dead_enemies, get_random_free_cell

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
turn = PLAYER_TURN
enemy_turn_index = 0  # Índice do inimigo que está jogando
enemy_turn_timer = 0

# Mensagem de feedback para o jogador
feedback_message = ""
feedback_timer = 0

# Objetos do jogo
dungeon = Dungeon()
hero = Hero(1, 1, dungeon)
enemies = []
bombs = []
last_time = 0

# Botões do menu
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Começar o Jogo", GREEN)
music_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "Música: ON", BLUE)
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "Sair", RED)

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def spawn_enemies():
    global enemies
    enemies = []
    used_cells = [(hero.grid_x, hero.grid_y)]
    # Sempre 1 slime, 1 golem, 1 specter
    x1, y1 = get_random_free_cell(dungeon, used_cells)
    enemies.append(Enemy(x1, y1, "slime", dungeon, hero))
    used_cells.append((x1, y1))
    x2, y2 = get_random_free_cell(dungeon, used_cells)
    enemies.append(Enemy(x2, y2, "golem", dungeon, hero))
    used_cells.append((x2, y2))
    x3, y3 = get_random_free_cell(dungeon, used_cells)
    enemies.append(Enemy(x3, y3, "specter", dungeon, hero))
    used_cells.append((x3, y3))
    # A cada fase, adicione mais inimigos variados
    enemy_types = ["slime", "golem", "specter"]

    # Para fases acima da 2, adiciona inimigos extras de tipos aleatórios
    for i in range(max(0, stage - 2)):
        x, y = get_random_free_cell(dungeon, used_cells)
        enemy_type = random.choice(enemy_types)
        enemies.append(Enemy(x, y, enemy_type, dungeon, hero))
        used_cells.append((x, y))

def start_stage():
    global hero, dungeon, enemies, bombs, game_state, turn, enemy_turn_index, game_over_sound_played
    game_over_sound_played = False
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
        for bomb in bombs:
            bomb.update(dt)
        bombs[:] = [b for b in bombs if not (b.exploded and b.explosion_timer <= 0)]

        if turn == ENEMY_TURN and enemy_turn_index < len(enemies) and not hero.moving:
            enemy_turn_timer += dt
            if enemy_turn_timer >= ENEMY_TURN_DELAY:
                enemy = enemies[enemy_turn_index]
                enemy.update(dt)
                if not enemy.moving:
                    enemy.ai_move()
                    enemy.move_timer = 0
                    process_enemy_turn()
                enemy_turn_timer = 0

    for idx, enemy in enumerate(enemies):
        if enemy.moving:
            enemy.update(dt)
        enemy.current_animation.update(dt)
        if enemy.actor:
            frame_name = enemy.current_animation.get_current_frame()
            enemy.actor.image = frame_name
            enemy.actor.pos = (enemy.pixel_x + GRID_SIZE // 2, enemy.pixel_y + GRID_SIZE // 2)

    for enemy in enemies:
        if hero.grid_x == enemy.grid_x and hero.grid_y == enemy.grid_y:
            hero.health -= 0.9
            if hero.health <= 0:
                game_state = GAME_OVER
                if sound_enabled and not game_over_sound_played:
                    play_sound('you_lose')
                    game_over_sound_played = True

    for bomb in bombs:
        if bomb.exploded and bomb.explosion_timer > 0:
            explosion_cells = [(bomb.grid_x, bomb.grid_y)]
            for d in range(1, bomb.radius + 1):
                explosion_cells.append((bomb.grid_x + d, bomb.grid_y))
                explosion_cells.append((bomb.grid_x - d, bomb.grid_y))
                explosion_cells.append((bomb.grid_x, bomb.grid_y + d))
                explosion_cells.append((bomb.grid_x, bomb.grid_y - d))
            if (hero.grid_x, hero.grid_y) in explosion_cells:
                hero.health -= 10
                if hero.health <= 0:
                    game_state = GAME_OVER
                    if sound_enabled and not game_over_sound_played:
                        play_sound('you_lose')
                        game_over_sound_played = True

    if hero.grid_x == door_out_x and hero.grid_y == door_out_y and game_state == PLAYING:
        global stage, next_stage_timer
        stage += 1
        game_state = NEXT_STAGE
        next_stage_timer = 4
        if sound_enabled:
            try:
                play_sound('you_win')
            except:
                pass

    if game_state == NEXT_STAGE:
        next_stage_timer -= dt
        victory_anim_timer += dt
        hero.victory_animation.update(dt)
        if next_stage_timer <= 0:
            start_stage()

def draw():
    screen.clear()
    
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
    screen.blit(images.background, (0, 0))
    title_y = HEIGHT // 4
    screen.draw.text(TITLE, center=(WIDTH//2, title_y), fontsize=48, color=WHITE)
    subtitle_y = title_y + 55
    screen.draw.text("O Despertar do Arcano: Sobreviva ao Labirinto", center=(WIDTH//2, subtitle_y), fontsize=22, color=WHITE)
    buttons_start_y = subtitle_y + 60
    btn_height = 50
    btn_spacing = 20
    start_button.rect.centery = buttons_start_y
    music_button.rect.centery = buttons_start_y + btn_height + btn_spacing
    exit_button.rect.centery = buttons_start_y + 2 * (btn_height + btn_spacing)
    start_button.draw(screen)
    music_button.draw(screen)
    exit_button.draw(screen)
    instr_y = HEIGHT - 70
    screen.draw.text("Use LMB para mover e RMB para posicionar a bomba", center=(WIDTH//2, instr_y), fontsize=16, color=WHITE)
    screen.draw.text("Explore o labirinto, derrote os inimigos e encontre a saída", center=(WIDTH//2, instr_y + 25), fontsize=16, color=WHITE)

def draw_game():
    screen.fill((20, 20, 20))
    dungeon.draw(screen)
    door_in_rect = pygame.Rect(door_in_x * GRID_SIZE, door_in_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    door_out_rect = pygame.Rect(door_out_x * GRID_SIZE, door_out_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    screen.draw.filled_rect(door_in_rect, (0, 150, 255))
    screen.draw.filled_rect(door_out_rect, (255, 215, 0))
    screen.draw.rect(door_in_rect, WHITE)
    screen.draw.rect(door_out_rect, WHITE)

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
                screen.draw.filled_rect(rect, (0, 255, 0, 128))
            else:
                screen.draw.filled_rect(rect, (255, 0, 0, 128))
            screen.draw.rect(rect, border_color)

    for enemy in enemies:
        enemy.draw(screen)
    
    hero.draw(screen)
    
    for bomb in bombs:
        bomb.draw(screen)
    
    hud_width = 430  # Largura ajustada para as 3 informações
    hud_height = GRID_SIZE # Altura igual ao tamanho do bloco
    hud_x = (WIDTH - hud_width) // 2
    hud_y = 0 # Posiciona no topo da tela
    hud_rect = pygame.Rect(hud_x, hud_y, hud_width, hud_height)
    screen.draw.filled_rect(hud_rect, (30, 30, 30))
    screen.draw.rect(hud_rect, WHITE)

    # Posicionamento das informações lado a lado
    text_y = hud_y + hud_height // 2 - 10 # Centraliza verticalmente o texto
    screen.draw.text(f"Inimigos: {len(enemies)}", (hud_x + 20, text_y), fontsize=20, color=(255, 80, 80))
    screen.draw.text(f"Fase: {stage}", (hud_x + 200, text_y), fontsize=20, color=(255, 215, 0))
    screen.draw.text("ESC: Menu", (hud_x + 350, text_y + 3), fontsize=14, color=(180, 180, 180))

    if feedback_message:
        box_width = 420
        box_height = 40
        box_x = (WIDTH - box_width) // 2
        box_y = 8
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        screen.draw.filled_rect(box_rect, RED)
        screen.draw.text(
            feedback_message,
            center=(box_x + box_width // 2, box_y + box_height // 2),
            fontsize=20,
            color=WHITE
        )

def draw_game_over():
    screen.fill(BLACK)
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=48, color=RED)
    screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=16, color=WHITE)

def draw_victory():
    screen.fill((30, 30, 60))
    hero.draw(screen)
    screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=48, color=GREEN)
    screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=24, color=WHITE)

def draw_next_stage():
    screen.fill((30, 30, 60))
    old_animation = hero.current_animation
    hero.current_animation = hero.victory_animation
    hero.draw(screen)
    hero.current_animation = old_animation
    screen.draw.text("Parabéns!", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=60, color=GREEN)
    screen.draw.text(f"Você chegou à porta de saída!", center=(WIDTH//2, HEIGHT//2 + 10), fontsize=32, color=WHITE)
    screen.draw.text(f"Fase {stage} começará em instantes...", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=28, color=WHITE)

def on_mouse_down(pos, button):
    global game_state, music_enabled, sound_enabled, turn, feedback_message, feedback_timer

    if game_state == PLAYING and turn == PLAYER_TURN and button == mouse.RIGHT:
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        if grid_x == hero.grid_x and grid_y == hero.grid_y and not is_bomb_at(hero.grid_x, hero.grid_y, bombs):
            bombs.append(Bomb(hero.grid_x, hero.grid_y))
            return

    if game_state == MENU:
        if start_button.is_clicked(pos):
            start_stage()
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
        elif exit_button.is_clicked(pos):
            exit()
            
    elif game_state == PLAYING and turn == PLAYER_TURN:
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        if hero.can_move_to(grid_x, grid_y) and is_adjacent(hero.grid_x, hero.grid_y, grid_x, grid_y) and not hero.moving:
            hero.move(grid_x - hero.grid_x, grid_y - hero.grid_y, lambda x, y: is_bomb_at(x, y, bombs))
            feedback_message = ""
            if len(enemies) > 0:
                turn = ENEMY_TURN
                enemy_turn_index = 0
            else:
                start_player_turn()
                turn = PLAYER_TURN
        else:
            feedback_message = "Só é possível mover para uma célula adjacente e livre!"
            feedback_timer = 2.5

def on_key_down(key):
    global game_state, stage, feedback_message, feedback_timer, game_over_sound_played
    if key == key.ESCAPE:
        if game_state == PLAYING or game_state == GAME_OVER or game_state == VICTORY:
            game_state = MENU
            bombs.clear()
            enemies.clear()
            hero.moving = False
            hero.current_animation = hero.idle_animation
            hero.current_animation.current_frame = 0
            hero.current_animation.time_since_last_frame = 0
            feedback_message = ""
            feedback_timer = 0

def play_sound(sound_name):
    if sound_enabled:
        try:
            getattr(sounds, sound_name).play()
        except Exception as e:
            print(f"Erro ao tocar som '{sound_name}': {e}")

def init_music():
    global music_enabled
    if music_enabled:
        try:
            music.set_volume(0.2)
            music.play('background_music')
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

def process_enemy_turn():
    global turn, enemy_turn_index, enemies
    remove_dead_enemies(enemies)
    if len(enemies) == 0:
        turn = PLAYER_TURN
        enemy_turn_index = 0
        start_player_turn()
        return
    if enemy_turn_index < len(enemies):
        enemy = enemies[enemy_turn_index]
        if enemy.health > 0:
            enemy.ai_move()
        enemy_turn_index += 1
        if enemy_turn_index < len(enemies):
            turn = ENEMY_TURN
        else:
            turn = PLAYER_TURN
            enemy_turn_index = 0
            start_player_turn()
    else:
        turn = PLAYER_TURN
        enemy_turn_index = 0
        start_player_turn()

def start_player_turn():
    global enemy_turn_timer, enemies
    for bomb in bombs:
        bomb.tick_round(dungeon, enemies, play_sound)
    remove_dead_enemies(enemies)
    enemy_turn_timer = 0

init_music()

pgzrun.go()

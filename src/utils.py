import random
from src.settings import GRID_WIDTH, GRID_HEIGHT

def is_bomb_at(x, y, bombs):
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

def remove_dead_enemies(enemies):
    """Remove todos os inimigos com vida menor ou igual a zero da lista, modificando a lista original."""
    i = 0
    while i < len(enemies):
        if enemies[i].health <= 0:
            enemies.pop(i)
        else:
            i += 1

def get_random_free_cell(dungeon, exclude_cells=None):
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
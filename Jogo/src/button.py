import pygame
from pgzero.builtins import sounds
from src.settings import BLACK

class Button:
    def __init__(self, x, y, width, height, text, color):
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

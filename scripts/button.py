from scripts.text import text, textindex
import pygame

class textbox():
    def __init__(self, game, surf, coords, text, type):
        self.game = game
        self.surf = surf
        self.coords = coords
        self.msg = text
        textl = self.textlength(game, text)
        self.size = (textl+4, 16)
        self.textcoords = (self.coords[0]+2, self.coords[1]+1)

    def textlength(self, game, text):
        width = 0
        for word in text:
            width += game.assets["alphabet"][textindex.index(word)].get_width() + 2
        return width

    def update(self, game, surf):
        rect = pygame.Rect(self.coords, self.size)
        colour = (255, 0, 0)
        if rect.collidepoint(game.mx, game.my):
            colour = (0, 255, 0) 
        pygame.draw.rect(surf, colour, rect)
        text(game, surf, self.textcoords, self.msg)
        pygame.display.update()
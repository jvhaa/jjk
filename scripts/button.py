from scripts.text import text, textindex
import pygame

class textbox():
    def __init__(self, game, surf, coords, text, type):
        self.game = game
        self.surf = surf
        coords = coords
        self.msg = text
        textl = self.textlength(game, text)
        size = (textl+4, 16)
        self.textcoords = (coords[0]+2, coords[1]+1)
        self.rect = pygame.Rect(coords, size)
        self.type = type

    def textlength(self, game, text):
        width = 0
        for word in text:
            width += game.assets["alphabet"][textindex.index(word)].get_width() + 2
        return width

    def update(self, game, surf):
        colour = (255, 0, 0)
        if self.rect.collidepoint(game.mx, game.my):
            colour = (0, 255, 0) 
            if game.click == True:
                game.gamestate = self.type
                game.b()
        pygame.draw.rect(surf, colour, self.rect)
        text(game, surf, self.textcoords, self.msg)
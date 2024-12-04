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
        self.textcoords = (coords[0]+3, coords[1]+2)
        self.rect = pygame.Rect(coords, size)
        self.type = type

    def textlength(self, game, text):
        width = 0
        for word in text:
            width += game.assets["alphabet"][textindex.index(word)].get_width() + 2
        return width

    def update(self):
        colour = (255, 0, 0)
        if self.rect.collidepoint(self.game.mx, self.game.my):
            colour = (0, 255, 0) 
            if self.game.click == True:
                self.game.gamestate = self.type
                if self.type[:4] == "game" and len(self.type) > 4:
                    self.game.gamestate = "game"
                    self.game.load_map(int(self.type.split(" ")[1])-1)

                self.game.b()
        pygame.draw.rect(self.surf, colour, self.rect)
        text(self.game, self.surf, self.textcoords, self.msg)
import math

class Particle:
    def __init__(self, game, p_type, pos, vel=[0, 0], frame=0,flip = False):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.vel = list(vel)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = 0
    
    def update(self):
        kill = False
        if self.animation.done == True:
            kill = True
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.animation.update()

        return kill
        
    def render(self, surf, offset=(0,0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0]-offset[0]-img.get_width()//2, self.pos[1]-offset[1]-img.get_height()))
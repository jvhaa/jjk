import pygame, sys, random, math

from scripts.entity import Physics_Entity, player, grade4_0, grade3_0
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import TileMap
from scripts.stars import stars
from scripts.particle import Particle
from scripts.sparks import Spark

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('jjk')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.move = [False, False]

        self.assets = {
            "alphabet" : load_images("alphabet"),
            "startup" : load_image("background/startup.png"),
            "street" : load_images("street"),
            "background" : load_image("background/night.png"),
            "stars" : load_images("Stars"),
            "city_background" : load_images("city_background"),
            "spawner" : load_images("spawner"),
            "grade3_0/idle": Animation(load_images("grade3_0/idle"), 3),
            "grade3_0/aggro": Animation(load_images("grade3_0/aggro"), 3),
            "grade3_0/charge" : Animation(load_images("grade3_0/charge"), 3),
            "grade3_0/bullet": load_image("grade3_0/bullet.png"),
            "grade4_0/idle" : Animation(load_images("grade4_0/idle"), 3),
            "grade4_0/aggro" : Animation(load_images("grade4_0/aggro"), 3),
            'grade4_0/charge' : Animation(load_images("grade4_0/charge"), 3),
            "player/idle" : Animation(load_images("player/idle"), 3),
            "player/walk" : Animation(load_images("player/walk"), 10),
            "player/jump" : Animation(load_images("player/jump"), 1),
            "player/wall_slide": Animation(load_images("player/wall_slide"), 1),
            "player/punch_0" : Animation(load_images("player/punch1"), 5, False),
            "player/punch_1" : Animation(load_images("player/punch2"), 5, False),
            "player/punch_2" : Animation(load_images("player/punch3"), 5, False),
            "player/groundslam" : Animation(load_images("player/groundslam"), 5, False),
            "player/frontsmash" : Animation(load_images("player/frontsmash"), 5, False),
            "player/uppercut" : Animation(load_images("player/punch1"), 5, False),
            "player/divfist" : Animation(load_images("player/divfist"), 10, False),
            "player/focus" : Animation(load_images("player/focus"), 1, False),
            "particle/lights" : Animation(load_images("particle/lights"), 1,),
            "particle/black_flash": Animation(load_images("particle/black_flash"), 10, False)
        }

        self.player = player(self, (100, 0), (25, 37))
        self.Tilemap = TileMap(self)
        self.stars = stars(self.assets["stars"])
        self.hitbox = []
        
        self.scroll = [0, 0]
        self.load_map(0)
    
    def main_menu(self):
        while True:
            self.display.blit(self.assets["startup"], (0, 0))
            button = pygame.Rect(125, 125, 90, 50)
            mx, my = pygame.mouse.get_pos()
            mx /= 2
            my /= 2
            color = (255, 0, 0)
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
            if button.collidepoint((mx, my)):
                color = (0, 255, 0)
                if click:
                    self.run()
            pygame.draw.rect(self.display, color, button)
            pygame.display.update()
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.clock.tick(60)

    def run(self):
        while True:

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.light:
                if random.random()* 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random()*rect.width, rect.y + random.random()*rect.height)
                    self.particles.append(Particle(self, "lights", pos, (random.randint(-1, 1)/10, 0.1)))
            self.display.blit(self.assets["background"], (0, 0))
            self.stars.render(self.display, render_scroll)
            self.stars.update()

            for hitbox in self.hitbox.copy():
                self.hitbox[self.hitbox.index(hitbox)]["pos"] = (hitbox["pos"][0] + hitbox["vel"][0], hitbox["pos"][1] + hitbox["vel"][1])
                hit_rect = pygame.Rect(hitbox["pos"][0], hitbox["pos"][1], hitbox["size"][0], hitbox["size"][1])
                pygame.draw.rect(self.display, (255, 0, 0), pygame.Rect(hitbox["pos"][0]-render_scroll[0], hitbox["pos"][1]-render_scroll[1], hitbox["size"][0], hitbox["size"][1]))
                self.hitbox[self.hitbox.index(hitbox)]["timer"] -= 1
                if "image" in hitbox:
                    self.display.blit(self.assets[hitbox["image"]], (hitbox["pos"][0]-render_scroll[0], hitbox["pos"][1]-render_scroll[1]))
                if hitbox["timer"] <= 0: 
                    self.hitbox.remove(hitbox)
                if hitbox["type"] == "player": 
                    for enemies in self.enemies:
                        if hit_rect.colliderect(enemies.rect().copy()) and not enemies.stun:
                            enemies.hp -= hitbox["hploss"]
                            enemies.velocity = list(hitbox["speed"])
                            enemies.stun = hitbox["stun"]
                            color = (255, 255, 255)

                            if "texture" in hitbox:
                                color = hitbox["texture"][0]
                                part = hitbox["texture"][1]
                                self.particles.append(Particle(self, part, (hitbox["vel"][0]+render_scroll[0], hitbox["vel"][1]+render_scroll[1]+hitbox["size"][1]+50), (0,0), 0))

                            for i in range(4):
                                if hitbox["vel"][0] > 0:
                                    self.sparks.append(Spark([enemies.rect().x, enemies.rect().centery], (random.random()*0.6 - 1)*math.pi, 3, color))
                                if hitbox["vel"][0] < 0:
                                    self.sparks.append(Spark([enemies.rect().x+enemies.rect().width, enemies.rect().centery], (-0.5 + random.random()*0.6)*math.pi, 3, color))
                else:
                    if hit_rect.colliderect(self.player.rect().copy()) and abs(self.player.dashing) < 180:
                        self.player.hp -= hitbox["hploss"]
                        if abs(hitbox["speed"][0]) > 1:
                            self.player.velocity[0] = hitbox["speed"][0]
                            print(self.player.velocity)
                        if abs(hitbox["speed"][1]) > 1:
                            self.player.velocity[1] = hitbox["speed"][1]
                        print(self.player.velocity)
                        self.hitbox.remove(hitbox)
                        for i in range(4):
                            if hitbox["vel"][0] > 0:
                                self.sparks.append(Spark([self.player.rect().x, self.player.rect().centery], (random.random()*0.6 - 1)*math.pi, 3))
                            if hitbox["vel"][0] < 0:
                                self.sparks.append(Spark([self.player.rect().x+self.player.rect().width, self.player.rect().centery], (-0.5 + random.random()*0.6)*math.pi, 3))


            for enemy in self.enemies.copy():
                enemy.update(self.Tilemap)
                enemy.render(self.display, render_scroll)
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    for i in range(8):
                        self.sparks.append(Spark(enemies.rect().center, random.random()-0.5+math.pi, 4))

            self.player.update(self.Tilemap, ((self.move[1]-self.move[0]), 0))
            self.player.render(self.display, render_scroll)
            if self.player.hp <= 0:
                sys.exit()
                pygame.quit()

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, render_scroll)
                if kill == True:
                    self.sparks.remove(spark)

            for particle in self.particles.copy():
                kill = particle.update()     
                particle.render(self.display, render_scroll)
                if kill == True:
                    self.particles.remove(particle)

            self.Tilemap.render(self.display, render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.move[0] = True
                    if event.key == pygame.K_d:
                        self.move[1] = True
                    if event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_q:
                        self.player.dash()
                    if event.key == pygame.K_p:
                        self.player.punch()
                    if event.key == pygame.K_o:
                        self.player.cursed_technique()
                    if event.key == pygame.K_f:
                        self.player.blocking = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.move[0] = False
                    if event.key == pygame.K_d:
                        self.move[1] = False
                    if event.key == pygame.K_f:
                        self.player.blocking = False
            pygame.display.update()
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.clock.tick(60)
            
    def load_map(self, map_id):
        self.Tilemap.load("maps/" + str(map_id) + ".json")

        self.enemies = []
        self.light = []
        self.particles = []
        self.sparks = []
    
        for street_light in self.Tilemap.extract([("city_background", 0)], True):
            self.light.append(pygame.Rect(street_light['pos'][0], street_light['pos'][1]+10, 10, 10))
        
        for spawner in self.Tilemap.extract([("spawner", 0), ("spawner", 1), ("spawner", 2)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
            elif spawner["variant"] == 1:
                self.enemies.append(grade4_0(self, spawner['pos'], (20, 20)))
            elif spawner["variant"] == 2:
                self.enemies.append(grade3_0(self, spawner["pos"], (20, 20)))

Game().main_menu()
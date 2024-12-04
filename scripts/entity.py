import pygame
import random

class Physics_Entity:
    def __init__(self, game, e_type, pos, size):
        self.iframes = 0
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.stun = 0

        self.action = ""
        self.anim_offset = [0, 0]
        self.flip = False
        self.animation = self.game.assets[self.type + "/" + "idle"].copy()
        self.last_movement = [0, 0]
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement = (0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.pos = [self.pos[0]+self.anim_offset[0], self.pos[1]+self.anim_offset[1]]

        self.velocity[1] = min(5, self.velocity[1]+0.1)
        self.iframes = max(self.iframes-1, 0)
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0]-0.1)
        if self.velocity[0] < 0:
            self.velocity[0] = min(0, self.velocity[0] +0.1)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                    self.velocity[0] = 0
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                    self.velocity[0] = 0
                self.pos[0] = entity_rect.x
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        self.last_movement = movement

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        self.animation.update()
    
    def render(self, surf, scroll=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0]-scroll[0]+self.anim_offset[0], self.pos[1]-scroll[1]+self.anim_offset[1]))

class enemy(Physics_Entity):
    def __init__(self, game, pos, size, type):
        super().__init__(game, type, pos, size)
        self.walking = 0
        self.attack = 0
        self.hitboxs = set()

    def attack4_0(self):
        self.velocity[1] = -2
        self.velocity[0] = random.randint(3, 5)
        if self.flip:
            self.velocity[0] *= -1
        hitbox = {"pos": (self.pos[0], self.pos[1]), "size": self.size, "speed": (self.velocity[0]*0.6, 0), "type": "enemy", "hploss": 5, "timer": 60, "stun": 5, "iframes": 20, "follow": self}
        self.game.hitbox.append(hitbox)
    
    def attack3_0(self):
        xdiff = (self.game.player.pos[0]-self.pos[0]+self.game.player.size[0]/2)
        ydiff = (self.game.player.pos[1]-self.pos[1]+self.game.player.size[1]/2)
        hyp = (xdiff**2 + ydiff**2) ** 0.5
        speed = (xdiff / hyp*2, ydiff / hyp*2)
        hitbox = {"pos": (self.pos[0], self.pos[1]), "vel": speed, "size": (5,5), "speed" : (speed[0]*1, speed[1]*1), "type": "enemy", "hploss": 2, "timer": 1000, "stun" : 6, "image" : self.type + "/bullet", "iframes": 20}
        self.game.hitbox.append(hitbox)

    def update(self, tilemap):
        movement = (0,0)
        no_block_ahead = not tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1]+50))
        player_dist = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1]-self.pos[1])
        walled = self.collisions["left"] or self.collisions["right"]
        insight = ((self.flip and player_dist[0] < 0) or (not self.flip and player_dist[0] > 0)) and abs(player_dist[1]) < 70
        detected = abs(player_dist[0]) < self.detecting_range and insight
        attack = (abs(player_dist[0]) < self.attack_range) and insight
        self.stun = max(0, self.stun-1)
        if self.cd > self.attack:
            if detected:
                self.set_action("aggro")
            else:
                self.set_action('idle')
        if not self.stun:
            if attack:
                if not self.attack:
                    self.set_action("charge")
                    self.attack = self.cd + self.charge

                self.attack = max(0, self.attack-1)
                if self.attack == self.cd:
                    if self.type == "grade4_0":
                        self.attack4_0()
                    elif self.type == "grade3_0":
                        self.attack3_0()
            else:
                self.attack = 0
            if self.walking and not attack:
                if (no_block_ahead or walled or 0.995 < random.random()) and not detected:
                    self.flip = not self.flip
                elif self.velocity[0] == 0:
                    movement = (movement[0]-1 if self.flip else movement[0]+1,movement[1])
                self.walking = max(self.walking-1,0)
            elif random.random() < 0.1 and not attack: 
                self.walking = random.randint(30, 120)
        else:
            self.attack = 0
        super().update(tilemap, movement)

    
    def render(self, surf, scroll=(0,0)):
        super().render(surf, scroll)

class grade4_0(enemy):
    def __init__(self, game, pos, size):
        self.hp = 30
        self.detecting_range = 150
        self.attack_range = random.randint(100, 120)
        self.cd = 120
        self.charge = 27
        super().__init__(game, pos, size, "grade4_0")

class grade3_0(enemy):
    def __init__(self, game, pos, size):
        self.hp = 20
        self.detecting_range = 1000
        self.attack_range = random.randint(300, 700)
        self.cd = 100
        self.charge = 18
        super().__init__(game, pos, size, "grade3_0")

class player(Physics_Entity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.punching = 0
        self.punch_count = 0
        self.special = {"up": 0, "side": 0, "down":0, "neutral": 0}
        self.cursed_energy = 0
        self.hp = 100
        self.blockhp = 100

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            self.set_action("wall_slide")
            if self.collisions['right']:
                self.flip = True
            else:
                self.flip = False

        self.punching = max(self.punching -1, 0)

        if self.dashing > 0:
            self.dashing = max(self.dashing -1, 0)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing+1)
        if abs(self.dashing) > 190:
            self.velocity[0] = abs(self.dashing)/self.dashing*8
            if abs(self.dashing) == 191:
                self.velocity[0] *= 0.1
        for key in self.special:
            self.special[key] = max(0, self.special[key]-1)
        if pygame.key.get_pressed()[pygame.K_o] and movement == (0, 0):
            if not (pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_d]):
                self.set_action("focus")
                self.cursed_energy = min(self.cursed_energy + 20/60, 100)
                self.special["neutral"] = 1


        if not self.wall_slide and self.punching <= 5 and self.special["up"] <= 1190 and self.special["side"] <= 1490 and self.special["neutral"] == 0:
            if self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("walk")
            else:
                self.set_action("idle")
    
    def render(self, surf, scroll=(0, 0)):
        if self.iframes not in [1, 2, 3, 4,6,8, 10, 13, 16, 20]:
            super().render(surf, scroll)

    def block(self):
        self.game
        pass

    def jump(self):
        if self.wall_slide:
            if not self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.jumps = max(0, self.jumps-1)
                self.air_time = 5
                return True
            if self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.jumps = max(0, self.jumps-1)
                self.air_time = 5
                return True

        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def dash(self):
        self.iframes = 10
        if not self.dashing:
            if self.flip:
                self.dashing = -200
            else:
                self.dashing = 200
    
    def punch(self):
        alts = pygame.key.get_pressed()
        size = (5, 37)
        vel = (-2 if self.flip else 2, 0)
        stun = 60
        if self.flip:
            pos = [self.rect().centerx-10, self.pos[1]]
        else:
            pos = [self.rect().centerx +10, self.pos[1]]
        if not self.punching:
            self.punching = 15
            time = 10
            if self.punch_count < 3:
                self.set_action("punch_" + str(self.punch_count))
                power = [0.5 * self.punch_count+2 * (-1 if self.flip else 1), 0]
                hploss = self.punch_count + 2
            else:
                if alts[pygame.K_w]:
                    self.velocity[1] = -2
                    hploss = 5
                    power = [1 * (-1 if self.flip else 1), -5]
                    self.set_action("uppercut")
                elif alts[pygame.K_s]:
                    hploss = 4
                    power = [0, 2]
                    self.set_action("groundslam")
                else:
                    hploss = 6
                    power = [5 * (-1 if self.flip else 1), 0]
                    self.set_action("frontsmash")

            self.punch_count = (self.punch_count+1)%4
            hitbox = {"pos": tuple(pos), "vel": vel, "size": size, "speed": power, "type": "player", "hploss": hploss, "timer": time, "stun": stun, "iframes" : stun, "id" : random.randint(0,1000000000000000)}
            self.game.hitbox.append(hitbox)

    def cursed_technique(self):
        alts = pygame.key.get_pressed()
        size = (5, 37)
        vel = (-2 if self.flip else 2, 0)
        time = 10
        stun = 120
        black_flash = 0
        if self.flip:
            pos = [self.rect().centerx-10, self.pos[1]]
        else:
            pos = [self.rect().centerx +10, self.pos[1]]
            time = 10
        if alts[pygame.K_w] and not self.special["up"]:
            self.special["up"] = 1200
            self.velocity[1] = -2
            hploss = 12 + self.cursed_energy * 0.1
            power = [1 * (-1 if self.flip else 1), -5]
            self.set_action("uppercut")
            hitbox = {"pos": tuple(pos), "vel": vel, "size": size, "speed": power, "type": "player", "hploss": hploss, "timer": time, "stun": stun, "iframes" : time, "id" : random.randint(0,1000000000000000)}
            self.game.hitbox.append(hitbox)
        elif (alts[pygame.K_d] or alts[pygame.K_a]) and not self.special["side"]:
            if random.randint(0,100)+self.cursed_energy/4 >= 100:
                black_flash = 1
            self.special["side"] = 1500
            hploss = 16 + self.cursed_energy * 0.2
            power = [5 * (-1 if self.flip else 1), 0]
            self.set_action("divfist")
            hitbox = {"pos": tuple(pos), "vel": vel, "size": size, "speed": power, "type": "player", "hploss": hploss, "timer": time, "stun": stun, "iframes" : stun, "id" : random.randint(0,1000000000000000)}
            if black_flash == 1:
                hitbox["texture "] = [(0, 0, 0), "black_flash"]
                hploss *= 1.5
            
            self.game.hitbox.append(hitbox)
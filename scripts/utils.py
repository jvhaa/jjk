import os
import pygame
from pathlib import Path
import sys

BUNDLE_PATH = getattr(sys, "_MEIPASS", Path(os.path.abspath(os.path.dirname(__file__))).parent)

def path_of(path):
    abspath = os.path.abspath(os.path.join(BUNDLE_PATH, path))
    if not os.path.exists(abspath):
        abspath = path
    return abspath

BASE_IMG_LINK = "assets/"

def load_image(path):
    img = pygame.image.load(path_of(BASE_IMG_LINK + path)).convert_alpha()
    return img

def load_images(path):
    images = []
    arr = os.listdir(path_of(BASE_IMG_LINK + path))
    arr = sorted(arr, key=lambda x: int(x.split(".")[0]))
    for img_name in arr:
        images.append((load_image(path + '/' + img_name)))
    return images

class Animation:
    def __init__(self, images, img_dur = 5, loop = True):
        self.images = images
        self.img_dur = img_dur
        self.loop = loop
        self.done = False
        self.frames = 0

    def copy(self):
        return Animation(self.images, self.img_dur, self.loop)
    
    def update(self):
        if self.loop:
            self.frames = (self.frames+1) % (self.img_dur*len(self.images))
        else:
            self.frames = min(self.frames+1 , self.img_dur * len(self.images)-1)
            if self.frames >= self.img_dur * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frames/ self.img_dur)]

    def size(self):
        return self.images[int(self.frames/self.img_dur)].get_size()
        
textindex = "abcdefghijklmnopqrstuvwxyz01234567890 "

def text(game, surf, coords, text):
        width = 0
        for word in text:
            img = game.assets["alphabet"][textindex.index(word)]
            surf.blit(img, (coords[0]+width, coords[1]))
            width += img.get_width()+2
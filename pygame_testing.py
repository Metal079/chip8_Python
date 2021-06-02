import sys
import pygame
import time
import random

pygame.init()

size = width, height = 64, 32
speed = [2, 2]
black = 0, 0, 0
screen = pygame.display.set_mode(size)
coords = [5,5]

def pixel_move(coords):
    coordx, coordy = coords
    x = random.randrange(coordx - 1, coordx + 2, 1)
    y = random.randrange(coordy - 1, coordy + 2, 1)
    coords[0] = x
    coords[1] = y
    return coords

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    coords = pixel_move(coords)
    if coords[0] <= 0:
        coords[0] += 2
    elif coords[0] > 32:
        coords[0] -= 1

    if coords[1] <= 0:
        coords[1] += 2
    elif coords[1] > 32:
        coords[1] -= 1
   
    screen.fill(black)

    color = (255, 255, 255)
    coordx, coordy = coords
    pygame.draw.rect(color=color, rect=(coordx, coordy, 5 ,5), surface=screen)

    pygame.display.flip()
    time.sleep(0.01)
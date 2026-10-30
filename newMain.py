import pygame
from pygame.locals import *

pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Testing")

WHT, BLU, RED, BLK, GRN = (255, 255, 255), (0, 200, 255), (255, 0, 0), (0, 0, 0), (0, 128, 0)
clock = pygame.time.Clock()

run = True
squareX = 0
squareY = 0
move_speed = 5
#test

while run:
    for e in pygame.event.get():
        if e.type == QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        squareX -= move_speed
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        squareX += move_speed
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        squareY -= move_speed
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        squareY += move_speed

    win.fill(GRN)
    square = pygame.Rect(squareX, squareY, 100, 100)
    pygame.draw.rect(win, RED, square)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
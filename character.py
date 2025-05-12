import pygame
import random



pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jumpy Tower')
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

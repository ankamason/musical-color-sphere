import pygame
import math
import colorsys

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rainbow Pulsing Sphere")

center_x, center_y = width // 2, height // 2
radius = 100
color = [255, 255, 255]
hue = 0.0

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))
    
    time = pygame.time.get_ticks() / 1000.0
    pulse_radius = int(radius + 20 * math.sin(time * 2))
    
    hue = (hue + 1) % 360
    
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 0.8, 1.0)
    color = [int(r * 255), int(g * 255), int(b * 255)]
    
    pygame.draw.circle(screen, color, (center_x, center_y), pulse_radius)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

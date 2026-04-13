from body import Body
from path import Path
import numpy as np
import pygame
from vverlet2d import *

def simulate(G, softening, body_list):
    
    pygame.init()
    running = True
    screen = pygame.display.set_mode((960,540))
    dt = 0.017
    clock  = pygame.time.Clock()
    screen_scale = set_screen_scale(body_list,screen)
    size_list = create_size_list(body_list)

    # actual simulation done here
    positions,velocities,accelerations,mass_vector, mass_products = setup_verlet(body_list)
    while running:
        screen.fill((0,0,0))
        positions, velocities, accelerations = step(positions,velocities,accelerations,dt,G,mass_vector,mass_products, softening)
        pix_coords = [i*screen_scale + np.asarray(pygame.display.get_window_size())/2 for i in positions]
        for i in range(len(pix_coords)):
            pygame.draw.circle(screen,"white",(pix_coords[i][0],pix_coords[i][1]),size_list[i])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        dt = clock.tick(60)/1000
    pygame.quit()

""" def update_path(path, body_positions, frame):
    path.x[frame] = body_positions[:,0]
    path.y[frame] = body_positions[:,1] """

def create_size_list(body_list):
    size_list = np.array([body.size for body in body_list])
    return size_list

def set_screen_scale(body_list,screen):
    # pixel pos = sim pos * screen scale
    max_pos = [0,0]
    # optional scale factor
    scale_factor = 2
    for body in body_list:
        max_pos = [max(max_pos[0],np.abs(body.position[0])),max(max_pos[1],np.abs(body.position[1]))]
    # account for origin of sim being (0,0)
    max_pos *= 2 
    max_pos *= scale_factor
    screen_size = pygame.display.get_window_size()
    screen_scale = screen_size[1]/np.sqrt(np.dot(max_pos,max_pos))
    return screen_scale

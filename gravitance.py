import pygame
from simulation import Simulation
from body import Body
import numpy as np

class Gravitance:
    def __init__(self,screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = pygame.display.get_window_size()
        self.clock  = pygame.time.Clock()

    def run(self):
        
        # define bodies
        body_1 = Body([0,0],[0,0],10000,30)
        body_2 = Body([10,0],[0,-100/np.sqrt(10)],1,5)

        self.simulation = Simulation([body_1,body_2])
        self.simulation.set_G(1)
        self.simulation.set_softening(0.01)
        self.set_screen_scale()

        running = True
        while running:
            self.screen.fill((0,0,0))
            self.simulation.step()
            pix_coords = self.sim2pix(self.simulation.positions)
            for i in range(self.simulation.n):
                pygame.draw.circle(self.screen,"white",(pix_coords[i][0],pix_coords[i][1]),self.simulation.sizes[i])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()
            self.simulation.set_dt(self.clock.tick(60)/1000)
        pygame.quit()

    def set_screen_scale(self):

        self.screen_scale = self.screen_size[1]/20

    def pix2sim(pix_coords):
        # sim pos = pixel pos / screen scale
        pass

    def sim2pix(self,sim_coords):
        # pixel pos = sim pos * screen scale
        pix_coords = sim_coords*self.screen_scale
        pix_coords[:,0] += np.asarray(self.screen_size)[0]/2
        pix_coords[:,1] = np.asarray(self.screen_size)[1]/2 - pix_coords[:,1]
        return pix_coords
    

gravitance = Gravitance((960,540))
gravitance.run()
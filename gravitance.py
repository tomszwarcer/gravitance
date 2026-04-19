import pygame
from simulation import Simulation
from body import Body
import numpy as np

class Gravitance:
    def __init__(self,screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = np.asarray(pygame.display.get_window_size())
        self.camera = Camera()
        self.clock  = pygame.time.Clock()
        self.running = True
        self.mouse_clicked = False
        self.mouse_hold_counter = 0
        

    def run(self):
        
        # define bodies
        body_1 = Body([1,0],[0,0.5],10)
        body_2 = Body([-1,0],[0,-0.5],10)
        body_3 = Body([1,0],[0,0],10)

        self.simulation = Simulation([body_1,body_2])
        self.simulation.set_G(0.1)
        self.simulation.set_softening(0.01)
        self.set_screen_scale()

        while self.running:
            self.screen.fill((0,0,0))
            self.simulation.step()
            pix_coords = self.sim2pix(self.simulation.positions)
            for i in range(self.simulation.n):
                pygame.draw.circle(self.screen,"white",(pix_coords[i][0],pix_coords[i][1]),self.simulation.sizes[i]*np.sqrt(self.camera.size_sf))

            self.mouse_event()
            self.key_event()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.flip()
            self.simulation.set_dt(self.clock.tick(60)/1000)
        pygame.quit()

    def set_screen_scale(self):
        # We show a region of self.camera.screen_visible_region sim units in the y direction
        self.screen_scale = self.screen_size[1]/self.camera.screen_visible_region

    def pix2sim(self,pix_coords):
        # sim pos = pixel pos / screen scale
        sim_coords = pix_coords
        if pix_coords.ndim == 1:
            sim_coords[1] = self.screen_size[1] - sim_coords[1]
        else:
            sim_coords[:,1] = self.screen_size[1] - sim_coords[:1]
        sim_coords -= self.screen_size/2
        sim_coords /= self.camera.radial_sf
        sim_coords[:] -= self.camera.sim_origin
        sim_coords /= self.screen_scale
        return sim_coords

    def sim2pix(self,sim_coords):
        pix_coords = sim_coords * self.screen_scale
        pix_coords[:] += self.camera.sim_origin 
        pix_coords *= self.camera.radial_sf
        pix_coords[:] += self.screen_size/2
        pix_coords[:,1] = self.screen_size[1] - pix_coords[:,1]
        return pix_coords
    
    def mouse_clicked_procedure(self,clicked_pos,end_pos):
        pygame.draw.line(self.screen,"red",clicked_pos,end_pos,width=5)
        pygame.draw.circle(self.screen,"red",self.mouse_pos,self.mouse_hold_counter*np.sqrt(self.camera.size_sf))
        self.mouse_hold_counter += 0.1

    def mouse_release_procedure(self,clicked_pos,end_pos):
        new_body_pos = self.pix2sim(np.asarray(end_pos,dtype="float64"))
        diff = np.asarray(end_pos) - np.asarray(clicked_pos)
        velocity_sf = 0.01
        velocity = velocity_sf * np.asarray([-1*diff[0],diff[1]])
        self.simulation.add_body(Body(new_body_pos,velocity,(self.mouse_hold_counter**2)/25))
        self.mouse_hold_counter = 0

    def mouse_event(self):
        # mouse click system
        self.mouse_pos = pygame.mouse.get_pos()
        if not self.mouse_clicked: pygame.draw.circle(self.screen,"red",self.mouse_pos,7,3)
        if pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
            self.mouse_clicked = True
            self.mouse_clicked_pos = self.mouse_pos
        if self.mouse_clicked and pygame.mouse.get_pressed()[0]:
            self.mouse_clicked_procedure(self.mouse_clicked_pos,pygame.mouse.get_pos())
        elif self.mouse_clicked:
            self.mouse_clicked = False
            self.mouse_release_procedure(self.mouse_clicked_pos,pygame.mouse.get_pos())


    def key_event(self):
        self.key_pressed = pygame.key.get_pressed()
        if self.key_pressed[pygame.K_x]:
            self.camera.radial_sf = self.camera.radial_sf * 1.05
            self.camera.size_sf = self.camera.size_sf * 1.05
        if self.key_pressed[pygame.K_z]:
            self.camera.radial_sf = self.camera.radial_sf / 1.05
            self.camera.size_sf = self.camera.size_sf / 1.05

        if self.key_pressed[pygame.K_w]:
            self.camera.sim_origin[1] -= 10
        if self.key_pressed[pygame.K_a]:
            self.camera.sim_origin[0] += 10
        if self.key_pressed[pygame.K_s]:
            self.camera.sim_origin[1] += 10
        if self.key_pressed[pygame.K_d]:
            self.camera.sim_origin[0] -= 10

class Camera:
    def __init__(self):
        self.screen_visible_region = 3
        self.size_sf = 1 # used to scale objects when zooming
        self.radial_sf = 1 # used to scale distances when zooming
        self.x_offset = 0
        self.y_offset = 0
        self.sim_origin = np.asarray([0,0])


gravitance = Gravitance((500,500))
gravitance.run()
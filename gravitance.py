import pygame
from simulation import Simulation
from body import Body
import numpy as np

class Gravitance:
    def __init__(self,screen_size):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Times New Roman",15)
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = np.asarray(pygame.display.get_window_size())

        while self.run():
            pass


    def run(self):

        self.camera = Camera()
        self.clock  = pygame.time.Clock()
        self.running = True
        self.mouse_clicked = False
        self.mouse_hold_counter = 0
        self.paused = True
        self.mode_list = ["Add","Bind"]
        self.mode = 0 # 0 = add, 1 = bind
        
        self.simulation = Simulation([])
        self.simulation.set_G(0.1)
        self.simulation.set_softening(0.01)
        self.set_screen_scale()

        self.bind_mode_i = -1
        self.bind_mode_j = -1

        while self.running:
            self.screen.fill((0,0,0))
            info_text = self.font.render("p: pause\nr: reset\nx: zoom in\nz:zoom out\nwasd: move camera\nj: change mode\n\nMode: "+self.mode_list[self.mode],True,"red")
            paused_text = self.font.render("Paused (press p to unpause)",True,"red")
            self.screen.blit(info_text,self.screen_size*0.05)
            if self.paused: self.screen.blit(paused_text,(self.screen_size[0]*0.65,self.screen_size[1]*0.05))
            if self.simulation.n != 0:
                if not self.paused: self.simulation.step()
                pix_coords = self.sim2pix(self.simulation.positions)
                for i in range(self.simulation.n):
                    pygame.draw.circle(self.screen,pygame.color.Color(self.simulation.bodies[i].colour),(pix_coords[i][0],pix_coords[i][1]),self.simulation.sizes[i]*np.sqrt(self.camera.size_sf))

            self.mouse_event()
            self.hold_key_event()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_j:
                        self.mode = (self.mode + 1) % len(self.mode_list)
                    if self.mode == 1 and event.key == pygame.K_b:
                        self.bind(0,1)
                    if event.key == pygame.K_r:
                        return True
            pygame.display.flip()
            self.simulation.set_dt(self.clock.tick(60)/1000)
        pygame.quit()
        return False

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
        if pix_coords.ndim == 1:
            pix_coords[1] = self.screen_size[1] - pix_coords[1]
        else:
            pix_coords[:,1] = self.screen_size[1] - pix_coords[:,1]
        return pix_coords
    
    def add_mode_mouse_clicked(self,clicked_pos,end_pos):
        pygame.draw.line(self.screen,"red",clicked_pos,end_pos,width=5)
        pygame.draw.circle(self.screen,"red",self.mouse_pos,self.mouse_hold_counter*np.sqrt(self.camera.size_sf))
        self.mouse_hold_counter += 0.3

    def add_mode_mouse_release(self,clicked_pos,end_pos):
        new_body_pos = self.pix2sim(np.asarray(end_pos,dtype="float64"))
        diff = np.asarray(end_pos) - np.asarray(clicked_pos)
        velocity_sf = 0.01
        velocity = velocity_sf * np.asarray([-1*diff[0],diff[1]])
        self.simulation.add_body(Body(new_body_pos,velocity,(self.mouse_hold_counter**2)/25))
        self.mouse_hold_counter = 0

    def mouse_event(self):
        # mouse click system
        self.mouse_pos = pygame.mouse.get_pos()
        if self.mode == 0:
            if not self.mouse_clicked: pygame.draw.circle(self.screen,"red",self.mouse_pos,7,3)
            if pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
                self.mouse_clicked = True
                self.mouse_clicked_pos = self.mouse_pos
            if self.mouse_clicked and pygame.mouse.get_pressed()[0]:
                self.add_mode_mouse_clicked(self.mouse_clicked_pos,self.mouse_pos)
            elif self.mouse_clicked:
                self.mouse_clicked = False
                self.add_mode_mouse_release(self.mouse_clicked_pos,self.mouse_pos)
        if self.mode == 1 and self.simulation.n >= 2:
            pix_coords = self.sim2pix(self.simulation.positions)
            mouse_body_comparison = np.linalg.norm(self.mouse_pos*np.ones_like(pix_coords) - pix_coords,axis=1) - self.simulation.sizes*np.sqrt(self.camera.size_sf)
            if not pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
                for i in range(self.simulation.n):
                    if mouse_body_comparison[i] < 0:
                        pygame.draw.circle(self.screen,"white",(pix_coords[i][0],pix_coords[i][1]),(self.simulation.sizes[i]+1)*np.sqrt(self.camera.size_sf),2)
                        self.bind_mode_i = i
                        continue
            if pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
                self.mouse_clicked = True
                self.mouse_clicked_pos = self.mouse_pos
            if self.mouse_clicked and pygame.mouse.get_pressed()[0]:
                self.bind_mode_mouse_clicked(self.sim2pix(self.simulation.positions[self.bind_mode_i]),self.mouse_pos)
            elif self.mouse_clicked:
                self.mouse_clicked = False
                self.bind_mode_mouse_release()    

    def bind_mode_mouse_clicked(self,clicked_pos,end_pos):
        pygame.draw.circle(self.screen,"white",clicked_pos,(self.simulation.sizes[self.bind_mode_i]+1)*np.sqrt(self.camera.size_sf),2)
        pygame.draw.line(self.screen,"white",clicked_pos,end_pos,width=5)
        pix_coords = self.sim2pix(self.simulation.positions)
        mouse_body_comparison = np.linalg.norm(end_pos*np.ones_like(pix_coords) - pix_coords,axis=1) - self.simulation.sizes*np.sqrt(self.camera.size_sf)
        for j in range(self.simulation.n):
            if mouse_body_comparison[j] < 0:
                pygame.draw.circle(self.screen,"white",(pix_coords[j][0],pix_coords[j][1]),(self.simulation.sizes[j]+1)*np.sqrt(self.camera.size_sf),2)
                self.bind_mode_j = j
                continue

    def bind_mode_mouse_release(self):
        self.bind(self.bind_mode_i,self.bind_mode_j) 

    def hold_key_event(self):
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

    def bind(self,i,j):
        # gravitationally bind bodies i,j about their CM
        x_cm, v_cm = self.simulation.calculate_cm(i,j)
        r_1 = self.simulation.positions[i] - x_cm
        r_2 = self.simulation.positions[j] - x_cm
        r_12 = r_2 - r_1
        R_squared = np.dot(r_1 + r_2,r_1 + r_2)
        v_1 = np.sqrt(self.simulation.G * self.simulation.masses[j] * np.sqrt(np.dot(r_1,r_1)) / np.dot(r_12,r_12))
        v_2 = np.sqrt(self.simulation.G * self.simulation.masses[i] * np.sqrt(np.dot(r_2,r_2)) / np.dot(r_12,r_12))
        # generate normalised vector orthogonal to r_12
        orthogonal = np.random.randn(2)
        orthogonal = orthogonal - (np.dot(orthogonal,r_12/np.linalg.norm(r_12)) * r_12/np.linalg.norm(r_12))
        orthogonal = orthogonal/np.linalg.norm(orthogonal)
        self.simulation.velocities[i] = v_cm + v_1 * orthogonal
        self.simulation.velocities[j] = v_cm - v_2 * orthogonal


class Camera:
    def __init__(self):
        self.screen_visible_region = 5
        self.size_sf = 1 # used to scale objects when zooming
        self.radial_sf = 1 # used to scale distances when zooming
        self.sim_origin = np.asarray([0,0])

    def set_sim_origin(self,sim_origin):
        self.sim_origin = np.asarray(sim_origin)


gravitance = Gravitance((800,500))
import numpy as np

class Body:
    def __init__(self,position,velocity,mass,size = 0):
        self.position = np.array(position,dtype='float64')
        self.velocity = np.array(velocity,dtype='float64')
        self.mass = mass
        self.acceleration = np.zeros(2)
        if size == 0:
            self.size = 5*np.sqrt(mass)
        else:
            self.size = size

        self.trail = Trail(self.position)

        self.can_target = False # False

        
    def set_colour(self,colour):
        self.colour = colour
        
class Trail:
    def __init__(self,pos):
        self.x = np.asarray([pos[0]])
        self.y = np.asarray([pos[1]])
        self.trail_index = 0
        self.trail_length = 120
        self.trail_spacing = 3
        self.spacing_counter = 0

    def update_trail(self,pos):
        self.spacing_counter += 1
        length = len(self.x)
        if self.spacing_counter % self.trail_spacing == 0:
            self.trail_index = (self.trail_index + 1) % self.trail_length
            if length < self.trail_length:
                self.x = np.append(self.x,pos[0])
                self.y = np.append(self.y,pos[1])
                length += 1
            else:
                self.x[self.trail_index] = pos[0]
                self.y[self.trail_index] = pos[1]
        return np.asarray([np.asarray([self.x[i],self.y[i]]) for i in range(length)])
    
    def get_trail(self):
        length = len(self.x)
        return np.asarray([np.asarray([self.x[i],self.y[i]]) for i in range(length)])
    
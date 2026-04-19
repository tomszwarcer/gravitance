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
        
    def set_colour(self,colour):
        self.colour = colour
    
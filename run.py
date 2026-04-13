import numpy as np
from body import Body
from simulation import *
# gravitational constant
G = 1

# softening parameter. Set to zero for accuracy in low body-high distance simulations
softening = 0.2

body_list = []
initial_positions = np.array([[1,0],[-1,0]])
initial_velocities = np.array([[0,2],[0,-2]])
body_list.append(Body(initial_positions[0],initial_velocities[0],25,10))
body_list.append(Body(initial_positions[1],initial_velocities[1],25,10))
body_list.append(Body([-5,-5],[0.5,0.5],6,2))


simulate(G,softening,body_list)

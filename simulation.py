import numpy as np

class Simulation:
    def __init__(self,bodies):
        self.n = len(bodies)
        self.bodies = bodies
        self.positions = np.asarray([b.position for b in bodies],"float64")
        self.velocities = np.asarray([b.velocity for b in bodies],"float64")
        self.accelerations = np.asarray([b.acceleration for b in bodies],"float64")
        self.masses = np.asarray([b.mass for b in bodies])
        self.sizes = [b.size for b in bodies]
        self.dt = 0.017
    
    def add_body(self,new_body):
        self.n += 1
        self.bodies.append(new_body)
        self.sizes.append(new_body.size)
        self.masses = np.append(self.masses,new_body.mass)
        self.positions = np.append(self.positions,new_body.position).reshape((self.n,2))
        self.velocities = np.append(self.velocities,new_body.velocity).reshape((self.n,2))
        self.accelerations = np.append(self.accelerations,np.zeros(2)).reshape((self.n,2))

    def set_dt(self,dt):
        self.dt = dt

    def set_G(self,G):
        self.G = G

    def set_softening(self,softening):
        self.softening = softening

    def get_distances(self):

        # distance vectors between each body stored in an nxn matrix ('distances')
        distances = np.zeros((self.n,self.n,2))
        for i in range(self.n-1):
            comparisons = self.n-i-1

            # create an array comprised of repeated copies of current body's position
            single_arr = self.positions[i]*np.ones(comparisons)[:,np.newaxis]

            # rest of the positions
            multiple_arr = [self.positions[j] for j in range(i+1,self.n)]

            # calculate distances
            distances[i][i+1:] = np.subtract(multiple_arr,single_arr) 

        # populate rest of array with the inverted distances
        distances = distances - np.transpose(distances, (1,0,2))

        distances_squared = np.sum(distances*distances,axis=2)
        distance_magnitudes = np.sqrt(distances_squared)

        # add the identity to prevent nan (this won't affect anything)
        distances_squared = distances_squared + np.identity(self.n)
        distance_magnitudes = distance_magnitudes + np.identity(self.n)

        self.distances_matrix = distances
        self.distances_squared_matrix = distances_squared
        self.distances_mag_matrix = distance_magnitudes

    def get_forces(self):
        self.get_distances()
        forces = np.zeros((self.n,self.n,2))
        force_magnitudes = self.G*np.outer(self.masses,self.masses)/(self.distances_squared_matrix + (self.softening*np.ones((self.n,self.n))))
        forces = force_magnitudes/self.distances_mag_matrix
        forces = forces[:,:,np.newaxis]*self.distances_matrix

        self.forces_matrix = forces
        self.forces_mag_matrix = force_magnitudes
        
        net_force = np.zeros((self.n,2))
        for i in range(self.n):
            net_force[i] = np.sum(np.array([j for j in forces[i]]),axis=0)
        self.net_forces = net_force

    def update_positions(self):
        self.positions += self.dt*self.velocities + 0.5*self.dt*self.dt*self.accelerations

    def update_accelerations(self):
        self.get_forces()
        self.avg_accel = 0.5*(self.accelerations + self.net_forces/self.masses[:,np.newaxis])
        self.accelerations = self.net_forces/self.masses[:,np.newaxis]    

    def update_velocities(self):
        self.velocities += self.dt*self.avg_accel

    def step(self):
        self.update_positions()
        self.update_accelerations()
        self.update_velocities()

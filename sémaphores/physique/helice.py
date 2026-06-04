import math

class MoteurHelice:
    def __init__(self, vitesse_depart=4.0):
        self.angle = 0.0
        self.vitesse = vitesse_depart
        
    def avancer_un_tic(self):
        self.angle = (self.angle + self.vitesse) % 360
        
    def calculer_position_matrice(self, x0, y0, angle_degres):
        
        theta = math.radians(angle_degres)
        
        x_prime = x0 * math.cos(theta) - y0 * math.sin(theta)
        y_prime = x0 * math.sin(theta) + y0 * math.cos(theta)
        
        return x_prime, y_prime
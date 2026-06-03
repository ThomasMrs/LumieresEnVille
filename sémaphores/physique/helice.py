
import math

class MoteurHelice:
    def __init__(self, vitesse_depart=2.0):
        self.angle = 0.0
        self.vitesse_rotation = vitesse_depart
        
    def avancer_un_tic(self):
        """Fait tourner l'hélice d'un cran en fonction de sa vitesse."""
        self.angle = (self.angle + self.vitesse_rotation) % 360
        
    def obtenir_coordonnees_led(self, rayon):
        """Traduit les coordonnées Polaires (Rayon, Angle) en Cartésiennes (X, Y)"""
        angle_rad = math.radians(self.angle)
        
        x = rayon * math.cos(angle_rad)
        y = rayon * math.sin(angle_rad)
        
        return x, y
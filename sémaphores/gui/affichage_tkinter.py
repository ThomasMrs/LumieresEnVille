# Fichier : gui/affichage_tkinter.py

import tkinter as tk

class FenetreSimulateur:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulateur Sémaphore - Persistance Rétinienne")
        
        self.largeur = 500
        self.hauteur = 500
        self.cx = self.largeur / 2  
        self.cy = self.hauteur / 2  
        
        self.canvas = tk.Canvas(self.root, width=self.largeur, height=self.hauteur, bg="black")
        self.canvas.pack(padx=20, pady=20)
        
    def nettoyer_ecran(self):
        """On n'efface plus TOUT l'écran ! On efface uniquement la barre grise"""
        self.canvas.delete("barre")
        
    def dessiner_barre(self, x_bout1, y_bout1, x_bout2, y_bout2):
        vrai_x1 = self.cx + x_bout1
        vrai_y1 = self.cy + y_bout1
        vrai_x2 = self.cx + x_bout2
        vrai_y2 = self.cy + y_bout2
        
        # ASTUCE : On ajoute le tag "barre" pour que la gomme sache quoi effacer
        self.canvas.create_line(vrai_x1, vrai_y1, vrai_x2, vrai_y2, fill="gray", width=6, tags="barre")
        
    def dessiner_led(self, x, y, est_allumee):
        """On ne dessine QUE les LEDs allumées pour laisser une trace lumineuse (Peinture)"""
        if est_allumee:
            vrai_x = self.cx + x
            vrai_y = self.cy + y
            r_led = 4 
            
            # On dessine la lumière et on la laisse sur le Canvas !
            self.canvas.create_oval(vrai_x - r_led, vrai_y - r_led, 
                                    vrai_x + r_led, vrai_y + r_led, 
                                    fill="cyan", outline="")

import tkinter as tk

class FenetreSimulateur:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulateur Sémaphore - Jalon 2")
        
        self.zone_saisie = tk.Frame(self.root)
        self.zone_saisie.pack(pady=10)
        
        tk.Label(self.zone_saisie, text="Lettre à afficher :").pack(side=tk.LEFT)
        self.champ_lettre = tk.Entry(self.zone_saisie, width=5)
        self.champ_lettre.pack(side=tk.LEFT, padx=5)
        
        self.bouton_valider = tk.Button(self.zone_saisie, text="Afficher")
        self.bouton_valider.pack(side=tk.LEFT)
        
        self.largeur = 500
        self.hauteur = 500
        self.cx = self.largeur / 2  
        self.cy = self.hauteur / 2  
        
        self.canvas = tk.Canvas(self.root, width=self.largeur, height=self.hauteur, bg="black")
        self.canvas.pack(padx=20, pady=20)
        
    def nettoyer_ecran(self):
        self.canvas.delete("barre")
        
    def dessiner_barre(self, x_bout1, y_bout1, x_bout2, y_bout2):
        vrai_x1 = self.cx + x_bout1
        vrai_y1 = self.cy + y_bout1
        vrai_x2 = self.cx + x_bout2
        vrai_y2 = self.cy + y_bout2
        
        self.canvas.create_line(vrai_x1, vrai_y1, vrai_x2, vrai_y2, fill="gray", width=6, tags="barre")
        
    def dessiner_led(self, x, y, est_allumee):
        if est_allumee:
            vrai_x = self.cx + x
            vrai_y = self.cy + y
            self.canvas.create_oval(vrai_x - 4, vrai_y - 4, vrai_x + 4, vrai_y + 4, fill="cyan", outline="")
import tkinter as tk

class FenetreSimulateur:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulateur Sémaphore")
        
        self.zone_saisie = tk.Frame(self.root)
        self.zone_saisie.pack(pady=10)
        
        tk.Label(self.zone_saisie, text="Angle (0-359):").pack(side=tk.LEFT)
        self.champ_angle = tk.Entry(self.zone_saisie, width=5)
        self.champ_angle.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.zone_saisie, text="Rayon (0-10):").pack(side=tk.LEFT)
        self.champ_rayon = tk.Entry(self.zone_saisie, width=5)
        self.champ_rayon.pack(side=tk.LEFT, padx=5)
        
        self.bouton_valider = tk.Button(self.zone_saisie, text="Ajouter le point")
        self.bouton_valider.pack(side=tk.LEFT)
        
        self.largeur = 600
        self.hauteur = 500
        
        self.canvas = tk.Canvas(self.root, width=self.largeur, height=self.hauteur, bg="black")
        self.canvas.pack(padx=20, pady=20)
        
    def nettoyer_ecran(self):
        self.canvas.delete("barre")
        
    def dessiner_barre(self, centre_x, centre_y, x_bout1, y_bout1, x_bout2, y_bout2):
        vrai_x1 = centre_x + x_bout1
        vrai_y1 = centre_y + y_bout1
        vrai_x2 = centre_x + x_bout2
        vrai_y2 = centre_y + y_bout2
        
        self.canvas.create_line(vrai_x1, vrai_y1, vrai_x2, vrai_y2, fill="gray", width=6, tags="barre")
        
    def dessiner_led(self, centre_x, centre_y, x, y, est_allumee):
        if est_allumee:
            vrai_x = centre_x + x
            vrai_y = centre_y + y
            self.canvas.create_oval(vrai_x - 4, vrai_y - 4, vrai_x + 4, vrai_y + 4, fill="cyan", outline="")
import tkinter as tk
import math

class SimulateurTable:
    def __init__(self, root, fichier_csv):
        self.top = tk.Toplevel(root)
        self.top.title("Simulateur Table Traçante")
        # Couleur de fond de la fenêtre Tkinter
        self.top.configure(bg="#333")
        
        # Dimensions fixes 
        # Taille du plan de travail papier
        self.W = 300
        self.H = 300
        self.CX = self.W / 2
        self.CY = self.H / 2
        
        self.canvas = tk.Canvas(self.top, width=self.W, height=self.H, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        
        self._dessiner_axes()
        
        # Les bras mécaniques qui suivent le curseur
        # Couleur et épaisseur des bras CNC
        self.rail_horizontal = self.canvas.create_line(0, self.CY, self.W, self.CY, fill="#666666", width=3)
        self.rail_vertical = self.canvas.create_line(self.CX, 0, self.CX, self.H, fill="#666666", width=3)
        
        # Lecture des données 
        self.points = self.charger_points(fichier_csv)
        self.index_actuel = 0
        
        # Le marqueur 
        self.stylo_visuel = self.canvas.create_oval(0, 0, 0, 0, fill="red", outline="black", width=1)
        self.derniere_pos = None
        
        self.top.after(500, self.animer)

    def _dessiner_axes(self):
        """Dessine les pointillés de repérage en arrière-plan."""
        # Style des axes (dash = taille pointillé)
        self.canvas.create_line(0, self.CY, self.W, self.CY, fill="#cccccc", dash=(4, 4))
        self.canvas.create_text(self.W - 10, self.CY - 10, text="X", fill="#999999", font=("Arial", 8, "bold"))
        self.canvas.create_line(self.CX, 0, self.CX, self.H, fill="#cccccc", dash=(4, 4))
        self.canvas.create_text(self.CX + 10, 10, text="Y", fill="#999999", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.CX - 10, self.CY + 10, text="0", fill="#999999", font=("Arial", 8))

    def charger_points(self, fichier_csv):
        """Extrait les points polaires et les convertit en cartésien normé (mise à l'échelle)."""
        points_bruts = []
        try:
            with open(fichier_csv, 'r') as f:
                lignes = f.readlines()
                for ligne in lignes:
                    if "rayon" in ligne or not ligne.strip():
                        continue
                    r, a, s = ligne.strip().split(';')
                    points_bruts.append((float(r), float(a), int(s)))
        except Exception:
            pass
        
        if not points_bruts:
            return []
            
        coords = []
        
        # échelle pour ne pas déborder la fenêtre
        r_max = max(p[0] for p in points_bruts) if points_bruts else 1.0
        if r_max == 0: 
            r_max = 1.0
        # Facteur de mise à l'échelle (0.85 = prend 85% de la toile)
        echelle = (min(self.W, self.H) / 2) * 0.85
        
        for r, a, s in points_bruts:
            r_ech = (r / r_max) * echelle
            x = self.CX + r_ech * math.cos(math.radians(a))
            # ppur mettre l'image à l'endroit
            y = self.CY - r_ech * math.sin(math.radians(a))
            coords.append((x, y, s))
            
        return coords

    def animer(self):
        """Boucle de tracé qui déplace les rails et gère le levé de stylo."""
        if self.index_actuel >= len(self.points):
            # pour enlever stylo et rail fin du dessin
            self.canvas.itemconfig(self.stylo_visuel, state="hidden")
            self.canvas.itemconfig(self.rail_horizontal, state="hidden")
            self.canvas.itemconfig(self.rail_vertical, state="hidden")
            return
            
        x, y, s = self.points[self.index_actuel]
        
        # Mise à jour de la position des rails 
        self.canvas.coords(self.rail_horizontal, 0, y, self.W, y)
        self.canvas.coords(self.rail_vertical, x, 0, x, self.H)
        
        # Déplacement de la pointe du stylo
        # Taille du curseur
        self.canvas.coords(self.stylo_visuel, x-5, y-5, x+5, y+5)
        
        # Le stylo frotte le papier, on laisse une trace noire quand c'est en 1
        if s == 1:
            # Couleur du curseur quand stylo posé
            self.canvas.itemconfig(self.stylo_visuel, fill="red")
            if self.derniere_pos:
                px, py = self.derniere_pos
                # Couleur et épaisseur dessin sur le papier
                self.canvas.create_line(px, py, x, y, fill="black", width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        # le stylo est en 0, il ne trace pas, on le met en bleu pour simuler qu'il est levé
        else:
            # Couleur du curseur quand stylo levé
            self.canvas.itemconfig(self.stylo_visuel, fill="lightblue")
            
        # pour que le stylo ne soit pas gêné par les rails
        self.canvas.tag_raise(self.stylo_visuel)
            
        self.derniere_pos = (x, y)
        self.index_actuel += 1
        
        # Vitesse d'animation
        # Vitesse d'animation (millisecondes entre chaque point tracé)
        self.top.after(10, self.animer)

def simuler_table_tracante_csv(fichier_csv, root_parent, duree_sec=10):
    """Fonction d'appel qui gère le Toplevel et ferme la fenêtre à la fin du chrono."""
    app = SimulateurTable(root_parent, fichier_csv)
    app.top.after(duree_sec * 1000, app.top.destroy)
    app.top.wait_window(app.top)
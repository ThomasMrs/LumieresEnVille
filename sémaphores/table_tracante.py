import tkinter as tk
import math

class SimulateurTable:
    def __init__(self, root, fichier_csv):
        self.top = tk.Toplevel(root)
        self.top.title("Simulateur Table Traçante")
        # Couleur de fond de la fenêtre Tkinter
        self.top.configure(bg="#f50000")
        
        # Dimensions fixes 
        # Taille du plan de travail papier
        self.W = 300
        self.H = 300
        self.CX = self.W / 2
        self.CY = self.H / 2
        
        self.canvas = tk.Canvas(self.top, width=self.W, height=self.H, bg="#f50000", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        
        self._dessiner_axes()
        
        # Les bras mécaniques qui suivent le curseur
        # Couleur et épaisseur 
        self.rail_horizontal = self.canvas.create_line(0, self.CY, self.W, self.CY, fill="#eaf500", width=3)
        self.rail_vertical = self.canvas.create_line(self.CX, 0, self.CX, self.H, fill="#eaf500", width=3)
        
        # Lecture des données 
        self.points = self.charger_points(fichier_csv)
        self.index_actuel = 0
        
        # Le marqueur 
        self.stylo_visuel = self.canvas.create_oval(0, 0, 0, 0, fill="#eaf500", outline="#eaf500", width=1)
        self.derniere_pos = None
        
        self.top.after(500, self.animer)

    def _dessiner_axes(self):
        """Dessine les pointillés de repérage en arrière-plan."""
        # Style des axes (dash = taille pointillé)
        self.canvas.create_line(0, self.CY, self.W, self.CY, fill="white", dash=(4, 4))
        self.canvas.create_text(self.W - 10, self.CY - 10, text="X", fill="white", font=("Arial", 8, "bold"))
        self.canvas.create_line(self.CX, 0, self.CX, self.H, fill="white", dash=(4, 4))
        self.canvas.create_text(self.CX + 10, 10, text="Y", fill="white", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.CX - 10, self.CY + 10, text="0", fill="white", font=("Arial", 8))

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
        # [TAG_ECHELLE] - Pour agrandir ou réduire la taille du dessin sur la feuille
        echelle = (min(self.W, self.H) / 2) * 0.85
        
        for r, a, s in points_bruts:
            r_ech = (r / r_max) * echelle
            x = self.CX + r_ech * math.cos(math.radians(a))
            # pour mettre l'image à l'endroit
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
        
        # [TAG_MOUVEMENT_DYNAMIQUE] - Mise à jour de la position des rails
        # Le rail horizontal est une ligne horizontale à la hauteur Y
        self.canvas.coords(self.rail_horizontal, 0, y, self.W, y)
        # Le rail vertical est une ligne verticale à la position X
        self.canvas.coords(self.rail_vertical, x, 0, x, self.H)
        
        # Déplacement de la pointe du stylo
        self.canvas.coords(self.stylo_visuel, x-5, y-5, x+5, y+5)
        
        # Le stylo frotte le papier, on laisse une trace noire quand c'est en 1
        if s == 1:
            # Couleur du curseur quand stylo posé
            self.canvas.itemconfig(self.stylo_visuel, fill="#eaf500")
            if self.derniere_pos:
                px, py = self.derniere_pos
                # Couleur et épaisseur dessin sur le papier
                self.canvas.create_line(px, py, x, y, fill="#eaf500", width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        # le stylo est en 0, il ne trace pas, on le met en bleu
        else:
            self.canvas.itemconfig(self.stylo_visuel, fill="lightblue")
            
        # pour que le stylo soit toujours au-dessus des rails
        self.canvas.tag_raise(self.stylo_visuel)
            
        self.derniere_pos = (x, y)
        self.index_actuel += 1
        
        # [TAG_VITESSE_CNC] - Vitesse de déplacement de la machine CNC
        self.top.after(10, self.animer)

def simuler_table_tracante_csv(fichier_csv, root_parent, duree_sec=10):
    """Fonction d'appel qui gère le Toplevel et ferme la fenêtre à la fin du chrono."""
    app = SimulateurTable(root_parent, fichier_csv)
    app.top.after(duree_sec * 1000, app.top.destroy)
    app.top.wait_window(app.top)
import tkinter as tk
import math

class SimulateurTable:
    def __init__(self, root, fichier_csv):
        self.top = tk.Toplevel(root)
        self.top.title("Simulateur Table Traçante")
        self.top.configure(bg="#333")
        
        self.W = 600
        self.H = 600
        self.CX = self.W / 2
        self.CY = self.H / 2
        
        self.canvas = tk.Canvas(self.top, width=self.W, height=self.H, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        
        self.points = self.charger_points(fichier_csv)
        self.index_actuel = 0
        
        self.stylo_visuel = self.canvas.create_oval(0, 0, 0, 0, fill="red", outline="")
        self.derniere_pos = None
        
        self.top.after(500, self.animer)

    def charger_points(self, fichier_csv):
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
        r_max = max(p[0] for p in points_bruts) if points_bruts else 1.0
        if r_max == 0: 
            r_max = 1.0
        
        echelle = (min(self.W, self.H) / 2) * 0.85
        
        for r, a, s in points_bruts:
            r_ech = (r / r_max) * echelle
            x = self.CX + r_ech * math.cos(math.radians(a))
            y = self.CY + r_ech * math.sin(math.radians(a))
            coords.append((x, y, s))
            
        return coords

    def animer(self):
        if self.index_actuel >= len(self.points):
            self.canvas.itemconfig(self.stylo_visuel, state="hidden")
            return
            
        x, y, s = self.points[self.index_actuel]
        
        self.canvas.coords(self.stylo_visuel, x-5, y-5, x+5, y+5)
        
        if s == 1:
            self.canvas.itemconfig(self.stylo_visuel, fill="red")
            if self.derniere_pos:
                px, py = self.derniere_pos
                self.canvas.create_line(px, py, x, y, fill="black", width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        else:
            self.canvas.itemconfig(self.stylo_visuel, fill="lightblue")
            
        self.derniere_pos = (x, y)
        self.index_actuel += 1
        
        self.top.after(10, self.animer)

def simuler_table_tracante_csv(fichier_csv, root_parent):
    SimulateurTable(root_parent, fichier_csv)
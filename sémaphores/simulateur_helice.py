import tkinter as tk
import math
import os

class HelicePOV:
    def __init__(self, root, fichier_initial=None, couleur=(0, 255, 255)):
        self.root = root
        self.root.title("Simulation Hélice POV")
        self.root.configure(bg="#222")
        
        self.W = 300
        self.H = 300
        self.CX = self.W / 2
        self.CY = self.H / 2
        self.refresh_rate = 20  
        
        self.vitesse_rotation = 5.0
        self.angle_moteur = 0.0
        self.pixels_remanents = []
        self.lettre_actuelle = "A"
        
        self.couleur_rgb = couleur
        self.couleur_hex = f"#{couleur[0]:02x}{couleur[1]:02x}{couleur[2]:02x}"
        
        self.matrices_polaires = {"A": self._creer_matrice_lettre_A()}
        self.CORRECTION_PHASE = 90
        
        self._creer_interface()
        self._initialiser_matrice_rotation()
        
        if fichier_initial and os.path.exists(fichier_initial):
            self.charger_depuis_csv_local(fichier_initial)
            self.lettre_actuelle = os.path.basename(fichier_initial).upper()
            self.entry_lettre.delete(0, tk.END)
            self.entry_lettre.insert(0, fichier_initial)
            
        self.animate()

    def _creer_matrice_lettre_A(self):
        matrice = [[None for _ in range(10)] for _ in range(360)]
        for a in range(80, 100): 
            matrice[a][9] = (255, 255, 255)
        return matrice

    def _creer_interface(self):
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.control_frame = tk.Frame(self.root, bg="#333", padx=15, pady=15)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(self.control_frame, text="Contrôle POV", font=("Arial", 14), bg="#333", fg="white").pack()
        self.entry_lettre = tk.Entry(self.control_frame)
        self.entry_lettre.pack(pady=5)
        tk.Button(self.control_frame, text="Afficher", command=self.update_lettre).pack()

        tk.Label(self.control_frame, text="Vitesse (°/frame):", bg="#333", fg="white").pack(anchor="w", pady=(20,0))
        self.slider_vitesse = tk.Scale(self.control_frame, from_=1, to=60, orient=tk.HORIZONTAL, bg="#333", fg="white", highlightthickness=0, command=self.update_vitesse)
        self.slider_vitesse.set(self.vitesse_rotation)
        self.slider_vitesse.pack(fill=tk.X, pady=5)

    def update_vitesse(self, val):
        self.vitesse_rotation = float(val)

    def update_lettre(self):
        choix = self.entry_lettre.get().strip()
        if os.path.exists(choix):
            self.charger_depuis_csv_local(choix)
            self.lettre_actuelle = os.path.splitext(os.path.basename(choix))[0].upper()

    def charger_depuis_csv_local(self, nom_fichier):
        matrice = [[None for _ in range(10)] for _ in range(360)]
        points = []
        try:
            with open(nom_fichier, "r") as f:
                for ligne in f:
                    if ";" not in ligne or "rayon" in ligne: 
                        continue
                    parts = ligne.strip().split(";")
                    points.append((float(parts[0]), int(float(parts[1])), int(parts[2])))
        except Exception:
            return

        r_max = max([p[0] for p in points]) if points else 1.0
        if r_max == 0:
            r_max = 1.0
        
        for r, a, s in points:
            if s == 1:
                led_idx = int((r / r_max) * 9)
                if led_idx > 9: led_idx = 9
                if led_idx < 0: led_idx = 0
                matrice[a % 360][led_idx] = self.couleur_rgb
        
        self.matrices_polaires[os.path.basename(nom_fichier).upper()] = matrice

    def _initialiser_matrice_rotation(self):
        self.bras_gui = [self.canvas.create_line(0,0,0,0, fill="gray", width=4) for _ in range(4)]
        self.leds_gui = [[self.canvas.create_oval(0,0,0,0, fill="#111") for _ in range(10)] for _ in range(4)]

    def _gerer_remanence(self):
        for p in self.pixels_remanents[:]:
            p['vie'] -= 15
            if p['vie'] <= 0:
                self.canvas.delete(p['id'])
                self.pixels_remanents.remove(p)
            else:
                ratio = p['vie'] / 255.0
                c = f'#{int(p["r"]*ratio):02x}{int(p["g"]*ratio):02x}{int(p["b"]*ratio):02x}'
                self.canvas.itemconfig(p['id'], fill=c)

    def animate(self):
        largeur_actuelle = self.canvas.winfo_width()
        hauteur_actuelle = self.canvas.winfo_height()
        
        if largeur_actuelle > 10 and hauteur_actuelle > 10:
            self.W = largeur_actuelle
            self.H = hauteur_actuelle
            self.CX = self.W / 2
            self.CY = self.H / 2

        self._gerer_remanence()
        
        matrice = self.matrices_polaires.get(self.lettre_actuelle, [[]])
        taille_min = min(self.W, self.H)
        
        pas_vitesse = int(self.vitesse_rotation)
        if pas_vitesse < 1: pas_vitesse = 1

        for pas in range(pas_vitesse):
            self.angle_moteur = (self.angle_moteur + 1) % 360
            dernier_pas = (pas == pas_vitesse - 1)

            for b in range(4):
                angle_physique = (self.angle_moteur + b * 90) % 360
                angle_rad = math.radians(angle_physique - 90) 
                
                angle_rad_prev = math.radians((angle_physique - 1) - 90)

                if dernier_pas:
                    x_b = self.CX + (self.W / 2.5) * math.cos(angle_rad)
                    y_b = self.CY + (self.H / 2.5) * math.sin(angle_rad)
                    self.canvas.coords(self.bras_gui[b], self.CX, self.CY, x_b, y_b)

                for i in range(10):
                    idx = int((angle_physique + self.CORRECTION_PHASE) % 360)
                    r_phys = (i + 1) * ((taille_min / 2 - 20) / 10.5) 
                    
                    x = self.CX + r_phys * math.cos(angle_rad)
                    y = self.CY + r_phys * math.sin(angle_rad)
                    
                    prev_x = self.CX + r_phys * math.cos(angle_rad_prev)
                    prev_y = self.CY + r_phys * math.sin(angle_rad_prev)

                    if idx < 360 and len(matrice[idx]) > i and matrice[idx][i]:
                        c = self.couleur_hex
                        tid = self.canvas.create_line(prev_x, prev_y, x, y, fill=c, width=4, capstyle=tk.ROUND)
                        
                        self.pixels_remanents.append({
                            'id': tid, 'vie': 255, 
                            'r': self.couleur_rgb[0], 
                            'g': self.couleur_rgb[1], 
                            'b': self.couleur_rgb[2]
                        })
                        
                        if dernier_pas:
                            self.canvas.itemconfig(self.leds_gui[b][i], fill=c)
                            self.canvas.coords(self.leds_gui[b][i], x-3, y-3, x+3, y+3)
                    else:
                        if dernier_pas:
                            self.canvas.itemconfig(self.leds_gui[b][i], fill="#111")
                            self.canvas.coords(self.leds_gui[b][i], x-3, y-3, x+3, y+3)
                            
        self.root.after(self.refresh_rate, self.animate)

def lancer_helice_ui(fenetre_parente, donnees=None, couleur=(0, 255, 255), duree_sec=10):
    top = tk.Toplevel(fenetre_parente)
    app = HelicePOV(top, fichier_initial=donnees, couleur=couleur)
    
    top.after(duree_sec * 1000, top.destroy)
    
    top.wait_window(top)

if __name__ == "__main__":
    root = tk.Tk()
    app = HelicePOV(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = HelicePOV(root)
    root.mainloop()
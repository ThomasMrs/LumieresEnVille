import tkinter as tk
import math
import os

class HelicePOV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Hélice POV")
        self.root.configure(bg="#222")
        
        self.W = 300
        self.H = 300
        self.CX = self.W / 2
        self.CY = self.H / 2
        self.ESPACEMENT_LED = 20
        self.refresh_rate = 20  
        
        self.vitesse_rotation = 5.0
        self.angle_moteur = 0.0
        self.pixels_remanents = []
        self.lettre_actuelle = "A"
        
        matrice_A = []
        for a in range(360):
            colonne_leds = []
            for led in range(10):
                if (240 < a < 260) or (280 < a < 300):
                    colonne_leds.append((255, 50, 50))
                else:
                    colonne_leds.append(None)
            matrice_A.append(colonne_leds)
            
        self.matrices_polaires = {"A": matrice_A}
        
        self.CORRECTION_PHASE = 90
        
        self._creer_interface()
        self._initialiser_matrice_rotation()
        self.animate()

    def _creer_interface(self):
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.control_frame = tk.Frame(self.root, bg="#333", padx=15, pady=15)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(self.control_frame, text="Contrôle POV", font=("Arial", 14, "bold"), bg="#333", fg="white").pack(pady=(0, 20))
        
        self.entry_lettre = tk.Entry(self.control_frame, font=("Arial", 12), width=15)
        self.entry_lettre.insert(0, "A")
        self.entry_lettre.pack(fill=tk.X, pady=5)
        
        tk.Button(self.control_frame, text="Afficher", command=self.update_lettre, bg="#555").pack(fill=tk.X, pady=5)
        
        tk.Label(self.control_frame, text="Vitesse (°/frame):", bg="#333", fg="white").pack(anchor="w", pady=(20,0))
        self.slider_vitesse = tk.Scale(self.control_frame, from_=1, to=40, orient=tk.HORIZONTAL, bg="#333", fg="white", highlightthickness=0, command=self.update_vitesse)
        self.slider_vitesse.set(self.vitesse_rotation)
        self.slider_vitesse.pack(fill=tk.X, pady=5)

    def update_vitesse(self, val):
        self.vitesse_rotation = float(val)

    def update_lettre(self):
        choix = self.entry_lettre.get().strip()
        if choix.upper() in self.matrices_polaires:
            self.lettre_actuelle = choix.upper()
        elif os.path.exists(choix):
            self.charger_depuis_csv_local(choix)
            self.lettre_actuelle = os.path.splitext(os.path.basename(choix))[0].upper()

    def charger_depuis_csv_local(self, nom_fichier):
        matrice = {}
        for a in range(360):
            matrice[a] = [None] * 10
            
        try:
            with open(nom_fichier, "r") as f:
                for ligne in f:
                    if ";" not in ligne or ligne.startswith("rayon"): 
                        continue
                        
                    r, angle, stylo = ligne.strip().split(";")
                    
                    if stylo == "1":
                        led_idx = int((float(r) / 200.0) * 9)
                        if led_idx > 9:
                            led_idx = 9
                            
                        angle_int = int(float(angle)) % 360
                        matrice[angle_int][led_idx] = (0, 255, 255) # Couleur cyan
                        
            nom_cle = os.path.splitext(os.path.basename(nom_fichier))[0].upper()
            self.matrices_polaires[nom_cle] = [matrice[a] for a in range(360)]
            print("CSV chargé :", nom_fichier)
            
        except Exception as e:
            print("Erreur lors de la lecture du fichier CSV :", e)

    def _initialiser_matrice_rotation(self):
        self.leds_initiales = []
        for i in range(10):
            x = (i + 1) * self.ESPACEMENT_LED
            y = 0
            self.leds_initiales.append((x, y))
            
        self.bras_gui = [self.canvas.create_line(0,0,0,0, fill="gray", width=6) for _ in range(4)]
        self.leds_gui = [[self.canvas.create_oval(0,0,0,0, fill="#111") for _ in range(10)] for _ in range(4)]

    def _gerer_remanence(self):
        """Gestion de l'effet de persistance rétinienne (fondu)"""
        pixels_restants = []
        for p in self.pixels_remanents:
            p['vie'] -= 15  
            if p['vie'] > 0:
                ratio = p['vie'] / 255.0
                rouge = int(p["r"] * ratio)
                vert = int(p["g"] * ratio)
                bleu = int(p["b"] * ratio)
                
                hex_color = f'#{rouge:02x}{vert:02x}{bleu:02x}'
                self.canvas.itemconfig(p['id'], fill=hex_color, outline="")
                pixels_restants.append(p)
            else:
                self.canvas.delete(p['id'])
                
        self.pixels_remanents = pixels_restants

    def animate(self):
        self._gerer_remanence()
        
        self.angle_moteur = (self.angle_moteur + self.vitesse_rotation) % 360
        
        if self.lettre_actuelle in self.matrices_polaires:
            matrice = self.matrices_polaires[self.lettre_actuelle]
        else:
            matrice = [[] for _ in range(360)]

        for b in range(4):
            angle_physique = (self.angle_moteur + b * 90) % 360
            angle_lecture = int((angle_physique + self.CORRECTION_PHASE) % 360)
            
            alpha = math.radians(angle_physique)
            cos_a = math.cos(alpha)
            sin_a = math.sin(alpha)

            x_bout = self.CX + (10.5 * self.ESPACEMENT_LED) * cos_a
            y_bout = self.CY + (10.5 * self.ESPACEMENT_LED) * sin_a
            self.canvas.coords(self.bras_gui[b], self.CX, self.CY, x_bout, y_bout)

            for i, (x0, y0) in enumerate(self.leds_initiales):
                # Matrice de rotation (x', y')
                x = self.CX + (x0 * cos_a - y0 * sin_a)
                y = self.CY + (x0 * sin_a + y0 * cos_a)
                
                self.canvas.coords(self.leds_gui[b][i], x-4, y-4, x+4, y+4)

                if angle_lecture < len(matrice) and len(matrice[angle_lecture]) > i and matrice[angle_lecture][i]:
                    r, g, b_col = matrice[angle_lecture][i]
                    hex_col = f'#{r:02x}{g:02x}{b_col:02x}'
                    
                    self.canvas.itemconfig(self.leds_gui[b][i], fill=hex_col)
                    
                    tid = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=hex_col, outline="")
                    self.pixels_remanents.append({'id': tid, 'vie': 255, 'r': r, 'g': g, 'b': b_col})
                else:
                    self.canvas.itemconfig(self.leds_gui[b][i], fill="#111")
                    
        self.root.after(self.refresh_rate, self.animate)

def lancer_helice_ui(fenetre_parente, nom_fichier_csv=None):
    """Fonction appelée par mainsemaphore.py pour ouvrir l'hélice"""
    top = tk.Toplevel(fenetre_parente)
    app = HelicePOV(top)
    if nom_fichier_csv and os.path.exists(nom_fichier_csv):
        app.charger_depuis_csv_local(nom_fichier_csv)
        app.lettre_actuelle = os.path.splitext(os.path.basename(nom_fichier_csv))[0].upper()

if __name__ == "__main__":
    root = tk.Tk()
    app = HelicePOV(root)
    root.mainloop()
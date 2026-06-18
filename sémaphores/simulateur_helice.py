import tkinter as tk
import math
import os

class HelicePOV:
    def __init__(self, root, fichier_initial=None):
        self.root = root
        self.root.title("Simulation Hélice POV")
        # Couleur du fond
        self.root.configure(bg="#222")
        
        # Dimensions de base 
        # Taille par défaut de la fenêtre
        self.W = 300
        self.H = 300
        self.CX = self.W / 2
        self.CY = self.H / 2
        
        # Réglages du moteur
        # FPS du moteur (20ms)
        self.refresh_rate = 20  
        # Vitesse par défaut
        self.vitesse_rotation = 5.0
        self.angle_moteur = 0.0
        
        # rémanence
        self.pixels_remanents = []
        self.lettre_actuelle = "A"
        self.matrices_polaires = {"A": self._creer_matrice_lettre_A()}
        # Décalage du point 0°
        self.CORRECTION_PHASE = 90
        
        self._creer_interface()
        self._initialiser_matrice_rotation()
        
        # Chargement des données cibles via le main
        if fichier_initial and os.path.exists(fichier_initial):
            self.charger_depuis_csv_local(fichier_initial)
            self.lettre_actuelle = os.path.basename(fichier_initial).upper()
            self.entry_lettre.delete(0, tk.END)
            self.entry_lettre.insert(0, fichier_initial)
            
        self.animate()

    def _creer_matrice_lettre_A(self):
        """Génère une véritable lettre 'A' visible sur l'hélice."""
        matrice = [[None for _ in range(10)] for _ in range(360)]

       
        def draw_line(x1, y1, x2, y2):
            dist = math.hypot(x2 - x1, y2 - y1)
            steps = int(dist * 20) # Haute résolution pour un tracé net
            for i in range(steps + 1):
                t = i / steps if steps > 0 else 0
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)

                r_float = math.hypot(x, y)
                r_idx = int(round(r_float))

                if 0 <= r_idx <= 9:
                    angle_rad = math.atan2(y, -x)
                    idx = int(math.degrees(angle_rad)) % 360
                    
                    # On allume la LED ciblée
                    matrice[idx][r_idx] = True
                    matrice[(idx + 1) % 360][r_idx] = True
                    matrice[(idx - 1) % 360][r_idx] = True
                    if r_idx < 9:
                        matrice[idx][r_idx + 1] = True

        
        draw_line(0, 8, -4, -8)
        draw_line(0, 8, 4, -8)
        draw_line(-2, 0, 2, 0)

        return matrice

    def _creer_interface(self):
        """Sépare la fenêtre entre le canvas visuel (à gauche) et le panneau de contrôle (à droite)."""
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.control_frame = tk.Frame(self.root, bg="#333", padx=15, pady=15)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(self.control_frame, text="Contrôle POV", font=("Arial", 14), bg="#333", fg="white").pack()
        self.entry_lettre = tk.Entry(self.control_frame)
        self.entry_lettre.pack(pady=5)
        tk.Button(self.control_frame, text="Afficher", command=self.update_lettre).pack()

        tk.Label(self.control_frame, text="Vitesse (°/frame):", bg="#333", fg="white").pack(anchor="w", pady=(20,0))
        # Plage de la barre de vitesse (to=60)
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
        """Convertit les points du CSV en une matrice [360 degrés] x [10 LEDs]."""
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

        # pour allumer la dernière led quand c'est le rayon maximum
        r_max = max([p[0] for p in points]) if points else 1.0
        if r_max == 0:
            r_max = 1.0
        
        for r, a, s in points:
            if s == 1:
                # Mise à l'échelle sur le nombre de LEDs physiques (9)
                led_idx = int((r / r_max) * 9)
                if led_idx > 9: led_idx = 9
                if led_idx < 0: led_idx = 0
                matrice[a % 360][led_idx] = (0, 255, 255)
        
        self.matrices_polaires[os.path.basename(nom_fichier).upper()] = matrice

    def _initialiser_matrice_rotation(self):
        """Prépare les objets Tkinter (bras mécaniques et LEDs) sans les positionner."""
        # Couleur et épaisseur des bras métalliques
        self.bras_gui = [self.canvas.create_line(0,0,0,0, fill="gray", width=4) for _ in range(4)]
        # Couleur des LEDs quand elles sont éteintes
        self.leds_gui = [[self.canvas.create_oval(0,0,0,0, fill="#111") for _ in range(10)] for _ in range(4)]

    def _gerer_remanence(self):
        """Réduit la durée de vie des pixels. S'ils sont à 0, on les détruit pour simuler le fondu."""
        for p in self.pixels_remanents[:]:
            # Vitesse d'estompage de la lumière (plus grand = disparaît plus vite)
            p['vie'] -= 15
            if p['vie'] <= 0:
                self.canvas.delete(p['id'])
                self.pixels_remanents.remove(p)
            else:
                ratio = p['vie'] / 255.0
                c = f'#{int(p["r"]*ratio):02x}{int(p["g"]*ratio):02x}{int(p["b"]*ratio):02x}'
                self.canvas.itemconfig(p['id'], fill=c)

    def animate(self):
        """Moteur de rendu physique : fait tourner l'hélice et allume les LEDs à l'angle ciblé."""
        # Adaptation fenêtre si changement de taille
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

        # pas entre chaque refresh d'image
        for pas in range(pas_vitesse):
            self.angle_moteur = (self.angle_moteur + 1) % 360
            dernier_pas = (pas == pas_vitesse - 1)

            # Simulation des 4 bras de l'hélice
            for b in range(4):
                angle_physique = (self.angle_moteur + b * 90) % 360
                angle_rad = math.radians(angle_physique - 90) 
                angle_rad_prev = math.radians((angle_physique - 1) - 90)

                # Barres en métal
                if dernier_pas:
                    # Longueur visuelle des barres sur l'écran
                    x_b = self.CX + (self.W / 2.5) * math.cos(angle_rad)
                    y_b = self.CY + (self.H / 2.5) * math.sin(angle_rad)
                    self.canvas.coords(self.bras_gui[b], self.CX, self.CY, x_b, y_b)

                # Allumage des 10 LEDs
                for i in range(10):
                    idx = int((angle_physique + self.CORRECTION_PHASE) % 360)
                    
                    # Écartement des LEDs sur le bras
                    r_phys = (i + 1) * ((taille_min / 2 - 20) / 10.5) 
                    
                    x = self.CX + r_phys * math.cos(angle_rad)
                    y = self.CY + r_phys * math.sin(angle_rad)
                    prev_x = self.CX + r_phys * math.cos(angle_rad_prev)
                    prev_y = self.CY + r_phys * math.sin(angle_rad_prev)

                    # indication de la matrice pour l'angle et la led nécessaire
                    if idx < 360 and len(matrice[idx]) > i and matrice[idx][i]:
                        # Couleur du flash LED (ici Cyan)
                        c = "#00ffff"  
                        # On trace une ligne pour éviter les "trous noirs" dus à la vitesse
                        # Épaisseur du tracé
                        tid = self.canvas.create_line(prev_x, prev_y, x, y, fill=c, width=4, capstyle=tk.ROUND)
                        self.pixels_remanents.append({'id': tid, 'vie': 255, 'r': 0, 'g': 255, 'b': 255})
                        
                        if dernier_pas:
                            self.canvas.itemconfig(self.leds_gui[b][i], fill=c)
                            self.canvas.coords(self.leds_gui[b][i], x-3, y-3, x+3, y+3)
                    else:
                        if dernier_pas:
                            # Couleur des LEDs éteintes
                            self.canvas.itemconfig(self.leds_gui[b][i], fill="#111")
                            self.canvas.coords(self.leds_gui[b][i], x-3, y-3, x+3, y+3)
                            
        self.root.after(self.refresh_rate, self.animate)

def lancer_helice_ui(fenetre_parente, donnees=None, duree_sec=10):
    """Fonction d'appel qui gère le Toplevel et ferme la fenêtre à la fin du chrono."""
    top = tk.Toplevel(fenetre_parente)
    app = HelicePOV(top, fichier_initial=donnees)
    top.after(duree_sec * 1000, top.destroy)
    top.wait_window(top)

if __name__ == "__main__":
    root = tk.Tk()
    app = HelicePOV(root)
    root.mainloop()
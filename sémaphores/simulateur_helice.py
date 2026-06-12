import tkinter as tk
import math

# ==========================================
# ÉTAPE 1 : DICTIONNAIRE ET MATRICES DE GLYPHES
# ==========================================
DICTIONNAIRE_LETTRES = {
    "A": [
        [
            (255, 50, 50) if (240 < a < 260 or 280 < a < 300) else
            (255, 50, 50) if (260 <= a <= 280 and 4 <= led <= 5) else
            None
            for led in range(10)
        ]
        for a in range(360)
    ],
    "B": [
        [
            (50, 255, 50) if (260 < a < 280) else
            (50, 255, 50) if (180 < a < 360 and led in [0, 4, 9]) else
            None
            for led in range(10)
        ]
        for a in range(360)
    ],
    "C": [
        [
            (50, 150, 255) if (not (320 < a or a < 40) and led in [8, 9]) else
            None
            for led in range(10)
        ]
        for a in range(360)
    ]
}

class HelicePOV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulateur Hélice Holographique POV")
        self.root.configure(bg="#111")
        
        # --- CONSTANTES PHYSIQUES ---
        self.W, self.H = 600, 600
        self.CX, self.CY = self.W / 2, self.H / 2
        self.ESPACEMENT_LED = 25
        
        # Variables d'état
        self.angle_moteur = 0
        self.pixels_remanents = [] 
        self.lettre_actuelle = "A" 
        self.vitesse = 5           
        self.en_rotation = False
        
        self.matrices_polaires = DICTIONNAIRE_LETTRES
        
        self._creer_interface()
        self._initialiser_matrice_rotation()

    # ==========================================
    # ÉTAPE 4 : INTERFACE GRAPHIQUE
    # ==========================================
    def _creer_interface(self):
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        frame_ctrl = tk.Frame(self.root, bg="#222", padx=20, pady=10)
        frame_ctrl.pack(fill="x")
        
        tk.Label(frame_ctrl, text="Lettre à afficher (A, B, C) :", bg="#222", fg="white").pack(side="left")
        self.entry_lettre = tk.Entry(frame_ctrl, width=5, font=("Arial", 12))
        self.entry_lettre.pack(side="left", padx=10)
        self.entry_lettre.insert(0, "A")
        
        btn_valider = tk.Button(frame_ctrl, text="Valider", command=self.changer_lettre)
        btn_valider.pack(side="left")
        
        tk.Label(frame_ctrl, text="   |   Vitesse de rotation :", bg="#222", fg="white").pack(side="left")
        self.scale_vitesse = tk.Scale(
            frame_ctrl, from_=1, to=40, orient="horizontal", 
            bg="#222", fg="white", length=200, command=self.maj_vitesse
        )
        self.scale_vitesse.set(self.vitesse)
        self.scale_vitesse.pack(side="left", padx=10)

    def changer_lettre(self):
        lettre = self.entry_lettre.get().upper()
        if lettre in self.matrices_polaires:
            self.lettre_actuelle = lettre
        else:
            print(f"La lettre {lettre} n'est pas dans le dictionnaire.")

    def maj_vitesse(self, val):
        self.vitesse = int(val)

    # ==========================================
    # ÉTAPE 2 : MATRICE DE ROTATION (Positions Initiales)
    # ==========================================
    def _initialiser_matrice_rotation(self):
        self.leds_initiales = [] 
        for i in range(10):
            x0 = (i + 1) * self.ESPACEMENT_LED
            y0 = 0
            self.leds_initiales.append((x0, y0))
            
        self.bras_gui = [self.canvas.create_line(0,0,0,0, fill="#333", width=4) for _ in range(4)]
        
        self.leds_gui = []
        for _ in range(4):
            branche = [self.canvas.create_oval(0,0,0,0, fill="#111", outline="#333") for _ in range(10)]
            self.leds_gui.append(branche)

    def demarrer(self):
        if not self.en_rotation:
            self.en_rotation = True
            self._boucle_animation()

    # ==========================================
    # ÉTAPE 3 ET DÉFIS : ROTATION ET RÉMANENCE
    # ==========================================
    def _gerer_remanence(self):
        pixels_restants = []
        for p in self.pixels_remanents:
            p['vie'] -= 15 
            
            if p['vie'] <= 0:
                self.canvas.delete(p['id'])
            else:
                ratio = p['vie'] / 255.0
                r = int(p['r'] * ratio)
                g = int(p['g'] * ratio)
                b = int(p['b'] * ratio)
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                
                self.canvas.itemconfig(p['id'], fill=hex_color, outline=hex_color)
                pixels_restants.append(p)
                
        self.pixels_remanents = pixels_restants

    def _boucle_animation(self):
        self._gerer_remanence()

        self.angle_moteur = (self.angle_moteur + self.vitesse) % 360
        matrice_lettre = self.matrices_polaires[self.lettre_actuelle]

        for num_branche in range(4):
            angle_branche = (self.angle_moteur + num_branche * 90) % 360
            alpha = math.radians(angle_branche)
            
            cos_a = math.cos(alpha)
            sin_a = math.sin(alpha)
            
            x0_bout, y0_bout = 10.5 * self.ESPACEMENT_LED, 0
            x_bout = self.CX + (x0_bout * cos_a - y0_bout * sin_a)
            y_bout = self.CY + (x0_bout * sin_a + y0_bout * cos_a)
            self.canvas.coords(self.bras_gui[num_branche], self.CX, self.CY, x_bout, y_bout)

            leds_etat = matrice_lettre[int(angle_branche)]
            
            for i, (x0, y0) in enumerate(self.leds_initiales):
                x_prime = x0 * cos_a - y0 * sin_a
                y_prime = x0 * sin_a + y0 * cos_a
                
                x_ecran = self.CX + x_prime
                y_ecran = self.CY + y_prime
                
                rayon = 4
                self.canvas.coords(self.leds_gui[num_branche][i], x_ecran-rayon, y_ecran-rayon, x_ecran+rayon, y_ecran+rayon)
                
                couleur_rgb = leds_etat[i]
                if couleur_rgb is not None:
                    r, g, b = couleur_rgb
                    hex_allume = f'#{r:02x}{g:02x}{b:02x}'
                    
                    self.canvas.itemconfig(self.leds_gui[num_branche][i], fill=hex_allume, outline="white")
                    
                    trace_id = self.canvas.create_oval(x_ecran-3, y_ecran-3, x_ecran+3, y_ecran+3, fill=hex_allume, outline="")
                    self.pixels_remanents.append({
                        'id': trace_id, 'vie': 255, 'r': r, 'g': g, 'b': b
                    })
                else:
                    self.canvas.itemconfig(self.leds_gui[num_branche][i], fill="#111", outline="#333")

        self.root.after(20, self._boucle_animation)

# --- Lanceur pour intégration dans mainsemaphore ---
def lancer_helice_ui(fenetre_parente, lettre_initiale="A"):
    top = tk.Toplevel(fenetre_parente)
    app = HelicePOV(top)
    
    if lettre_initiale in app.matrices_polaires:
        app.lettre_actuelle = lettre_initiale
        app.entry_lettre.delete(0, tk.END)
        app.entry_lettre.insert(0, lettre_initiale)
        
    app.demarrer()

# --- Point d'entrée autonome ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HelicePOV(root)
    app.demarrer()
    root.mainloop()
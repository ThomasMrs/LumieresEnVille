import tkinter as tk
from physique.helice import MoteurHelice
from gui.affichage_tkinter import FenetreSimulateur

class Semaphore:
    def __init__(self, id_sema, centre_x, centre_y):
        self.id = id_sema
        self.cx = centre_x
        self.cy = centre_y
        self.moteur = MoteurHelice(vitesse_depart=4.0)
        
        self.en_mission = False
        self.donnees_mission = {}
        self.temps_restant = 0
        
    def recevoir_mission(self, donnees, duree_tics):
        self.donnees_mission = donnees
        self.temps_restant = duree_tics
        self.en_mission = True
        print(f"[{self.id}] Mission recue. Reveil et execution.")
        
    def cloturer_mission(self):
        self.en_mission = False
        self.donnees_mission = {}
        print(f"[{self.id}] Mission terminee. Notification au WS et rendormissement.")

    def mettre_a_jour(self):
        if self.en_mission:
            self.moteur.avancer_un_tic()
            self.temps_restant -= 1
            if self.temps_restant <= 0:
                self.cloturer_mission()

vue = FenetreSimulateur()

liste_semaphores = [
    Semaphore("SEMA_01", 150, 250),
    Semaphore("SEMA_02", 350, 250)
]

forme_en_attente = {}

def ajouter_point_polaire():
    try:
        angle_saisi = int(vue.champ_angle.get())
        rayon_saisi = int(vue.champ_rayon.get())
        
        if rayon_saisi < 0 or rayon_saisi > 10:
            print("Erreur : Le rayon doit etre compris entre 0 et 10.")
            return
            
        angle_arrondi = (angle_saisi // 10) * 10
        
        if angle_arrondi not in forme_en_attente:
            forme_en_attente[angle_arrondi] = []
            
        if rayon_saisi not in forme_en_attente[angle_arrondi]:
            forme_en_attente[angle_arrondi].append(rayon_saisi)
            
        print(f"Point memorise dans la forme : Angle {angle_arrondi}, Rayon {rayon_saisi}")
        
    except ValueError:
        print("Erreur : Entiers requis.")

def envoyer_mission_test():
    for sema in liste_semaphores:
        sema.recevoir_mission(forme_en_attente, 150)

vue.bouton_valider.config(command=ajouter_point_polaire)

bouton_mission = tk.Button(vue.zone_saisie, text="[TEST] Envoyer Mission", command=envoyer_mission_test)
bouton_mission.pack(side=tk.LEFT, padx=10)

def boucle_principale():
    vue.nettoyer_ecran()
    
    for sema in liste_semaphores:
        sema.mettre_a_jour()
        
        if sema.en_mission:
            x1, y1 = sema.moteur.calculer_position_matrice(200, 0, sema.moteur.angle)
            x2, y2 = sema.moteur.calculer_position_matrice(-200, 0, sema.moteur.angle)
            vue.dessiner_barre(sema.cx, sema.cy, x1, y1, x2, y2)
            
            x3, y3 = sema.moteur.calculer_position_matrice(0, 200, sema.moteur.angle)
            x4, y4 = sema.moteur.calculer_position_matrice(0, -200, sema.moteur.angle)
            vue.dessiner_barre(sema.cx, sema.cy, x3, y3, x4, y4)
            
            for i in range(4):
                angle_branche = (sema.moteur.angle + i * 90) % 360
                angle_arrondi = int(angle_branche // 10) * 10
                
                if angle_arrondi in sema.donnees_mission:
                    for rayon in sema.donnees_mission[angle_arrondi]:
                        dist = rayon * 15
                        
                        if i == 0: x0, y0 = dist, 0
                        elif i == 1: x0, y0 = 0, dist
                        elif i == 2: x0, y0 = -dist, 0
                        else: x0, y0 = 0, -dist
                            
                        x_led, y_led = sema.moteur.calculer_position_matrice(x0, y0, sema.moteur.angle)
                        vue.dessiner_led(sema.cx, sema.cy, x_led, y_led, True)
                        
    vue.root.after(20, boucle_principale)

print("Lancement du simulateur")
boucle_principale()
vue.root.mainloop()
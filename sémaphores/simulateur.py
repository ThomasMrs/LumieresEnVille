import tkinter as tk
from physique.helice import MoteurHelice
from gui.affichage_tkinter import FenetreSimulateur

moteur = MoteurHelice(vitesse_depart=4.0)
vue = FenetreSimulateur()

coordonnees_profs = {}

def ajouter_point_polaire():
    try:
        angle_saisi = int(vue.champ_angle.get())
        rayon_saisi = int(vue.champ_rayon.get())
        
        angle_arrondi = (angle_saisi // 10) * 10
        
        if angle_arrondi not in coordonnees_profs:
            coordonnees_profs[angle_arrondi] = []
            
        if rayon_saisi not in coordonnees_profs[angle_arrondi]:
            coordonnees_profs[angle_arrondi].append(rayon_saisi)
            
        vue.canvas.delete("all")
        print(f"Point ajoute : Angle {angle_arrondi}, Rayon {rayon_saisi}")
        
    except ValueError:
        print("Erreur : Entiers requis.")

vue.bouton_valider.config(command=ajouter_point_polaire)

def boucle_principale():
    vue.nettoyer_ecran()
    moteur.avancer_un_tic()
    
    x1, y1 = moteur.obtenir_coordonnees_led(200)
    x2, y2 = moteur.obtenir_coordonnees_led(-200)
    vue.dessiner_barre(x1, y1, x2, y2)
    
    angle_actuel = int(moteur.angle // 10) * 10
    
    if angle_actuel in coordonnees_profs:
        rayons_a_allumer = coordonnees_profs[angle_actuel]
        
        for rayon in rayons_a_allumer:
            x_led, y_led = moteur.obtenir_coordonnees_led(rayon * 15)
            vue.dessiner_led(x_led, y_led, True)
            
    vue.root.after(20, boucle_principale)

print("Lancement du simulateur polaire...")
boucle_principale()
vue.root.mainloop()
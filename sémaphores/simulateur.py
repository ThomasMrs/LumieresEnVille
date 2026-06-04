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
        
        if rayon_saisi < 0 or rayon_saisi > 10:
            print("Erreur : Le rayon doit etre compris entre 0 et 10.")
            return
        if angle_saisi < 0 or angle_saisi >= 360:
            print("Erreur : L'angle doit etre compris entre 0 et 359.")
            return
            
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
    

    x1, y1 = moteur.calculer_position_matrice(200, 0, moteur.angle)
    x2, y2 = moteur.calculer_position_matrice(-200, 0, moteur.angle)
    vue.dessiner_barre(x1, y1, x2, y2)
    
    # Branche verticale à l'arrêt (Haut et Bas)
    x3, y3 = moteur.calculer_position_matrice(0, 200, moteur.angle)
    x4, y4 = moteur.calculer_position_matrice(0, -200, moteur.angle)
    vue.dessiner_barre(x3, y3, x4, y4)
    
    for i in range(4):
        angle_branche = (moteur.angle + i * 90) % 360
        angle_arrondi = int(angle_branche // 10) * 10
        
        if angle_arrondi in coordonnees_profs:
            for rayon in coordonnees_profs[angle_arrondi]:
                dist = rayon * 15
                
                if i == 0:
                    x0, y0 = dist, 0       
                elif i == 1:
                    x0, y0 = 0, dist       
                elif i == 2:
                    x0, y0 = -dist, 0     
                else:
                    x0, y0 = 0, -dist     
                    
                x_led, y_led = moteur.calculer_position_matrice(x0, y0, moteur.angle)
                vue.dessiner_led(x_led, y_led, True)
                
    vue.root.after(20, boucle_principale)

print("Lancement du simulateur Etape 2...")
boucle_principale()
vue.root.mainloop()
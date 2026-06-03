# Fichier : simulateur.py

# On importe nos propres outils depuis nos dossiers !
from modélisation.matrices_glyphes import ALPHABET
from physique.helice import MoteurHelice
from gui.affichage_tkinter import FenetreSimulateur

# 1. PRÉPARATION DES OUTILS
lettre_choisie = ALPHABET["A"]            # On décide de lire la partition de la lettre A
moteur = MoteurHelice(vitesse_depart=4.0) # On crée notre moteur mathématique
vue = FenetreSimulateur()                 # On crée notre fenêtre noire

def boucle_principale():
    """C'est le chef d'orchestre qui bat la mesure (la frame d'animation)"""
    
    # A. On nettoie l'écran (on efface uniquement la barre grise, on laisse la lumière !)
    vue.nettoyer_ecran()
    
    # B. On fait avancer le moteur d'un cran
    moteur.avancer_un_tic()
    
    # C. On dessine le bras physique de l'hélice (du rayon -200 au rayon +200)
    x1, y1 = moteur.obtenir_coordonnees_led(200)
    x2, y2 = moteur.obtenir_coordonnees_led(-200)
    vue.dessiner_barre(x1, y1, x2, y2)
    
    # D. LE CERVEAU : Lecture de la matrice (Version sans déformation !)
    # On décide d'imprimer la lettre uniquement quand l'hélice passe en haut.
    # En trigonométrie, le haut du cercle correspond aux angles entre 220° et 320°.
    if 220 <= moteur.angle < 320:
        
        # On calcule dans quelle colonne (0 à 9) on se trouve dans cette petite fenêtre.
        # (Chaque colonne fait maintenant 10 degrés de large)
        colonne_actuelle = int((moteur.angle - 220) // 10) 
        
        # On vérifie les 10 cases de cette colonne pour savoir quelles LEDs allumer
        for rayon in range(10):
            etat_matrice = lettre_choisie[rayon][colonne_actuelle]
            est_allumee = (etat_matrice == 1)
            
            # On décale les LEDs du centre pour ne pas que le dessin soit tout écrasé au milieu
            x_led, y_led = moteur.obtenir_coordonnees_led((rayon + 5) * 12)
            
            # On donne l'ordre à la Vue de dessiner la LED
            vue.dessiner_led(x_led, y_led, est_allumee)
            
    # E. La boucle temporelle : on se relance dans 20 millisecondes !
    vue.root.after(20, boucle_principale)


# --- LANCEMENT DU PROGRAMME ---
print("Lancement du simulateur...")
boucle_principale()    # On lance le premier battement de mesure
vue.root.mainloop()    # On affiche la fenêtre et on la laisse ouverte

from modélisation.matrices_glyphes import ALPHABET
from physique.helice import MoteurHelice
from gui.affichage_tkinter import FenetreSimulateur

moteur = MoteurHelice(vitesse_depart=4.0)
vue = FenetreSimulateur()

lettre_actuelle = ALPHABET["A"]

def changer_lettre():
    """Se déclenche quand on clique sur le bouton 'Afficher'"""
    global lettre_actuelle
    symbole = vue.champ_lettre.get().upper() 
    
    if symbole in ALPHABET:
        lettre_actuelle = ALPHABET[symbole]
        vue.canvas.delete("all") 
        print(f"Affichage de la lettre : {symbole}")
    else:
        print(f"Erreur : La lettre '{symbole}' n'existe pas dans le dictionnaire.")

vue.bouton_valider.config(command=changer_lettre)

def boucle_principale():
    vue.nettoyer_ecran()
    moteur.avancer_un_tic()
    
    x1, y1 = moteur.obtenir_coordonnees_led(200)
    x2, y2 = moteur.obtenir_coordonnees_led(-200)
    vue.dessiner_barre(x1, y1, x2, y2)
    
    if 220 <= moteur.angle < 320:
        colonne_actuelle = int((moteur.angle - 220) // 10) 
        
        for rayon in range(10):
            if lettre_actuelle[rayon][colonne_actuelle] == 1:
                x_led, y_led = moteur.obtenir_coordonnees_led((rayon + 5) * 12)
                vue.dessiner_led(x_led, y_led, True)
                
    vue.root.after(20, boucle_principale)

print("Lancement du simulateur...")
boucle_principale()
vue.root.mainloop()
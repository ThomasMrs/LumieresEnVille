import tkinter as tk

def creer_grille_vierge(lignes, colonnes):
    grille_memoire = []
    for i in range(lignes):
        grille_memoire.append([0] * colonnes)
    return grille_memoire

def colorier_case(event):
    colonne = event.x // TAILLE_CASE
    ligne = event.y // TAILLE_CASE
    
    memoire[ligne][colonne] = 1
    
    x1 = colonne * TAILLE_CASE
    y1 = ligne * TAILLE_CASE
    x2 = x1 + TAILLE_CASE
    y2 = y1 + TAILLE_CASE
    toile.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")

def exporter_matrice():
    print("=== COORDONNÉES POLAIRES DES PIXELS NOIRS ===")
    
    for ligne in range(LIGNES):
        for colonne in range(COLONNES):
            
            if memoire[ligne][colonne] == 1:
    
                r = ligne
                theta = colonne
                print(f"LED à allumer -> Rayon r={r}, Angle theta={theta}")
                
    print("=============================================")


LIGNES = 10
COLONNES = 10
TAILLE_CASE = 30

memoire = creer_grille_vierge(LIGNES, COLONNES)

fenetre = tk.Tk()
fenetre.title("Mon Usine à Formes")

largeur_ecran = COLONNES * TAILLE_CASE
hauteur_ecran = LIGNES * TAILLE_CASE

toile = tk.Canvas(fenetre, width=largeur_ecran, height=hauteur_ecran, bg="white")
toile.pack() 

for ligne in range(LIGNES):
    for colonne in range(COLONNES):
        x1 = colonne * TAILLE_CASE
        y1 = ligne * TAILLE_CASE
        x2 = x1 + TAILLE_CASE
        y2 = y1 + TAILLE_CASE
        toile.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

toile.bind("<Button-1>", colorier_case)

bouton_export = tk.Button(fenetre, text="Générer les Coordonnées", command=exporter_matrice)
bouton_export.pack()

fenetre.mainloop()
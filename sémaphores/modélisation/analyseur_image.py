import tkinter as tk

# ==========================================
# 1. LES OUTILS (Fonctions)
# ==========================================

def creer_grille_vierge(lignes, colonnes):
    grille_memoire = []
    for i in range(lignes):
        grille_memoire.append([0] * colonnes)
    return grille_memoire

def colorier_case(event):
    # a. On traduit les pixels du clic en Index (0, 1, 2...)
    colonne = event.x // TAILLE_CASE
    ligne = event.y // TAILLE_CASE
    
    # b. Mise à jour de la MÉMOIRE (Le Cerveau)
    memoire[ligne][colonne] = 1
    
    # c. Mise à jour de l'ÉCRAN (Les Yeux)
    x1 = colonne * TAILLE_CASE
    y1 = ligne * TAILLE_CASE
    x2 = x1 + TAILLE_CASE
    y2 = y1 + TAILLE_CASE
    toile.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")

# ==========================================
# 2. LES PARAMÈTRES (Constantes)
# ==========================================
LIGNES = 10
COLONNES = 15
TAILLE_CASE = 30

# ==========================================
# 3. LE PROGRAMME PRINCIPAL
# ==========================================

# Initialisation du cerveau
memoire = creer_grille_vierge(LIGNES, COLONNES)

# Création de la fenêtre
fenetre = tk.Tk()
fenetre.title("Mon Usine à Formes")

largeur_ecran = COLONNES * TAILLE_CASE
hauteur_ecran = LIGNES * TAILLE_CASE

toile = tk.Canvas(fenetre, width=largeur_ecran, height=hauteur_ecran, bg="white")
toile.pack() 

# Dessin du quadrillage de base
for ligne in range(LIGNES):
    for colonne in range(COLONNES):
        x1 = colonne * TAILLE_CASE
        y1 = ligne * TAILLE_CASE
        x2 = x1 + TAILLE_CASE
        y2 = y1 + TAILLE_CASE
        toile.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

# On attache le clic gauche de la souris à notre nouvelle fonction
toile.bind("<Button-1>", colorier_case)

# Lancement du moteur
fenetre.mainloop()
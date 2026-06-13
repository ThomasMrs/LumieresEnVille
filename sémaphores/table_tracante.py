import tkinter as tk
import math
import os

def simuler_table_tracante_csv(nom_fichier, root_parent):
    """Lit un fichier CSV polaire (r;a;s) et le convertit en Cartésien pour affichage"""
    if not os.path.exists(nom_fichier):
        print(f"Erreur Table : Le fichier {nom_fichier} est introuvable.")
        return

    top = tk.Toplevel(root_parent)
    top.title("Simulateur Table Traçante - Rendu Cartésien")
    
    canvas = tk.Canvas(top, width=500, height=500, bg="white")
    canvas.pack(padx=10, pady=10)

    cx, cy = 250, 250  # Centre de la table
    x_prec, y_prec = None, None

    try:
        with open(nom_fichier, "r") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne or ligne.startswith("rayon") or ligne.startswith("Name"):
                    continue
                
                parties = ligne.split(";")
                if len(parties) >= 3:
                    r = float(parties[0])
                    # Conversion de l'angle du CSV en radians pour les fonctions mathématiques
                    a = math.radians(float(parties[1]))
                    stylo = int(parties[2])

                    # Formule de passage Polaire -> Cartésien
                    x = cx + r * math.cos(a)
                    y = cy + r * math.sin(a)

                    # Si le stylo est abaissé (1), on trace la ligne depuis le point précédent
                    if stylo == 1 and x_prec is not None:
                        canvas.create_line(x_prec, y_prec, x, y, fill="black", width=2)

                    x_prec, y_prec = x, y
    except Exception as e:
        print(f"Erreur lors du tracé de la table : {e}")
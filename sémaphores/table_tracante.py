import tkinter as tk
import time
import os

def lire_points_csv(fichier_csv):
    """Lit un fichier CSV et retourne la liste des coordonnées (X, Y)"""
    cibles = []
    try:
        with open(fichier_csv, 'r') as f:
            lignes = f.readlines()
            for ligne in lignes:
                ligne = ligne.strip()
                if not ligne or ';' not in ligne:
                    continue
                parties = ligne.split(';')
                try:
                    cibles.append((float(parties[1]), float(parties[2])))
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"ERREUR : Le fichier {fichier_csv} est introuvable.")
    return cibles

def simuler_table_tracante_csv(fichier_csv, fenetre_parente):
    cibles = lire_points_csv(fichier_csv)
    if not cibles or len(cibles) < 2:
        return

    # 1. Calcul des échelles
    xs = [p[0] for p in cibles]
    ys = [p[1] for p in cibles]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    if max_x == min_x: max_x += 1
    if max_y == min_y: max_y += 1

    W, H = 400, 400
    PAD = 40

    def scale_x(x_val):
        return PAD + (x_val - min_x) / (max_x - min_x) * (W - 2 * PAD)
    
    def scale_y(y_val):
        return H - PAD - (y_val - min_y) / (max_y - min_y) * (H - 2 * PAD)

    # 2. Création de la fenêtre
    top = tk.Toplevel(fenetre_parente)
    top.title(f"Simulation Physique - {os.path.basename(fichier_csv)}")
    top.configure(bg="#2d2d2d")

    cv_draw = tk.Canvas(top, width=W, height=H, bg="white", highlightthickness=2, highlightbackground="blue")
    cv_draw.pack(side=tk.LEFT, padx=10, pady=10)
    cv_draw.create_text(W/2, 15, text="Tracé de la table", fill="black", font=("Arial", 12, "bold"))

    cv_motor = tk.Canvas(top, width=W, height=H, bg="black", highlightthickness=2, highlightbackground="gray")
    cv_motor.pack(side=tk.RIGHT, padx=10, pady=10)
    cv_motor.create_text(W/2, 15, text="Tension Moteurs (Rouge=X, Vert=Y)", fill="white", font=("Arial", 10))
    cv_motor.create_line(PAD, H/2, W-PAD, H/2, fill="gray", dash=(4, 4))

    # 3. Pré-calcul
    PAS = 0.5
    total_etapes = 0
    x_calc, y_calc = cibles[0]
    for tx, ty in cibles[1:]:
        dist_x, dist_y = tx - x_calc, ty - y_calc
        total_etapes += max(int(abs(dist_x) / PAS), int(abs(dist_y) / PAS)) or 1
        x_calc, y_calc = tx, ty

    def scale_t(t_val):
        return PAD + (t_val / total_etapes) * (W - 2 * PAD)
    def scale_m(m_val):
        return H/2 - m_val * 80

    # 4. Animation
    x, y = cibles[0]
    t = 0
    prev_x_draw, prev_y_draw = scale_x(x), scale_y(y)
    prev_t, prev_m1, prev_m2 = scale_t(0), scale_m(0), scale_m(0)

    for tx, ty in cibles[1:]:
        distance_x = tx - x
        distance_y = ty - y
        
        nb_etapes = max(int(abs(distance_x) / PAS), int(abs(distance_y) / PAS))
        if nb_etapes == 0: nb_etapes = 1
            
        pas_x = distance_x / nb_etapes
        pas_y = distance_y / nb_etapes

        for i in range(nb_etapes):
            t += 1
            x += pas_x
            y += pas_y
            
            moteur1 = 1 if pas_x > 0 else (-1 if pas_x < 0 else 0)
            moteur2 = 1 if pas_y > 0 else (-1 if pas_y < 0 else 0)
            
            curr_x_draw, curr_y_draw = scale_x(x), scale_y(y)
            curr_t = scale_t(t)
            curr_m1, curr_m2 = scale_m(moteur1), scale_m(moteur2)

            cv_draw.create_line(prev_x_draw, prev_y_draw, curr_x_draw, curr_y_draw, fill="blue", width=3)
            cv_motor.create_line(prev_t, prev_m1, curr_t, curr_m1, fill="red", width=2)
            cv_motor.create_line(prev_t, prev_m2, curr_t, curr_m2, fill="green", width=2)

            prev_x_draw, prev_y_draw = curr_x_draw, curr_y_draw
            prev_t, prev_m1, prev_m2 = curr_t, curr_m1, curr_m2

            if t % 3 == 0:
                top.update()
                time.sleep(0.01)

    top.update()
    time.sleep(2)
    top.destroy()
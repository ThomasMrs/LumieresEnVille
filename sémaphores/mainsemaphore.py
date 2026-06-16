import threading
import os
import math
import time
import tkinter as tk  
from datetime import datetime 
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None
DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))

def ecrire_csv_temporaire(liste_points, nom_fichier="temp_mission.csv"):
    chemin = os.path.join(DOSSIER_ACTUEL, nom_fichier)
    with open(chemin, 'w') as f:
        f.write("rayon;angle;stylo\n")
        for p in liste_points:
            f.write(f"{p['r']};{p['a']};{p['s']}\n")
    return chemin

def centrer_points_polaires(points):
    if not points: 
        return points
    coords = []
    for p in points:
        x = p['r'] * math.cos(math.radians(p['a']))
        y = p['r'] * math.sin(math.radians(p['a']))
        coords.append({'x': x, 'y': y, 's': p['s']})
    xs = [p['x'] for p in coords]
    ys = [p['y'] for p in coords]
    centre_x = (min(xs) + max(xs)) / 2.0
    centre_y = (min(ys) + max(ys)) / 2.0
    points_centres = []
    for p in coords:
        nx = p['x'] - centre_x
        ny = p['y'] - centre_y
        nouveau_rayon = math.hypot(nx, ny)
        nouvel_angle = math.degrees(math.atan2(ny, nx)) % 360
        points_centres.append({'r': nouveau_rayon, 'a': int(nouvel_angle), 's': p['s']})
    return points_centres

def interpoler_points(points):
    PHASE_SHIFT = 90  
    if len(points) < 2: 
        return points
    points_denses = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)] 
        a1 = (p1['a'] + PHASE_SHIFT) % 360
        a2 = (p2['a'] + PHASE_SHIFT) % 360
        x1 = p1['r'] * math.cos(math.radians(a1))
        y1 = p1['r'] * math.sin(math.radians(a1))
        x2 = p2['r'] * math.cos(math.radians(a2))
        y2 = p2['r'] * math.sin(math.radians(a2))
        distance = math.hypot(x2 - x1, y2 - y1)
        nb_etapes = max(20, int(distance * 2))
        for t in range(nb_etapes):
            fraction = t / float(nb_etapes)
            xt = x1 + fraction * (x2 - x1)
            yt = y1 + fraction * (y2 - y1)
            rt = math.hypot(xt, yt)
            at = (math.degrees(math.atan2(yt, xt)) - PHASE_SHIFT) % 360
            points_denses.append({'r': int(rt), 'a': int(at), 's': 1})
    return points_denses

def lancer_dessin_physique():
    global etat, mission_en_cours
    
    if mission_en_cours is None: 
        return
    
    ui.mettre_a_jour_statut("Préparation du tracé...")
    ui.afficher_forme("") 
    
    m_id = mission_en_cours.get("id")
    shape_id = mission_en_cours.get("shape_id")
    sem = get_semaphore(mission_en_cours.get("semaphore_id"))
    type_sem = sem.get("type", "").lower()

    r = int(mission_en_cours.get("color_r") or 0)
    g = int(mission_en_cours.get("color_g") or 255)
    b = int(mission_en_cours.get("color_b") or 255)
    couleur_mission = (r, g, b)
    
    duree_str = mission_en_cours.get("time")
    try:
        duree_sec = int(duree_str)
    except Exception:
        duree_sec = 10  
    
    shape = get_shape(shape_id)
    
    if shape:
        donnees = shape.get("points") or shape.get("data") or shape.get("image")
        points_bruts = []
        cible_affichage = None
        
        if isinstance(donnees, list):
            for pt in donnees:
                try:
                    r_pt = float(pt.get("r", pt.get("rayon", 0)))
                    a_pt = int(float(pt.get("a", pt.get("angle", 0))))
                    s_pt = int(pt.get("s", pt.get("stylo", 1)))
                    points_bruts.append({"r": r_pt, "a": a_pt, "s": s_pt})
                except Exception:
                    pass
            points_centres = centrer_points_polaires(points_bruts)
            points_finaux = interpoler_points(points_centres)
            cible_affichage = ecrire_csv_temporaire(points_finaux)
            
        elif isinstance(donnees, str) and len(donnees.strip()) < 5:
            cible_affichage = donnees.strip()
            
        elif isinstance(donnees, str):
            points_bruts = decoder_chaine_image(donnees)
            points_centres = centrer_points_polaires(points_bruts)
            points_finaux = interpoler_points(points_centres)
            cible_affichage = ecrire_csv_temporaire(points_finaux)
            
        if cible_affichage:
            if type_sem == "helice":
                lancer_helice_ui(ui.root, cible_affichage, couleur_mission, duree_sec)
            else:
                if cible_affichage.endswith(".csv"):
                    simuler_table_tracante_csv(cible_affichage, ui.root, couleur_mission, duree_sec)
                else:
                    ui.afficher_forme(cible_affichage, couleur_mission)
                    var_attente = tk.IntVar()
                    ui.root.after(duree_sec * 1000, lambda: var_attente.set(1))
                    ui.root.wait_variable(var_attente)
                    ui.afficher_forme("") 
                    
    else:
        ui.mettre_a_jour_statut("ERREUR - Shape introuvable")
    
    put_mission_state(m_id, "Done")
    put_semaphore_state(mission_en_cours.get("semaphore_id"), "Available")
    
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def boucle_automatisation():
    global etat, mission_en_cours
    
    try:
        if not ui.root.winfo_exists():
            return
    except Exception:
        return
    
    if etat == "RECHERCHE_MISSION":
        toutes_les_missions = get_missions()
        missions_valides = []
        for m in toutes_les_missions:
            if isinstance(m, dict) and m.get("state") in ["Pending", "Pending_semaphore"]:
                missions_valides.append(m)
                
        if len(missions_valides) > 0:
            mission_en_cours = missions_valides[0]
            etat = "ATTENTE_DEPART"
            
    elif etat == "ATTENTE_DEPART":
        date_depart_str = mission_en_cours.get("start_date")
        demarrer_maintenant = False
        
        if not date_depart_str: 
            demarrer_maintenant = True
        else:
            try:
                date_depart = datetime.fromisoformat(date_depart_str.replace("Z", ""))
                if datetime.now() >= date_depart:
                    demarrer_maintenant = True
            except Exception:
                demarrer_maintenant = True

        if demarrer_maintenant:
            etat = "IMPRESSION"
            put_semaphore_state(mission_en_cours.get("semaphore_id"), "Occupied")
            lancer_dessin_physique()
        else:
            heure_propre = date_depart_str.replace("T", " à ")
            ui.mettre_a_jour_statut(f"Planifié pour le {heure_propre}")
            
    if ui.root.winfo_exists():
        ui.root.after(3000, boucle_automatisation)

if __name__ == "__main__":
    boucle_automatisation()
    ui.root.mainloop()
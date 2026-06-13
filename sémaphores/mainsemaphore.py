import threading
import os
import math
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

def interpoler_points(points):
    """Transforme les sommets en lignes continues pour l'affichage POV"""
    PHASE_SHIFT = 90  # 
    if len(points) < 2: return points
    
    points_denses = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)] 
        
        a1, a2 = (p1['a'] + PHASE_SHIFT) % 360, (p2['a'] + PHASE_SHIFT) % 360
        x1, y1 = p1['r'] * math.cos(math.radians(a1)), p1['r'] * math.sin(math.radians(a1))
        x2, y2 = p2['r'] * math.cos(math.radians(a2)), p2['r'] * math.sin(math.radians(a2))
        
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(20, int(dist * 2))
        
        for t in range(steps):
            f = t / float(steps)
            xt, yt = x1 + f * (x2 - x1), y1 + f * (y2 - y1)
            rt = math.hypot(xt, yt)
            at = (math.degrees(math.atan2(yt, xt)) - PHASE_SHIFT) % 360
            points_denses.append({'r': int(rt), 'a': int(at), 's': 1})
    return points_denses

def lancer_dessin_physique():
    global etat, mission_en_cours
    mission = mission_en_cours
    if not mission: return
    
    ui.mettre_a_jour_statut("Préparation...")
    shape = get_shape(mission.get("shape_id"))
    sem = get_semaphore(mission.get("semaphore_id"))
    
    points = interpoler_points(decoder_chaine_image(shape.get("image", "")))
    chemin = ecrire_csv_temporaire(points)
    
    if sem.get("type", "").lower() == "helice":
        lancer_helice_ui(ui.root, chemin)
    else:
        simuler_table_tracante_csv(chemin, ui.root)
    
    put_mission_state(mission.get("id"), "Done")
    put_semaphore_state(mission.get("semaphore_id"), "Available")
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def boucle_automatisation():
    global etat
    if etat == "RECHERCHE_MISSION":
        missions = [m for m in get_missions() if m.get("state") in ["Pending", "Pending_semaphore"]]
        if missions:
            global mission_en_cours
            mission_en_cours = missions[0]
            etat = "IMPRESSION"
            put_semaphore_state(mission_en_cours.get("semaphore_id"), "Occupied")
            lancer_dessin_physique()
    ui.root.after(3000, boucle_automatisation)

if __name__ == "__main__":
    boucle_automatisation()
    ui.root.mainloop()
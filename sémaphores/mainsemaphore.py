import threading
import os
import math
import time
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None
DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))

def ecrire_csv_temporaire(liste_points, nom_fichier="temp_mission.csv"):
    """Génère le fichier CSV local à partir des points de l'API"""
    chemin = os.path.join(DOSSIER_ACTUEL, nom_fichier)
    with open(chemin, 'w') as f:
        f.write("rayon;angle;stylo\n")
        for p in liste_points:
            f.write(f"{p['r']};{p['a']};{p['s']}\n")
    return chemin

def interpoler_points(points):
    """
    Crée des points intermédiaires entre les sommets 
    pour avoir une ligne continue sur l'hélice.
    """
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
    """Gère toute la séquence de dessin physique"""
    global etat, mission_en_cours
    
    if mission_en_cours is None: 
        return
    
    ui.mettre_a_jour_statut("Préparation du tracé")
    
    shape = get_shape(mission_en_cours.get("shape_id"))
    sem = get_semaphore(mission_en_cours.get("semaphore_id"))
    
    image_data = shape.get("image", "").strip()
    type_sem = sem.get("type", "").lower()
    
    if "P" in image_data and ";" in image_data:
        ui.afficher_forme("★")
        points_bruts = decoder_chaine_image(image_data)
        # L'helice (POV) a besoin de points tres denses pour allumer les LED a chaque angle ;
        # la table tracante, elle, relie deja les sommets par des droites -> on lui passe les points bruts.
        if type_sem == "helice":
            cible_affichage = ecrire_csv_temporaire(interpoler_points(points_bruts))
        else:
            cible_affichage = ecrire_csv_temporaire(points_bruts)
    else:
        cible_affichage = image_data
        ui.afficher_forme(cible_affichage)

    if type_sem == "helice":
        lancer_helice_ui(ui.root, cible_affichage)
    elif cible_affichage.endswith(".csv"):
        simuler_table_tracante_csv(cible_affichage, ui.root)
    
    put_mission_state(mission_en_cours.get("id"), "Done")
    put_semaphore_state(mission_en_cours.get("semaphore_id"), "Available")
    
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def boucle_automatisation():
    """Boucle principale qui interroge l'API régulièrement"""
    global etat, mission_en_cours
    
    if etat == "RECHERCHE_MISSION":
        toutes_les_missions = get_missions()
        
        missions_valides = []
        for m in toutes_les_missions:
            if m.get("state") in ["Pending", "Pending_semaphore"]:
                missions_valides.append(m)
                
        if len(missions_valides) > 0:
            mission_en_cours = missions_valides[0]
            etat = "IMPRESSION"
            
            put_semaphore_state(mission_en_cours.get("semaphore_id"), "Occupied")
            lancer_dessin_physique()
            
    ui.root.after(3000, boucle_automatisation)

if __name__ == "__main__":
    boucle_automatisation()
    ui.root.mainloop()
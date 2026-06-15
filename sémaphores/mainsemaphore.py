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
    """Gère la séquence de dessin en lisant la liste JSON des points dans la shape"""
    global etat, mission_en_cours
    
    if mission_en_cours is None: 
        return
    
    ui.mettre_a_jour_statut("Préparation du tracé...")
    ui.afficher_forme("") 
    
    m_id = mission_en_cours.get("id")
    shape_id = mission_en_cours.get("shape_id")
    sem = get_semaphore(mission_en_cours.get("semaphore_id"))
    type_sem = sem.get("type", "").lower()
    
    shape = get_shape(shape_id)
    
    if shape:
        
        donnees = shape.get("points") or shape.get("data") or shape.get("image")
        
        points_bruts = []
        cible_affichage = None
        
        if isinstance(donnees, list):
            for pt in donnees:
                try:
                    r = float(pt.get("r", pt.get("rayon", 0)))
                    a = int(float(pt.get("a", pt.get("angle", 0))))
                    s = int(pt.get("s", pt.get("stylo", 1)))
                    points_bruts.append({"r": r, "a": a, "s": s})
                except Exception as e:
                    print("Erreur de lecture sur un point :", pt)
            
            points_finaux = interpoler_points(points_bruts)
            cible_affichage = ecrire_csv_temporaire(points_finaux)
            
        # CAS 2 : Si c'est juste une lettre ASCII (ex: "A")
        elif isinstance(donnees, str) and len(donnees.strip()) < 5:
            cible_affichage = donnees.strip()
            ui.afficher_forme(cible_affichage)
            
        # CAS 3 : Fallback si c'est encore l'ancien format texte
        elif isinstance(donnees, str):
            points_bruts = decoder_chaine_image(donnees)
            points_finaux = interpoler_points(points_bruts)
            cible_affichage = ecrire_csv_temporaire(points_finaux)
        # -----------------------------------
            
        # Lancement du simulateur
        if cible_affichage:
            if type_sem == "helice":
                lancer_helice_ui(ui.root, cible_affichage)
            else:
                if cible_affichage.endswith(".csv"):
                    simuler_table_tracante_csv(cible_affichage, ui.root)
                    
    else:
        print(f"Erreur : Impossible de récupérer la Shape {shape_id}")
        ui.mettre_a_jour_statut("ERREUR - Shape introuvable")
    
    put_mission_state(m_id, "Done")
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
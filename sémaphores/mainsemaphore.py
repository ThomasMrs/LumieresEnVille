import threading
import os
import math
import time
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

# --- Initialisation des variables globales ---
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
    PHASE_SHIFT = 90  # Permet de recadrer l'image si elle est tournée
    
    if len(points) < 2: 
        return points
    
    points_denses = []
    
    # On relie chaque point au suivant
    for i in range(len(points)):
        p1 = points[i]
        # Le modulo permet de relier le dernier point au premier
        p2 = points[(i + 1) % len(points)] 
        
        # On décale l'angle avec le PHASE_SHIFT
        a1 = (p1['a'] + PHASE_SHIFT) % 360
        a2 = (p2['a'] + PHASE_SHIFT) % 360
        
        # Conversion polaire vers cartésien pour pouvoir tracer la ligne droite
        x1 = p1['r'] * math.cos(math.radians(a1))
        y1 = p1['r'] * math.sin(math.radians(a1))
        x2 = p2['r'] * math.cos(math.radians(a2))
        y2 = p2['r'] * math.sin(math.radians(a2))
        
        # Calcul de la distance avec Pythagore pour savoir combien de points insérer
        distance = math.hypot(x2 - x1, y2 - y1)
        nb_etapes = max(20, int(distance * 2))
        
        # On calcule les coordonnées de chaque point intermédiaire
        for t in range(nb_etapes):
            fraction = t / float(nb_etapes)
            xt = x1 + fraction * (x2 - x1)
            yt = y1 + fraction * (y2 - y1)
            
            # On repasse en polaire (rayon et angle)
            rt = math.hypot(xt, yt)
            at = (math.degrees(math.atan2(yt, xt)) - PHASE_SHIFT) % 360
            
            points_denses.append({'r': int(rt), 'a': int(at), 's': 1})
            
    return points_denses

def lancer_dessin_physique():
    """Gère toute la séquence de dessin physique"""
    global etat, mission_en_cours
    
    if mission_en_cours is None: 
        return
    
    ui.mettre_a_jour_statut("Préparation du tracé...")
    
    # Récupération des données serveur
    shape = get_shape(mission_en_cours.get("shape_id"))
    sem = get_semaphore(mission_en_cours.get("semaphore_id"))
    
    # Décodage et interpolation
    points_bruts = decoder_chaine_image(shape.get("image", ""))
    points_finaux = interpoler_points(points_bruts)
    
    # Création du fichier physique
    chemin = ecrire_csv_temporaire(points_finaux)
    
    # Lancement du bon simulateur en fonction du type
    type_sem = sem.get("type", "").lower()
    if type_sem == "helice":
        lancer_helice_ui(ui.root, chemin)
    else:
        simuler_table_tracante_csv(chemin, ui.root)
    
    # On clôture la mission côté serveur
    put_mission_state(mission_en_cours.get("id"), "Done")
    put_semaphore_state(mission_en_cours.get("semaphore_id"), "Available")
    
    # On réinitialise pour la prochaine mission
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def boucle_automatisation():
    """Boucle principale qui interroge l'API régulièrement"""
    global etat, mission_en_cours
    
    if etat == "RECHERCHE_MISSION":
        toutes_les_missions = get_missions()
        
        # On filtre pour ne garder que les missions qui nous concernent
        missions_valides = []
        for m in toutes_les_missions:
            if m.get("state") in ["Pending", "Pending_semaphore"]:
                missions_valides.append(m)
                
        if len(missions_valides) > 0:
            mission_en_cours = missions_valides[0]
            etat = "IMPRESSION"
            
            # On dit au serveur qu'on est occupé
            put_semaphore_state(mission_en_cours.get("semaphore_id"), "Occupied")
            lancer_dessin_physique()
            
    # On relance la fonction dans 3 secondes
    ui.root.after(3000, boucle_automatisation)

# --- Point d'entrée du programme ---
if __name__ == "__main__":
    # Lancement de la boucle asynchrone
    boucle_automatisation()
    # Lancement de l'interface Tkinter
    ui.root.mainloop()
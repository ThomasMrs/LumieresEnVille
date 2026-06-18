import os
import math
import tkinter as tk
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

# Variables et initialisation
ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None
DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))

# Fonctions géométriques et traitement points

# Nom du fichier temporaire
def ecrire_csv_temporaire(liste_points, nom_fichier="temp_mission.csv"):
    """Crée un fichier local temporaire pour que les simulateurs puissent le lire."""
    chemin = os.path.join(DOSSIER_ACTUEL, nom_fichier)
    with open(chemin, 'w') as f:
        f.write("rayon;angle;stylo\n")
        for p in liste_points:
            f.write(f"{p['r']};{p['a']};{p['s']}\n")
    return chemin

def centrer_points_polaires(points):
    """Recherche le barycentre de la forme et décale tous les points pour la centrer sur le repère."""
    if not points: 
        return points

    # Conversion temporaire en cartésien pour calculer le centre
    coords = []
    for p in points:
        x = p['r'] * math.cos(math.radians(p['a']))
        y = p['r'] * math.sin(math.radians(p['a']))
        coords.append({'x': x, 'y': y, 's': p['s']})

    xs = [p['x'] for p in coords]
    ys = [p['y'] for p in coords]
    centre_x = (min(xs) + max(xs)) / 2.0
    centre_y = (min(ys) + max(ys)) / 2.0

    # Décalage des points et reconversion en polaire
    points_centres = []
    for p in coords:
        nx = p['x'] - centre_x
        ny = p['y'] - centre_y
        
        nouveau_rayon = math.hypot(nx, ny)
        nouvel_angle = math.degrees(math.atan2(ny, nx)) % 360
        points_centres.append({'r': nouveau_rayon, 'a': int(nouvel_angle), 's': p['s']})

    return points_centres

def interpoler_points(points):
    """Calcule des points intermédiaires pour lisser le tracé entre deux sommets éloignés."""
    # [TAG_ROTATION] - Pour pivoter le dessin entier de 90 ou 180 degrés
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
        # [TAG_LISSAGE] - Densité des points pour fluidifier le moteur
        nb_etapes = max(20, int(distance * 2))
        
        for t in range(nb_etapes):
            fraction = t / float(nb_etapes)
            xt = x1 + fraction * (x2 - x1)
            yt = y1 + fraction * (y2 - y1)
            
            rt = math.hypot(xt, yt)
            at = (math.degrees(math.atan2(yt, xt)) - PHASE_SHIFT) % 360
            points_denses.append({'r': int(rt), 'a': int(at), 's': 1})
            
    return points_denses

# Boucle principale

def lancer_dessin_physique():
    # ... (code inchangé)
    pass 

def boucle_automatisation():
    """Tourne en fond pour regarder les nouvelles missions en mode Pending."""
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
            
            # [TAG_DATE] - Vérification de l'heure de départ de la mission
            if datetime.now() >= date_depart:
                etat = "IMPRESSION"
                put_semaphore_state(mission_en_cours.get("semaphore_id"), "Occupied")
                lancer_dessin_physique()
            
    # Relance la boucle toutes les 3 secondes via Tkinter
    if ui.root.winfo_exists():
        # [TAG_SCAN_RESEAU] - Fréquence d'interrogation de l'API (en ms)
        ui.root.after(3000, boucle_automatisation)

if __name__ == "__main__":
    boucle_automatisation()
    ui.root.mainloop()
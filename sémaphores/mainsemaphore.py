import threading
import time
from api_client import *
from gui import Interface

# Initialisation
ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None

def lancer_dessin_physique():
    """Exécute le dessin sans bloquer l'interface."""
    global etat, mission_en_cours
    
    shape_id = mission_en_cours.get("shape_id")
    ui.afficher_forme(shape_id)
    ui.mettre_a_jour_statut(f"Impression : {mission_en_cours.get('name')}")
    ui.mettre_a_jour_details(f"Forme {shape_id} en cours...")
    
    # --- Code de pilotage matériel ici ---
    time.sleep(5) 
    
    # Clôture
    put_mission_state(mission_en_cours.get("id"), "Done")
    put_semaphore(mission_en_cours.get("semaphore_id"), "Awaiting")
    
    ui.mettre_a_jour_details("Mission terminée, ressource libérée.")
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def choisir_mission(mission):
    global etat, mission_en_cours
    mission_en_cours = mission
    put_semaphore(mission_en_cours.get("semaphore_id"), "Occupied")
    etat = "ATTENTE_ROBOT"

def boucle():
    global etat, mission_en_cours
    
    if etat == "RECHERCHE_MISSION":
        ui.mettre_a_jour_statut("État : Recherche")
        missions = get_missions()
        # Filtre conforme à l'étape 8
        missions_pretes = [m for m in missions if m.get("state") == "Pending_semaphore"]
        
        if missions_pretes:
            ui.afficher_missions(missions_pretes, choisir_mission)
            etat = "CHOIX_MISSION"
        else:
            ui.mettre_a_jour_details("En attente de mission...")
            
    elif etat == "ATTENTE_ROBOT":
        ui.mettre_a_jour_details(f"Robot attendu pour {mission_en_cours.get('name')}...")
        # Vérifie si le robot est arrivé (Étape 6 du diagramme)
        if get_robot(mission_en_cours.get("robot_id")):
            etat = "IMPRESSION"
            threading.Thread(target=lancer_dessin_physique, daemon=True).start()
            
    ui.root.after(1000, boucle)

boucle()
ui.root.mainloop()
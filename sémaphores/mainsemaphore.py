import threading
import time
import os
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv

ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None

def lancer_dessin_physique():
    global etat, mission_en_cours
    mission = mission_en_cours
    if not mission: return
    
    # Récupération du nom réel de la forme depuis l'API
    shape_data = get_shape(mission.get("shape_id"))
    shape_name = shape_data.get("name", "Inconnu")
    
    ui.afficher_forme(shape_name)
    ui.mettre_a_jour_statut(f"Impression : {mission.get('name')}")
    ui.mettre_a_jour_details("Simulation table traçante...")
    
    # Chemin absolu sécurisé pour trouver le fichier CSV
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier_actuel, "etoile-symbole (1).csv")
    
    # Lancement de la simulation physique 100% Tkinter
    simuler_table_tracante_csv(chemin_csv, ui.root) 
    
    # Clôture de la mission et libération de la ressource
    put_mission_state(mission.get("id"), "Done")
    put_semaphore(mission.get("semaphore_id"), "AVAILABLE")
    
    ui.mettre_a_jour_details("Mission terminée.")
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def choisir_mission(mission):
    global etat, mission_en_cours
    mission_en_cours = mission
    
    put_semaphore(mission_en_cours.get("semaphore_id"), "OCCUPIED")
    etat = "IMPRESSION"
    
    threading.Thread(target=lancer_dessin_physique, daemon=True).start()

def boucle():
    global etat
    if etat == "RECHERCHE_MISSION":
        ui.mettre_a_jour_statut("État : Recherche")
        missions = get_missions()
        
        missions_pretes = [m for m in missions if m.get("state") in ["Awaiting", "Pending_semaphore"]]
        
        if missions_pretes:
            ui.afficher_missions(missions_pretes, choisir_mission)
            etat = "CHOIX_MISSION"
        else:
            ui.mettre_a_jour_details("En attente de mission...")
            
    ui.root.after(1000, boucle)

boucle()
ui.root.mainloop()
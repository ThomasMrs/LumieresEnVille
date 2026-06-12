import threading
import time
import os
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None

def lancer_table_locale():
    nom_fichier = "etoile-symbole (1).csv" 
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier_actuel, nom_fichier)
    
    ui.mettre_a_jour_statut("Test Manuel : Table Traçante")
    ui.mettre_a_jour_details(f"Fichier : {nom_fichier}")
    ui.afficher_forme("✒️")
    
    if os.path.exists(chemin_csv):
        threading.Thread(target=lambda: simuler_table_tracante_csv(chemin_csv, ui.root), daemon=True).start()
    else:
        print(f"ERREUR : Fichier {nom_fichier} introuvable.")

def lancer_helice_locale():
    ui.mettre_a_jour_statut("Test Manuel : Hélice LED")
    ui.mettre_a_jour_details("Interface POV (Cahier des charges)")
    ui.afficher_forme("🌀")
    
    lancer_helice_ui(ui.root, "A")

ui.set_commande_table(lancer_table_locale)
ui.set_commande_helice(lancer_helice_locale)

def lancer_dessin_physique():
    global etat, mission_en_cours
    mission = mission_en_cours
    if not mission: return
    
    shape_data = get_shape(mission.get("shape_id"))
    shape_name = shape_data.get("name", "Inconnu")
    symbole_ascii = shape_data.get("image", "?")
    
    ui.afficher_forme(symbole_ascii)
    ui.mettre_a_jour_statut(f"Mission API : {mission.get('name')}")
    ui.mettre_a_jour_details(f"Forme : {shape_name}")
    
    nom_propre = shape_name.strip().lower()
    fichier_csv = "default.csv"
    type_machine = "table"
    lettre_pov = "A"
    
    if "lettre b" in nom_propre:
        type_machine = "helice"
        lettre_pov = "B"
    elif "lettre c" in nom_propre:
        type_machine = "helice"
        lettre_pov = "C"
    elif "lettre a" in nom_propre:
        type_machine = "helice"
        lettre_pov = "A"
    elif "etoile" in nom_propre:
        fichier_csv = "etoile-symbole (1).csv"
        type_machine = "table"
        
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier_actuel, fichier_csv)
    
    if type_machine == "helice":
        lancer_helice_ui(ui.root, lettre_pov)
    else:
        if os.path.exists(chemin_csv):
            simuler_table_tracante_csv(chemin_csv, ui.root)
        else:
            print(f"DEBUG : Fichier {fichier_csv} introuvable pour la table.")
            time.sleep(2)
    
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
        ui.mettre_a_jour_statut("État : Écoute du Serveur")
        missions = get_missions()
        missions_pretes = [m for m in missions if m.get("state") in ["Awaiting", "Pending_semaphore"]]
        if missions_pretes:
            ui.afficher_missions(missions_pretes, choisir_mission)
            etat = "CHOIX_MISSION"
        else:
            ui.mettre_a_jour_details("En attente de mission API...")
    ui.root.after(1000, boucle)

boucle()
ui.root.mainloop()
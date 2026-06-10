import tkinter as tk
import requests
import time

URL_BASE = "http://192.168.1.14:8000/api"

etat_actuel = "RECHERCHE_MISSION"
mission_en_cours = None
current_semaphore_id = None
current_robot_id = None
temps_fin_impression = 0
formes = {}

fenetre = tk.Tk()
fenetre.title("Sémaphore - Automatique Global")
canvas = tk.Canvas(fenetre, width=500, height=500, bg="black")
canvas.pack(padx=20, pady=20)

texte_statut = canvas.create_text(250, 30, text="Statut : Démarrage", fill="white", font=("Arial", 12))
texte_mission = canvas.create_text(250, 60, text="", fill="yellow", font=("Arial", 10))
texte_symbole = canvas.create_text(250, 250, text="", fill="lime", font=("Courier", 100, "bold"))

try:
    req = requests.get(f"{URL_BASE}/list_shapes", timeout=2)
    for f in req.json():
        formes[f["id"]] = f["image"]
except:
    print("Erreur réseau : Impossible de charger la liste des formes au démarrage.")


def update_semaphore(id_semaphore, nouveau_statut):
    """ Fait un PUT pour changer le statut du sémaphore de la mission """
    try:
        url = f"{URL_BASE}/update_semaphore/{id_semaphore}"
        req = requests.put(url, json={"State": nouveau_statut}, timeout=1.5)
        return req.status_code == 200
    except:
        return False

def verifier_robot(id_robot):
    """ Fait un GET pour vérifier si le robot associé est arrivé """
    try:
        url = f"{URL_BASE}/robot/{id_robot}"
        req = requests.get(url, timeout=1.5)
        donnees_robot = req.json()
        return donnees_robot.get("status") == "arrived" or donnees_robot.get("at_destination") == True
    except:
        return False


def automate():
    global etat_actuel, mission_en_cours, current_semaphore_id, current_robot_id, temps_fin_impression
    
    canvas.itemconfig(texte_statut, text=f"Statut : {etat_actuel}")
    
    if etat_actuel == "RECHERCHE_MISSION":
        try:
            req = requests.get(f"{URL_BASE}/list_missions", timeout=1.5)
            for m in req.json():
                if m.get("state") == "Pending":
                    mission_en_cours = m
                    
                    current_semaphore_id = m.get("semaphore_id")
                    current_robot_id = m.get("robot_id", "default_robot") 
                    
                    canvas.itemconfig(texte_mission, text=f"Mission : {m.get('name')} (Sem: {current_semaphore_id[:8]}...)")
                    etat_actuel = "ATTENTE_ROBOT"
                    break
        except:
            pass

    elif etat_actuel == "ATTENTE_ROBOT":
        if verifier_robot(current_robot_id):
            etat_actuel = "LOCK_SEMAPHORE"

    elif etat_actuel == "LOCK_SEMAPHORE":
        if update_semaphore(current_semaphore_id, "Occupied"):
            duree_mission = float(mission_en_cours.get("time", 5)) 
            temps_fin_impression = time.time() + duree_mission
            
            symbole_a_afficher = formes.get(mission_en_cours.get("shape_id"), "?")
            canvas.itemconfig(texte_symbole, text=symbole_a_afficher)
            
            etat_actuel = "IMPRESSION"

    elif etat_actuel == "IMPRESSION":
        if time.time() >= temps_fin_impression:
            canvas.itemconfig(texte_symbole, text="") 
            canvas.itemconfig(texte_mission, text="")  
            etat_actuel = "UNLOCK_SEMAPHORE"

    elif etat_actuel == "UNLOCK_SEMAPHORE":
        if update_semaphore(current_semaphore_id, "Available"):
            mission_en_cours = None
            current_semaphore_id = None
            current_robot_id = None
            etat_actuel = "RECHERCHE_MISSION"

    fenetre.after(1000, automate)

fenetre.after(1000, automate)
fenetre.mainloop()
import threading
import os
from api_client import *
from gui import Interface
from table_tracante import simuler_table_tracante_csv
from simulateur_helice import lancer_helice_ui

# --- Initialisation de l'IHM ---
ui = Interface()
etat = "RECHERCHE_MISSION"
mission_en_cours = None

DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))

def ecrire_csv_temporaire(liste_points, nom_fichier="temp_mission.csv"):
    chemin = os.path.join(DOSSIER_ACTUEL, nom_fichier)
    try:
        with open(chemin, 'w') as f:
            f.write("rayon;angle;stylo\n")
            for p in liste_points:
                f.write(f"{p['r']};{p['a']};{p['s']}\n")
    except Exception as e:
        print(f"Erreur lors de la création du CSV temporaire : {e}")
    return chemin

def lancer_dessin_physique():
    global etat, mission_en_cours
    mission = mission_en_cours
    if not mission: return
    
    # 1. Le sémaphore annonce qu'il commence le travail
    ui.mettre_a_jour_statut("Téléchargement de la forme...")
    put_mission_state(mission.get("id"), "In progress") # Statut exigé par le serveur
    
    # 2. Requête API
    shape_data = get_shape(mission.get("shape_id"))
    nom_forme = shape_data.get("name", "inconnu").lower()
    chaine_image = shape_data.get("image", "")
    
    liste_points = decoder_chaine_image(chaine_image)
    ui.mettre_a_jour_statut(f"Exécution : {nom_forme}")
    chemin_csv = ecrire_csv_temporaire(liste_points)
    
    # 3. Exécution mécanique (on bloque jusqu'à ce que la fenêtre se ferme)
    if "helice" in nom_forme:
        lancer_helice_ui(ui.root, chemin_csv)
    else:
        simuler_table_tracante_csv(chemin_csv, ui.root)
    
    # 4. Le sémaphore a fini ! Il clôture tout proprement
    put_mission_state(mission.get("id"), "Done")
    put_semaphore_state(mission.get("semaphore_id"), "Available")
    
    ui.mettre_a_jour_statut("En attente de mission...")
    etat = "RECHERCHE_MISSION"
    mission_en_cours = None

def choisir_mission(mission):
    global etat, mission_en_cours
    mission_en_cours = mission
    etat = "IMPRESSION"
    
    # Le robot aurait dû le mettre en Occupied, mais on s'en assure ici au cas où
    put_semaphore_state(mission.get("semaphore_id"), "Occupied")
    
    threading.Thread(target=lancer_dessin_physique, daemon=True).start()

def boucle_automatisation():
    global etat
    if etat == "RECHERCHE_MISSION":
        missions = get_missions()
        
        
        missions_pretes = [m for m in missions if m.get("state") in ["Pending", "Pending_semaphore"]]        
        if missions_pretes:
            ui.afficher_missions(missions_pretes, choisir_mission)
            etat = "CHOIX_MISSION"
            
    ui.root.after(3000, boucle_automatisation)

# ==========================================
# TESTS MANUELS (Pour le jury)
# ==========================================
def lancer_table_locale():
    chemin = os.path.join(DOSSIER_ACTUEL, "test_ligne.csv")
    ui.mettre_a_jour_statut("Test Manuel : Table")
    threading.Thread(target=lambda: simuler_table_tracante_csv(chemin, ui.root), daemon=True).start()

def lancer_helice_locale():
    chemin = os.path.join(DOSSIER_ACTUEL, "test_ligne.csv")
    ui.mettre_a_jour_statut("Test Manuel : Hélice")
    lancer_helice_ui(ui.root, chemin)

ui.set_commande_table(lancer_table_locale)
ui.set_commande_helice(lancer_helice_locale)

if __name__ == "__main__":
    boucle_automatisation()
    ui.root.mainloop()
from serveur.tests.stockage import lire_missions

def valider_nouvelle_mission(name, time, semaphore_id, team_id, symbole, mission_id):
    missions = lire_missions()
    
    mission_trouvee = None
    
    for mission_selectionner in missions:
        if mission_selectionner["id"] == mission_id:
            mission_trouvee = mission_selectionner
            break                              
    
    if not mission_trouvee:
        return {"succes": False, "message": "Erreur : Mission introuvable."}
    
    if mission_trouvee["state"] == "Done":
        return {"succes": False, "message": "Erreur : La mission est déjà finie."}
        
    return {"succes": True, "message": "La mission est valide !"}
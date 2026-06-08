import tkinter as tk
import requests

URL_SERVEUR = "http://192.168.1.100:8000/api/list_missions"
ID_SEMAPHORE = "SEMA_01"

root = tk.Tk()
root.title(f"Test Afficheur Pur - {ID_SEMAPHORE}")
canvas = tk.Canvas(root, width=500, height=500, bg="black")
canvas.pack(padx=20, pady=20)

cx = 250
cy = 250

def executer_afficheur(symbole):
    """Affiche juste le texte en gros et en vert au centre"""
    canvas.delete("all")
    canvas.create_text(cx, cy, text=symbole, fill="lime green", font=("Courier", 100, "bold"))
    print(f"[{ID_SEMAPHORE}] Affichage du texte '{symbole}' pendant 5 secondes.")
    
    root.after(5000, rendormir_semaphore)

def rendormir_semaphore():
    canvas.delete("all")
    print(f"[{ID_SEMAPHORE}] Mission terminée. Retour au sommeil...")
    surveiller_reseau()

def surveiller_reseau():
    print(f"[{ID_SEMAPHORE}] Zzz... Attente d'un signal du Web Service...")
    try:
        reponse = requests.get(URL_SERVEUR, timeout=2)
        
        if reponse.status_code == 200:
            liste_missions = reponse.json()
            mission_trouvee = False
            
            if isinstance(liste_missions, list):
                for mission in liste_missions:
                    cible = mission.get("id_semaphore") or mission.get("id")
                    
                    if cible == ID_SEMAPHORE:
                        statut = mission.get("statut")
                        
                        if statut in ["ALLUME", "OCCUPE", "EN_COURS"]:
                            symbole = mission.get("symbole", "?")
                            print(f"Déclenchement détecté ! Symbole à afficher : {symbole}")
                            
                            executer_afficheur(symbole)
                            mission_trouvee = True
                            break
            
            if not mission_trouvee:
                root.after(3000, surveiller_reseau)
                
    except requests.exceptions.ConnectionError:
        print("Serveur injoignable, nouvelle tentative dans 3 secondes...")
        root.after(3000, surveiller_reseau)

surveiller_reseau()
root.mainloop()
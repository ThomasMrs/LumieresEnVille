import tkinter as tk
import requests

URL_SERVEUR = "http://192.168.1.100:8000/api/list_missions"
ID_SEMAPHORE = "S-102"

root = tk.Tk()
root.title(f"Sémaphore - {ID_SEMAPHORE}")
canvas = tk.Canvas(root, width=500, height=500, bg="black")
canvas.pack(padx=20, pady=20)

def afficher_forme(symbole):
    canvas.delete("all")
    canvas.create_text(250, 250, text=symbole, fill="lime", font=("Courier", 100, "bold"))
    print(f"[{ID_SEMAPHORE}] Affichage : {symbole}")
    root.after(5000, lambda: canvas.delete("all"))

def choisir_et_lancer():
    try:
        reponse = requests.get(URL_SERVEUR, timeout=2)
        if reponse.status_code == 200:
            missions = reponse.json()
            disponibles = [m for m in missions if m.get("semaphore_id") == ID_SEMAPHORE]
            
            print("\n--- Missions disponibles pour S-102 ---")
            for i, m in enumerate(disponibles):
                print(f"{i+1} - Forme: {m.get('shape_id')} | État: {m.get('state')}")
            
            choix = input("Choisis le numéro de la mission à afficher : ")
            
            try:
                idx = int(choix) - 1
                if 0 <= idx < len(disponibles):
                    forme = disponibles[idx].get("shape_id")
                    afficher_forme(forme)
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Entrée invalide.")
                
    except requests.exceptions.RequestException:
        print("Erreur de connexion au serveur.")
    
    root.after(2000, choisir_et_lancer)

# Lancement
root.after(1000, choisir_et_lancer)
root.mainloop()
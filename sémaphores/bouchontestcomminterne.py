import tkinter as tk
import requests

api_missions = "http://192.168.1.100:8000/api/list_missions"
api_formes = "http://192.168.1.100:8000/api/list_shapes"

formes = {}

fenetre = tk.Tk()
fenetre.title("Sema - Toutes les missions")
canvas = tk.Canvas(fenetre, width=500, height=500, bg="black")
canvas.pack(padx=20, pady=20)

try:
    req = requests.get(api_formes, timeout=2)
    for f in req.json():
        formes[f["id"]] = f["image"]
except:
    pass

def afficher(symbole):
    canvas.delete("all")
    canvas.create_text(250, 250, text=symbole, fill="lime", font=("Courier", 100, "bold"))
    print(f"-> Affichage de : {symbole}")
    fenetre.after(5000, lambda: canvas.delete("all"))

def boucle_principale():
    try:
        req = requests.get(api_missions, timeout=2)
        mes_missions = req.json()
        
        print("\n--- Liste de TOUTES les missions ---")
        for i, m in enumerate(mes_missions):
            symb = formes.get(m["shape_id"], "?")
            sem_id = m.get("semaphore_id", "Inconnu")[:8]
            
            print(f"{i+1} - {m.get('name', 'Sans nom')} | Sem: {sem_id}... | {m.get('state', 'N/A')} | {symb}")
        
        choix = input("Choix (numero) : ")
        
        try:
            index = int(choix) - 1
            if index >= 0 and index < len(mes_missions):
                afficher(formes.get(mes_missions[index]["shape_id"], "?"))
            else:
                print("Numero hors liste.")
        except:
            print("Erreur de saisie.")
            
    except:
        print("Erreur serveur...")
    
    fenetre.after(2000, boucle_principale)

fenetre.after(1000, boucle_principale)
fenetre.mainloop()
import tkinter as tk
import requests

api_missions = "http://192.168.1.100:8000/api/list_missions"
api_formes = "http://192.168.1.100:8000/api/list_shapes"
mon_id = "c4e95c86-d916-4477-9f44-1c3ac8c64e98"

formes = {}

fenetre = tk.Tk()
fenetre.title("Sema - " + mon_id)
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
        mes_missions = [m for m in req.json() if m["semaphore_id"] == mon_id]
        
        print("\n--- Liste des missions ---")
        for i, m in enumerate(mes_missions):
            symb = formes.get(m["shape_id"], "?")
            print(f"{i+1} - {m['name']} | {m['state']} | {symb}")
        
        choix = input("Choix (numero) : ")
        
        try:
            index = int(choix) - 1
            if index >= 0:
                afficher(formes.get(mes_missions[index]["shape_id"], "?"))
        except:
            print("Erreur de saisie.")
            
    except:
        print("Erreur serveur...")
    
    fenetre.after(2000, boucle_principale)

fenetre.after(1000, boucle_principale)
fenetre.mainloop()
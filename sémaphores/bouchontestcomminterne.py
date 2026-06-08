import tkinter as tk
import requests
import time

URL_SERVEUR = "http://192.168.1.100:8000/api/list_missions"
ID_SEMAPHORE = "S-102"

root = tk.Tk()
root.title(f"Semaphore - {ID_SEMAPHORE}")
canvas = tk.Canvas(root, width=500, height=500, bg="black")
canvas.pack()

def afficher_forme(symbole):
    canvas.delete("all")
    canvas.create_text(250, 250, text=symbole, fill="lime", font=("Courier", 100, "bold"))
    root.after(5000, lambda: canvas.delete("all"))

def verifier_missions():
    try:
        reponse = requests.get(URL_SERVEUR, timeout=2)
        if reponse.status_code == 200:
            missions = reponse.json()
            for m in missions:
                if m.get("semaphore_id") == ID_SEMAPHORE:
                    state = str(m.get("state") or "").upper()
                    if state in ["AVAILABLE", "OCCUPIED", "PENDING"]:
                        afficher_forme(m.get("shape_id"))
                        break
    except requests.exceptions.RequestException:
        pass
    root.after(3000, verifier_missions)

verifier_missions()
root.mainloop()
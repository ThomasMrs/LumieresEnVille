from fastapi import FastAPI
from stockage import lire_semaphore, ajouter_semaphore, lire_robots, ajouter_robots, ajouter_equipe, lire_equipe, supprimer_semaphores, supprimer_robots, supprimer_equipes, supprimer_missions, lire_missions, ajouter_missions


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# --- Sémaphores ---

@app.get("/get_semaphore", tags=["Semaphore"])
def read_semaphore():
    return lire_semaphore()

@app.post("/post_semaphore", tags=["Semaphore"])
def send_semaphore(nom: str, caractere_affiche: str, disponible: int, etat: str):
    return ajouter_semaphore(nom, caractere_affiche, disponible, etat)

@app.delete("/delete_semaphores", tags=["Semaphore"])
def delete_semaphores():
    return supprimer_semaphores()

# --- Robots ---

@app.get("/get_robots", tags=["Robots"])
def read_robots():
    return lire_robots()

@app.post("/post_robots", tags=["Robots"])
def post_robots(nom: str, position_x: float, position_y: float, statut: str, disponible: int):
    return ajouter_robots(nom, position_x, position_y, statut, disponible)

@app.delete("/delete_robots", tags=["Robots"])
def delete_robots():
    return supprimer_robots()

# --- Equipe ---

@app.post("/post_equipe", tags=["Equipe"])
def post_equipe(nom: str, adresse_ip: str, autorise: bool):
    return ajouter_equipe(nom,adresse_ip, autorise)

@app.get("/get_equipe", tags=["Equipe"])
def read_equipe():
    return lire_equipe()

@app.delete("/delete_equipes", tags=["Equipe"])
def delete_equipe():
    return supprimer_equipes()

# --- Missions ---

@app.post("/post_mission", tags=["Missions"])
def post_mission(semaphore_id: str, symbole: str, heure_debut: str, duree: int, statut: str):
    return ajouter_missions(semaphore_id, symbole, heure_debut, duree, statut)

@app.get("/get_missions", tags=["Missions"])
def read_missions():
    return lire_missions()

@app.delete("/delete_missions", tags=["Missions"])
def delete_missions():
    return supprimer_missions()


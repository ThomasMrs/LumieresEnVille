from fastapi import FastAPI, Form, HTTPException
from stockage import (
    lire_semaphore, ajouter_semaphore, supprimer_semaphores, modifier_semaphore,
    lire_robots, ajouter_robots, supprimer_robots, modifier_robots,
    lire_equipe, ajouter_equipe, supprimer_equipes, modifier_equipes, auth_equipe,
    lire_missions, ajouter_missions, supprimer_missions, modifier_missions,
)
import gestion
import http

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# --- Semaphore ---

@app.get("/api/list_semaphore", tags=["Semaphore"])
def read_semaphore():
    return lire_semaphore()

@app.get("/api/semaphore/{id}", tags=["Semaphore"])
def read_one_semaphore(id: str):
    for s in lire_semaphore():
        if s["id"] == id:
            return s
    return {}

@app.post("/api/add_semaphore", tags=["Semaphore"])
def add_semaphore(name: str, state: str):
    return ajouter_semaphore(name, state)

@app.put("/api/update_semaphore/{id}", tags=["Semaphore"])
def update_semaphore(id: str, name: str, state: str, duration: int):
    return modifier_semaphore(id, name, state, duration)

@app.delete("/api/delete_semaphores", tags=["Semaphore"])
def delete_semaphores():
    return supprimer_semaphores()

# --- Robot ---

@app.get("/api/list_robots", tags=["Robot"])
def read_robots():
    return lire_robots()

@app.get("/api/robot/{id}", tags=["Robot"])
def read_one_robot(id: str):
    for r in lire_robots():
        if r["id"] == id:
            return r
    return {}

@app.get("/api/robot/{id}/mission", tags=["Robot"])
def read_robot_missions(id: str):
    return [m for m in lire_missions() if m["robot_id"] == id]

@app.post("/api/add_robot", tags=["Robot"])
def add_robot(name: str, state: str, speed: float, position_x: float, position_y: float):
    return ajouter_robots(name, state, speed, position_x, position_y)

@app.put("/api/update_robot/{id}", tags=["Robot"])
def update_robot(id: str, name: str, state: str, speed: float, position_x: float, position_y: float):
    return modifier_robots(id, name, state, speed, position_x, position_y)

@app.delete("/api/delete_robots", tags=["Robot"])
def delete_robots():
    return supprimer_robots()

# --- Mission ---

@app.get("/api/list_missions", tags=["Mission"])
def read_missions():
    return lire_missions()

@app.post("/api/add_mission", tags=["Mission"])
def add_mission(name: str, time: int, semaphore_id: str, team_id: str, robot_id: str = None, state: str = "Pending", start_date: str = None, end_date: str = None):
    return ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team_id,time)

@app.put("/api/update_mission/{id}", tags=["Mission"])
def update_mission(id: str, name: str, semaphore_id: str, robot_id: str, state: str, start_date: str, end_date: str, team: str):
    return modifier_missions(id, name, semaphore_id, robot_id, state, start_date, end_date, team)

@app.delete("/api/delete_missions", tags=["Mission"])
def delete_missions():
    return supprimer_missions()

@app.put("/api/valider_mission/{mission_id}", tags=["Mission"])
def api_valider_mission(mission_id: str, name: str, time: int, semaphore_id: str, team_id: str, symbole: str):
    
    resultat = gestion.valider_nouvelle_mission(name, time, semaphore_id, team_id, symbole, mission_id)

    if resultat["succes"] == False:
        raise HTTPException(status_code=400, detail=resultat["message"])
    return {"status": "ok", "detail": resultat["message"]}

# --- Team ---

@app.get("/api/list_teams", tags=["Team"])
def read_teams():
    return lire_equipe()

@app.post("/api/add_team", tags=["Team"])
def add_team(name: str, ip: str, allowed: bool):
    return ajouter_equipe(name, ip, allowed)

@app.put("/api/update_team/{id}", tags=["Team"])
def update_team(id: str, name: str, ip: str, allowed: bool):
    return modifier_equipes(id, name, ip, allowed)

@app.delete("/api/delete_teams", tags=["Team"])
def delete_teams():
    return supprimer_equipes()

# Liste des objets autorisés à se connecter
@app.get("/api/list_teams_allowed", tags=["Team"])
def read_teams_allowed():
    return auth_equipe()
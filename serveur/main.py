from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille

app = FastAPI()

# Chemins d'accès absolus vers tes deux fichiers séparés
# Remplacer ces deux lignes tout en haut de ton main.py :

IHM_PATH = Path(__file__).parent / "serveur" / "static" / "index.html"
CSS_PATH = Path(__file__).parent / "serveur" / "static" / "style.css"

def page_html(message=""):
    html = IHM_PATH.read_text(encoding="utf-8")
    if message:
        html = html.replace("", f'<div class="message">{message}</div>')
    return HTMLResponse(content=html)

# --- ROUTE PRINCIPALE POUR L'IHM ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return page_html()

# --- ROUTE TECHNIQUE POUR LE FICHIER CSS SÉPARÉ ---
@app.get("/style.css")
def read_css():
    css_content = CSS_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=css_content, media_type="text/css")


# --- UNIFICATION DES ROUTES FORMULAIRES ---
@app.get("/ihm/add_config", response_class=HTMLResponse)
def ihm_add_config(nombre_x: int, nombre_y: int, nombre_semaphore: int, nombre_robot: int):
    config.ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)
    return page_html("Configuration serveur initialisée avec succès")

@app.get("/ihm/create_grille", response_class=HTMLResponse)
def ihm_create_grille(name: str):
    resultat = grille.creer_grille(name)
    if resultat is None:
        return page_html("Erreur : config introuvable")
    return page_html(f"Grille '{name}' créée ({resultat['segments']} segments)")

@app.get("/ihm/add_semaphore", response_class=HTMLResponse)
def ihm_add_semaphore(name: str, duration: int, type: str, coord_x: int, coord_y: int):
    semaphores.ajouter_semaphore(name, duration, type, coord_x, coord_y)
    return page_html(f"Sémaphore '{name}' ajouté aux coordonnées ({coord_x}, {coord_y})")

@app.get("/ihm/add_robot", response_class=HTMLResponse)
def ihm_add_robot(name: str = "", speed: int = 1, position_x: int = 0, position_y: int = 0):
    champs = {}
    if name: champs["name"] = name
    if speed: champs["speed"] = speed
    if position_x: champs["position_x"] = position_x
    if position_y: champs["position_y"] = position_y
    robots.ajouter_robots(**champs)
    return page_html(f"Robot '{name}' déployé à sa base")

@app.get("/ihm/add_team", response_class=HTMLResponse)
def ihm_add_team(name: str, ip: str = "", allowed: str = ""):
    teams.ajouter_equipe(name, ip, allowed == "true")
    return page_html(f"Équipe '{name}' enregistrée")

@app.get("/ihm/add_shape", response_class=HTMLResponse)
def ihm_add_shape(name: str, image: str):
    shapes.ajouter_shape(name, image)
    return page_html(f"Forme '{name}' ajoutée au catalogue")

@app.get("/ihm/add_mission", response_class=HTMLResponse)
def ihm_add_mission(semaphore_id: str, shape_id: str, team: str,
                    name: str = "", robot_id: str = "",
                    start_date: str = "", end_date: str = "", time: str = ""):
    missions.ajouter_missions(name, semaphore_id, robot_id or None, "pending",
                              start_date, end_date, team, time, shape_id)
    return page_html(f"Mission '{name}' lancée avec succès")

# --- INCLUSION DES ROUTERS API ---
app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
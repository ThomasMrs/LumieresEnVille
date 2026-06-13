from pathlib import Path
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille, segment

app = FastAPI()

# Chemins simples vers tes fichiers
IHM_PATH = Path(__file__).parent / "static" / "index.html"
CSS_PATH = Path(__file__).parent / "static" / "style.css"

def page_html(message=""):
    try:
        html = IHM_PATH.read_text(encoding="utf-8")
        css = CSS_PATH.read_text(encoding="utf-8")
        html = html.replace("", f"<style>{css}</style>")
        if message:
            html = html.replace("", f'<div class="message"><b>Info :</b> {message}</div>')
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(f"Erreur de lecture des fichiers HTML/CSS : {e}")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return page_html()

# --- ROUTE POST POUR LE CSV ---
@app.post("/ihm/add_shape_csv", response_class=HTMLResponse)
async def ihm_add_shape_csv(name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        texte_csv = content.decode("utf-8")
        # Nettoyage pur : supprime les sauts de ligne, virgules, espaces
        matrice_propre = re.sub(r'[\n\r\s,;]', '', texte_csv)
        shapes.ajouter_shape(name, matrice_propre)
        return page_html(f"Succès ! Forme '{name}' ajoutée depuis le CSV.")
    except Exception as e:
        return page_html(f"Erreur CSV : {e}")

# --- AUTRES ROUTES BASIQUES ---
@app.get("/ihm/add_config", response_class=HTMLResponse)
def ihm_add_config(nombre_x: int, nombre_y: int, nombre_semaphore: int, nombre_robot: int):
    config.ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)
    return page_html("Configuration initialisée")

@app.get("/ihm/create_grille", response_class=HTMLResponse)
def ihm_create_grille(name: str):
    grille.creer_grille(name)
    return page_html(f"Grille '{name}' créée")

@app.get("/ihm/add_semaphore", response_class=HTMLResponse)
def ihm_add_semaphore(name: str, duration: int, type: str, coord_x: int, coord_y: int):
    semaphores.ajouter_semaphore(name, duration, type, coord_x, coord_y)
    return page_html(f"Sémaphore '{name}' ajouté en ({coord_x}, {coord_y})")

@app.get("/ihm/add_robot", response_class=HTMLResponse)
def ihm_add_robot(name: str = "", speed: int = 1, position_x: int = 0, position_y: int = 0):
    robots.ajouter_robots(name=name, speed=speed, position_x=position_x, position_y=position_y)
    return page_html(f"Robot '{name}' déployé")

@app.get("/ihm/add_team", response_class=HTMLResponse)
def ihm_add_team(name: str, ip: str = "", allowed: str = ""):
    teams.ajouter_equipe(name, ip, allowed == "true")
    return page_html(f"Équipe '{name}' enregistrée")

@app.get("/ihm/add_mission", response_class=HTMLResponse)
def ihm_add_mission(semaphore_id: str, shape_id: str, team: str, name: str = ""):
    missions.ajouter_missions(name, semaphore_id, None, "pending", "", "", team, "", shape_id)
    return page_html(f"Mission '{name}' lancée")

# Inclusions
app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
app.include_router(segment.router)
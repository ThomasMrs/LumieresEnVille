from pathlib import Path
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille

app = FastAPI()

# Détection du chemin (gère le fait que main.py soit à la racine ou non)
BASE_DIR = Path(__file__).parent
if (BASE_DIR / "serveur" / "static" / "index.html").exists():
    IHM_PATH = BASE_DIR / "serveur" / "static" / "index.html"
    CSS_PATH = BASE_DIR / "serveur" / "static" / "style.css"
else:
    IHM_PATH = BASE_DIR / "static" / "index.html"
    CSS_PATH = BASE_DIR / "static" / "style.css"

def page_html(message=""):
    try:
        html = IHM_PATH.read_text(encoding="utf-8")
        if message:
            html = html.replace("", f'<div class="message">{message}</div>')
        else:
            html = html.replace("", "")
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"Erreur de lecture du fichier HTML : {e}")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return page_html()

@app.get("/style.css")
def read_css():
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
        return HTMLResponse(content=css, media_type="text/css")
    except:
        return HTMLResponse(content="")

# --- ROUTE POST POUR L'IMPORTATION DU CSV (SANS JS) ---
@app.post("/ihm/add_shape_csv", response_class=HTMLResponse)
async def ihm_add_shape_csv(name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        texte_csv = content.decode("utf-8")
        # Python supprime espaces, virgules et sauts de ligne pour créer la matrice propre
        matrice_propre = re.sub(r'[\n\r\s,;]', '', texte_csv)
        shapes.ajouter_shape(name, matrice_propre)
        return page_html(f"Succès ! La forme '{name}' a été importée depuis le CSV.")
    except Exception as e:
        return page_html(f"Erreur lors de la lecture du fichier CSV : {e}")

# --- ROUTES DE FORMULAIRES CLASSIQUES ---
@app.get("/ihm/add_config", response_class=HTMLResponse)
def ihm_add_config(nombre_x: int, nombre_y: int, nombre_semaphore: int, nombre_robot: int):
    config.ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)
    return page_html("Configuration initialisée avec succès.")

@app.get("/ihm/add_semaphore", response_class=HTMLResponse)
def ihm_add_semaphore(name: str, duration: int, type: str, coord_x: int, coord_y: int):
    semaphores.ajouter_semaphore(name, duration, type, coord_x, coord_y)
    return page_html(f"Sémaphore '{name}' enregistré.")

@app.get("/ihm/add_robot", response_class=HTMLResponse)
def ihm_add_robot(name: str, speed: int = 1, position_x: int = 0, position_y: int = 0):
    robots.ajouter_robots(name=name, speed=speed, position_x=position_x, position_y=position_y)
    return page_html(f"Robot '{name}' déployé.")

@app.get("/ihm/add_team", response_class=HTMLResponse)
def ihm_add_team(name: str, ip: str = "127.0.0.1", allowed: str = "true"):
    teams.ajouter_equipe(name, ip, allowed == "true")
    return page_html(f"Équipe '{name}' enregistrée.")


# -- Inclusion de tes API
app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
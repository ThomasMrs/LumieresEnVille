from pathlib import Path
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille, ihm, fun

app = FastAPI()

BASE_DIR = Path(__file__).parent
CSS_PATH = BASE_DIR / "style.css"


# -- Route qui sert le fichier de style de l'IHM
@app.get("/style.css")
def envoyer_css():
    return HTMLResponse(content=CSS_PATH.read_text(encoding="utf-8"), media_type="text/css")


# -- Inclusion de tes API
app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
app.include_router(ihm.router)
app.include_router(fun.router)
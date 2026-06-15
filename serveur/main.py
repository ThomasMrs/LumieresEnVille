from pathlib import Path
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille, segment

app = FastAPI()

BASE_DIR = Path(__file__).parent
HTML_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "style.css"

# 1. Route pour afficher la page d'accueil
@app.get("/", response_class=HTMLResponse)
def afficher_accueil():
    contenu_html = HTML_PATH.read_text(encoding="utf-8")
    # On supprime le marqueur de message s'il n'y a rien à afficher
    contenu_html = contenu_html.replace("", "")
    return HTMLResponse(content=contenu_html)

# 2. Route pour envoyer le fichier de design (CSS)
@app.get("/style.css")
def envoyer_css():
    contenu_css = CSS_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=contenu_css, media_type="text/css")

# 3. Route pour traiter une action (ex: soumission d'un formulaire)
@app.post("/traiter_formulaire", response_class=HTMLResponse)
def traiter_formulaire(nom_utilisateur: str = Form(...)):
    contenu_html = HTML_PATH.read_text(encoding="utf-8")
    
    # On crée un message de succès
    message = f"<div class='succes'>Bonjour <b>{nom_utilisateur}</b>, donnée reçue avec succès !</div>"
    
    # On injecte le message dans le HTML à la place du commentaire prévu
    contenu_html = contenu_html.replace("", message)
    
    return HTMLResponse(content=contenu_html)

app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
app.include_router(segment.router)
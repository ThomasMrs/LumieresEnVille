from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from stockage.robot import ajouter_robots
from stockage.semaphore import ajouter_semaphore
from stockage.shape import ajouter_shape
from stockage.config import ajouter_config
from routes.grille import creer_grille
from gestion import valider_type_semaphore, valider_coordonnees

router = APIRouter(prefix="/api", tags=["Ihm"])

def generer_page_html(message: str = "Bienvenue sur l'IHM !") -> str:
    html_content = f"""
    <!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHM</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <section class="form-robot">
        <form method="post" action="/api/ihm/add_robot">
            <h1>Robot</h1>
            <label>Nom&nbsp;:
                <input name="name" autocomplete="name" />
            </label>
            <label>Vitesse&nbsp;:
                <input name="speed" />
            </label>
            <label>Position X&nbsp;:
                <input name="position_x" />
            </label>
            <label>Position Y&nbsp;:
                <input name="position_y" />
            </label>
            <button type="submit">Ajouter le robot</button>
        </form>
    </section>

    <section class="form-semaphore">
        <form method="post" action="/api/ihm/add_semaphore">
            <h1>Sémaphore</h1>
            <label>Nom&nbsp;:
                <input name="name" autocomplete="name" />
            </label>
            <label>Durée&nbsp;:
                <input name="duration" />
            </label>

            <label for="type-select">Type&nbsp;:</label>
            <select name="type" id="type-select">
                <option value="Ascii">Ascii</option>
                <option value="Tracant">Tracant</option>
                <option value="Helice">Helice</option>
            </select>

            <label>Coordonnées X&nbsp;:
                <input name="coord_x" />
            </label>
            <label>Coordonnées Y&nbsp;:
                <input name="coord_y" />
            </label>
            <button type="submit">Ajouter le sémaphore</button>
        </form>
    </section>

    <section class="form-shape">
        <form method="post" action="/api/ihm/add_shape">
            <h1>Forme</h1>
            <label>Nom&nbsp;:
                <input name="name" autocomplete="name" />
            </label>
            <label>Image&nbsp;:
                <input name="image" />
            </label>
            <button type="submit">Ajouter la forme</button>
        </form>
    </section>

    <section class="form-config">
        <form method="post" action="/api/ihm/add_grille">
            <h1>Grille</h1>
            <label>Nom de la grille&nbsp;:
                <input name="name" autocomplete="name" />
            </label>
            <label>Nombre sémaphore&nbsp;:
                <input name="nombre_semaphore" />
            </label>
            <label>Nombre robot&nbsp;:
                <input name="nombre_robot" />
            </label>
            <label>Nombre X&nbsp;:
                <input name="nombre_x" />
            </label>
            <label>Nombre Y&nbsp;:
                <input name="nombre_y" />
            </label>
            <button type="submit">Ajouter la grille</button>
        </form>
    </section>
</body>
</html>
    """
    return html_content

@router.get("/ihm", response_class=HTMLResponse)
def accueil():
    return generer_page_html()


@router.post("/ihm/add_robot", response_class=HTMLResponse)
def ihm_add_robot(name: str = Form(None), speed: int = Form(None),
                  position_x: int = Form(None), position_y: int = Form(None)):
    ajouter_robots(name=name, speed=speed, position_x=position_x, position_y=position_y)
    return generer_page_html("Robot ajouté !")


@router.post("/ihm/add_semaphore", response_class=HTMLResponse)
def ihm_add_semaphore(name: str = Form(...), duration: int = Form(...),
                      type: str = Form(...), coord_x: int = Form(...),
                      coord_y: int = Form(...)):
    if not valider_type_semaphore(type):
        return generer_page_html("Erreur : Type invalide (Ascii | Helice | Tracant)")
    if not valider_coordonnees(coord_x, coord_y):
        return generer_page_html("Erreur : Coordonnées hors limites de la grille")
    ajouter_semaphore(name, duration, type, coord_x, coord_y)
    return generer_page_html("Sémaphore ajouté !")


@router.post("/ihm/add_shape", response_class=HTMLResponse)
def ihm_add_shape(name: str = Form(...), image: str = Form(...)):
    ajouter_shape(name, image)
    return generer_page_html("Forme ajoutée !")


@router.post("/ihm/add_grille", response_class=HTMLResponse)
def ihm_add_grille(name: str = Form(...), nombre_x: int = Form(...),
                   nombre_y: int = Form(...), nombre_semaphore: int = Form(...),
                   nombre_robot: int = Form(...)):
    # 1. On enregistre la config (taille de la grille + quotas)
    ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)
    # 2. On génère réellement la grille (noeuds + segments)
    resultat = creer_grille(name)
    if resultat is None:
        return generer_page_html("Erreur : impossible de créer la grille")
    return generer_page_html(f"Grille « {name} » créée ({resultat['segments']} segments) !")
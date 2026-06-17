from fastapi import Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from stockage.robot import ajouter_robots
from stockage.semaphore import ajouter_semaphore
from stockage.shape import ajouter_shape
from stockage.config import ajouter_config
from stockage.team import ajouter_equipe
from stockage.mission import ajouter_missions
from routes.grille import creer_grille
from gestion import valider_type_semaphore, valider_type_robot, valider_coordonnees

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

            <label for="type-robot-select">Type&nbsp;:</label>
            <select name="type" id="type-robot-select">
                <option value="Roulant">Roulant</option>
                <option value="Volant">Volant</option>
                <option value="Sautant">Sautant</option>
            </select>

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
                <option value="table">table</option>
                <option value="helice">helice</option>
                <option value="caractere">caractere</option>
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

        <form method="post" action="/api/ihm/add_shape_csv" enctype="multipart/form-data">
            <h1>Forme (CSV)</h1>
            <label>Fichier CSV&nbsp;:
                <input type="file" name="fichier" accept=".csv" />
            </label>
            <button type="submit">Importer le CSV</button>
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

    <section class="form-generer">
        <form method="post" action="/api/ihm/generer">
            <h1>Données de test</h1>
            <button type="submit">Générer un élément dans chaque table</button>
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
def ihm_add_robot(name: str = Form(None), speed: float = Form(None),
                  position_x: float = Form(None), position_y: float = Form(None),
                  type: str = Form(None)):
    if type is not None and not valider_type_robot(type):
        return generer_page_html("Erreur : Type robot invalide (Roulant | Volant | Sautant)")
    ajouter_robots(name=name, speed=speed, position_x=position_x,
                   position_y=position_y, type=type)
    return generer_page_html("Robot ajouté !")


@router.post("/ihm/add_semaphore", response_class=HTMLResponse)
def ihm_add_semaphore(name: str = Form(...), duration: int = Form(...),
                      type: str = Form(...), coord_x: int = Form(...),
                      coord_y: int = Form(...)):
    if not valider_type_semaphore(type):
        return generer_page_html("Erreur : Type invalide (table | helice | caractere)")
    if not valider_coordonnees(coord_x, coord_y):
        return generer_page_html("Erreur : Coordonnées hors limites de la grille")
    ajouter_semaphore(name, duration, type, coord_x, coord_y)
    return generer_page_html("Sémaphore ajouté !")


@router.post("/ihm/add_shape", response_class=HTMLResponse)
def ihm_add_shape(name: str = Form(...), image: str = Form(...)):
    ajouter_shape(name, image)
    return generer_page_html("Forme ajoutée !")


@router.post("/ihm/add_shape_csv", response_class=HTMLResponse)
def ihm_add_shape_csv(fichier: UploadFile):
    # Lecture en memoire (sync). Le nom de la forme = nom du fichier uploade
    # (sans l'extension .csv), pour que le controleur voie un vrai nom.
    contenu = fichier.file.read().decode("utf-8").strip()
    if not contenu:
        return generer_page_html("Erreur : fichier CSV vide")
    name = fichier.filename or "forme"
    if name.lower().endswith(".csv"):
        name = name[:-4]
    # Le CSV peut contenir des guillemets, du texte (nom) et melanger
    # espaces/retours ligne. On ne garde que les points (label;x;y;actif),
    # c'est-a-dire les jetons contenant des ';' : pas de texte, pas de nom.
    brut = contenu.replace('"', " ").replace("\n", " ").replace("\r", " ")
    points = [jeton for jeton in brut.split() if ";" in jeton]
    image = "\n".join(points)
    ajouter_shape(name, image)
    return generer_page_html("Forme (CSV) importée !")


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


@router.post("/ihm/generer", response_class=HTMLResponse)
def ihm_generer():
    """Genere un element coherent dans chaque table (jeu de demonstration).
    Aligne sur les dernieres regles : grille base (0,0) + centree sur x,
    coords valides (x in [-2,2], y in [1,5]), type de robot, positions et
    vitesse decimales, image = points uniquement, missions avec couleur RGB.
    """
    # Config 5x5 + grille (base en (0,0), segment vertical, grille centree).
    ajouter_config(5, 5, 3, 3)
    creer_grille("Grille générée")

    # Semaphore : un type valide, coordonnees centrees valides.
    s_id = ajouter_semaphore("Sémaphore démo", 30, "helice", 0, 3)["id"]

    # Robot : type valide + position et vitesse decimales.
    r_id = ajouter_robots(name="Robot démo", speed=1.5,
                          position_x=1.5, position_y=2.0, type="Roulant")

    # Equipe.
    ajouter_equipe("Équipe démo", "192.168.1.50", 1)

    # Forme : image = points uniquement (label;x;y;actif).
    sh_id = ajouter_shape("Triangle démo",
                          "P1;0.0;0.0;1\nP2;50.0;0.0;1\nP3;25.0;43.3;1")["id"]

    # Mission : etat valide, liens coherents, couleur RGB.
    ajouter_missions("Mission démo", s_id, r_id, "Done",
                     "2026-06-01", "2026-06-02", "Équipe démo", "90", sh_id,
                     255, 128, 0)

    return generer_page_html("Un élément généré dans chaque table !")
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Ihm"])

# --- FONCTION UTILITAIRE POUR GÉNÉRER LE HTML ---
def generer_page_html(message: str = "Bienvenue sur l'IHM !") -> str:
    """
    Construit et retourne le code HTML complet de la page.
    L'utilisation des f-strings (f"...") permet d'injecter des variables Python.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Mon IHM sans Jinja ni JS</title>
    </head>
    <body>
    </body>
    </html>
    """
    return html_content


# --- ROUTES FASTAPI ---

@router.get("/ihm", response_class=HTMLResponse)
async def accueil():
    # On génère le HTML avec le message par défaut
    page = generer_page_html()
    return page

@router.post("/soumettre", response_class=HTMLResponse)
async def traiter_formulaire(nom_utilisateur: str = Form(...)):
    # On crée notre nouveau message
    nouveau_message = f"Salut {nom_utilisateur}, tes données ont été traitées avec succès !"
    
    # On regénère la page complète avec le nouveau message
    page = generer_page_html(message=nouveau_message)
    return page
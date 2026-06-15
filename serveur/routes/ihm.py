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
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #eee; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; max-width: 400px; }}
            .message {{ color: #d9534f; font-weight: bold; }}
            input, button {{ margin-top: 10px; padding: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mon Application</h1>
            
            <p class="message">{message}</p>

            <form action="/soumettre" method="post">
                <label>Entrez votre nom :</label><br>
                <input type="text" name="nom_utilisateur" required><br>
                <button type="submit">Envoyer</button>
            </form>
        </div>
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
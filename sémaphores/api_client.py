import requests
from datetime import datetime

BASE_URL = "http://192.168.1.14:8000"

def get_missions():
    try:
        response = requests.get(f"{BASE_URL}/api/list_missions", timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print("Erreur de connexion au serveur API:", e)
        return []

def get_shape(shape_id):
    try:
        response = requests.get(f"{BASE_URL}/api/shape/{shape_id}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def get_semaphore(semaphore_id):
    try:
        response = requests.get(f"{BASE_URL}/api/list_semaphore")
        sems = response.json()
        for s in sems:
            if s.get("id") == semaphore_id:
                return s
    except:
        pass
    return {}

def put_mission_state(mission_id, state):
    url = f"{BASE_URL}/api/update_mission/{mission_id}"
    maintenant = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "state": state, 
        "end_date": maintenant
    }
    try:
        rep = requests.put(url, params=params)
        return rep.status_code == 200
    except:
        return False

def put_semaphore_state(semaphore_id, state):
    url = f"{BASE_URL}/api/update_semaphore/{semaphore_id}"
    try:
        rep = requests.put(url, params={"state": state})
        return rep.status_code == 200
    except:
        return False

def decoder_chaine_image(chaine):
    """Transforme le CSV du serveur (une ligne 'label;rayon;angle;stylo' par point)
    en liste de dictionnaires {r, a, s}."""
    points = []
    if not chaine:
        return points

    for ligne in chaine.replace("\r", "").split("\n"):
        ligne = ligne.strip()
        # on saute les lignes vides et l'eventuel entete (rayon;angle;stylo, name...)
        if not ligne or ligne.lower().startswith(("rayon", "name", "label")):
            continue
        colonnes = ligne.split(";")
        if len(colonnes) < 4:
            continue
        try:
            rayon = float(colonnes[1])
            angle = float(colonnes[2])
            stylo = int(colonnes[3])
            points.append({'r': rayon, 'a': angle, 's': stylo})
        except ValueError:
            print("Erreur de parsing sur la ligne:", ligne)

    return points
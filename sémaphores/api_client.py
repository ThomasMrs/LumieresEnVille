import requests
from datetime import datetime

# Configuration du lien avec l'API
ip_serveur = input("IP du serveur (ex: 192.168.1.14) : ").strip()
if not ip_serveur:
    ip_serveur = "127.0.0.1" 

BASE_URL = f"http://{ip_serveur}:8000"
print(f"Configuré sur {BASE_URL} ")

# Requêtes de lecture (Get) 

def get_missions():
    """Récupère la liste de toutes les missions avec un timeout court pour ne pas bloquer l'UI."""
    try:
        response = requests.get(f"{BASE_URL}/api/list_missions", timeout=2)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print("Erreur de connexion au serveur API:", e)
        return []

def get_shape(shape_id):
    """Récupère le dictionnaire JSON contenant les données d'une forme précise."""
    try:
        response = requests.get(f"{BASE_URL}/api/shape/{shape_id}")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

def get_semaphore(semaphore_id):
    """Parcourt tous les sémaphores pour trouver celui qui correspond à l'ID de la mission."""
    try:
        response = requests.get(f"{BASE_URL}/api/list_semaphore")
        sems = response.json()
        for s in sems:
            if s.get("id") == semaphore_id:
                return s
    except:
        pass
    return {}

def get_shape_csv(shape_id):
    """Télécharge les données brutes d'une forme au format CSV."""
    url = f"{BASE_URL}/api/shape/{shape_id}/csv"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

# Requêtes de mise à jour (Put)

def put_mission_state(mission_id, state):
    """Met à jour l'état d'une mission et force l'horodatage de fin."""
    url = f"{BASE_URL}/api/update_mission/{mission_id}"
    maintenant = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        rep = requests.put(url, params={"state": state, "end_date": maintenant})
        return rep.status_code == 200
    except:
        return False

def put_semaphore_state(semaphore_id, state):
    """Libère ou occupe un sémaphore physique."""
    url = f"{BASE_URL}/api/update_semaphore/{semaphore_id}"
    try:
        rep = requests.put(url, params={"state": state})
        return rep.status_code == 200
    except:
        return False

# Traitement données 

def decoder_chaine_image(chaine):
    """Nettoie une chaîne CSV brute (supprime les en-têtes et les espaces) et extrait les points R, A, S."""
    points = []
    if not chaine: return points
    
    chaine_propre = chaine.replace(" ", "\n").replace("\r", "")
    
    for ligne in chaine_propre.split("\n"):
        ligne = ligne.strip()
        if not ligne or ligne.lower().startswith(("rayon", "angle", "stylo")): 
            continue
            
        colonnes = ligne.split(";")
        if len(colonnes) < 4: 
            continue
            
        try:
            points.append({
                'r': float(colonnes[1]), 
                'a': float(colonnes[2]), 
                's': int(colonnes[3])
            })
        except ValueError:
            continue
            
    return points
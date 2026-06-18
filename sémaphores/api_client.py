import requests
from datetime import datetime


ip_serveur = input("IP du serveur (ex: 192.168.1.14) : ").strip()
if not ip_serveur:
    ip_serveur = "127.0.0.1" 

BASE_URL = f"http://{ip_serveur}:8000"
print(f"Configuré sur {BASE_URL} ")

def get_missions():
    try:
        # Le timeout (2 sec) 
        response = requests.get(f"{BASE_URL}/api/list_missions", timeout=2)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print("Erreur de connexion au serveur API:", e)
        return []

def get_shape(shape_id):
    try:
        response = requests.get(f"{BASE_URL}/api/shape/{shape_id}")
        return response.json() if response.status_code == 200 else {}
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
    try:
        rep = requests.put(url, params={"state": state, "end_date": maintenant})
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

def get_shape_csv(shape_id):
    url = f"{BASE_URL}/api/shape/{shape_id}/csv"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None
import requests
from datetime import datetime

# URL de ton serveur
BASE_URL = "http://192.168.1.5"

def get_missions():
    try:
        response = requests.get(f"{BASE_URL}/api/list_missions")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Erreur get_missions : {e}")
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
    params = {
        "state": state,
        "end_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    try:
        response = requests.put(url, params=params)
        return response.status_code == 200
    except:
        return False

def put_semaphore_state(semaphore_id, state):
    url = f"{BASE_URL}/api/update_semaphore/{semaphore_id}"
    params = {"state": state}
    try:
        response = requests.put(url, params=params)
        return response.status_code == 200
    except:
        return False

def decoder_chaine_image(chaine):
    """Décode la chaîne format Pxxx.xxx.x en liste de points"""
    points = []
    if not chaine or chaine == "T": return points
    
    segments = chaine.split('P')
    for seg in segments:
        if not seg: continue
        try:
            parts = seg.split('.')
            points.append({'r': float(parts[0]), 'a': int(parts[1]), 's': int(parts[2])})
        except:
            continue
    return points
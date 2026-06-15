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
    """Transforme les données de l'API en dictionnaire r, a, s (Gère tous les formats)"""
    points = []
    if not chaine or chaine == "T": 
        return points
        
    if ";" in chaine or "\n" in chaine:
        lignes = chaine.strip().split('\n')
        for ligne in lignes:
            ligne = ligne.strip()
            # On ignore les en-têtes
            if not ligne or "rayon" in ligne.lower() or "name" in ligne.lower():
                continue
            
            parties = ligne.split(';')
            try:
                if len(parties) >= 4:
                    r = float(parties[1])
                    a = int(float(parties[2]))
                    s = int(parties[3])
                elif len(parties) == 3:
                    r = float(parties[0])
                    a = int(float(parties[1]))
                    s = int(parties[2])
                else:
                    continue
                    
                points.append({'r': r, 'a': a, 's': s})
            except Exception as e:
                print(f"Erreur lecture CSV sur la ligne : {ligne}")
        return points

    segments = chaine.split('P')
    for seg in segments:
        if seg == "": 
            continue
        try:
            parts = seg.split('.')
            rayon = float(parts[0])
            angle = int(float(parts[1]))
            stylo = int(parts[2])
            points.append({'r': rayon, 'a': angle, 's': stylo})
        except: 
            print("Erreur de parsing sur le segment mathématique:", seg)
            continue
            
    return points
import requests

BASE_URL = "http://192.168.1.18:8000/api"

# ==========================================
# MISSIONS
# ==========================================
def get_missions():
    try:
        req = requests.get(f"{BASE_URL}/list_missions", timeout=2)
        return req.json() if req.status_code == 200 else []
    except: return []

def add_mission(semaphore_id, shape_id, team, name="Test", robot_id=None):
    """Utilisé par le ROBOT pour demander un dessin"""
    params = {
        'semaphore_id': semaphore_id, 'shape_id': shape_id, 
        'team': team, 'name': name, 'robot_id': robot_id
    }
    try:
        req = requests.post(f"{BASE_URL}/add_mission", params=params, timeout=2)
        return req.json() if req.status_code == 200 else None
    except: return None

def put_mission_state(mission_id, state):
    """Utilisé par le SÉMAPHORE (états autorisés: Pending, In progress, Done)"""
    try:
        requests.put(f"{BASE_URL}/update_mission/{mission_id}", params={'state': state}, timeout=2)
    except: pass

# ==========================================
# SEMAPHORES
# ==========================================
def get_semaphore(semaphore_id):
    try:
        req = requests.get(f"{BASE_URL}/semaphore/{semaphore_id}", timeout=2)
        return req.json() if req.status_code == 200 else None
    except: return None

def put_semaphore_state(semaphore_id, state):
    """États autorisés: Available, Occupied, Disabled"""
    try:
        requests.put(f"{BASE_URL}/update_semaphore/{semaphore_id}", params={'state': state}, timeout=2)
    except: pass

# ==========================================
# SHAPES (FORMES)
# ==========================================
def get_shape(shape_id):
    try:
        req = requests.get(f"{BASE_URL}/shape/{shape_id}", timeout=2)
        return req.json() if req.status_code == 200 else {}
    except: return {}

def decoder_chaine_image(chaine_image):
    """Décode 'etoileP19.432.01P...' en [{'r':19, 'a':432, 's':1}]"""
    points = []
    if not chaine_image: return points
    morceaux = chaine_image.split('P')
    for morceau in morceaux[1:]:
        valeurs = morceau.split('.')
        if len(valeurs) >= 3:
            try:
                points.append({
                    'r': float(valeurs[0]),
                    'a': int(valeurs[1]) % 360,
                    's': int(valeurs[2])
                })
            except ValueError:
                continue
    return points
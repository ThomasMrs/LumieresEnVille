import requests

URL_BASE = "http://192.168.1.14:8000/api"

def get_missions():
    try:
        req = requests.get(f"{URL_BASE}/list_missions", timeout=2)
        return req.json() if req.status_code == 200 else []
    except: return []

def get_shape(shape_id):
    try:
        req = requests.get(f"{URL_BASE}/shape/{shape_id}", timeout=2)
        return req.json() if req.status_code == 200 else {}
    except: return {}

def put_semaphore(semaphore_id, state):
    try:
        url = f"{URL_BASE}/update_semaphore/{semaphore_id}?state={state}"
        requests.put(url, timeout=2)
    except: pass

def put_mission_state(mission_id, state):
    try:
        url = f"{URL_BASE}/update_mission/{mission_id}?state={state}"
        requests.put(url, timeout=2)
    except: pass
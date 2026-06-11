import requests

URL_BASE = "http://192.168.1.14:8000/api"

def get_missions():
    try:
        req = requests.get(f"{URL_BASE}/list_missions", timeout=2)
        return req.json() if req.status_code == 200 else []
    except: return []

def get_semaphore(id):
    try:
        req = requests.get(f"{URL_BASE}/semaphore/{id}", timeout=2)
        return req.json() if req.status_code == 200 else {}
    except: return {}

def get_robot(id):
    try:
        req = requests.get(f"{URL_BASE}/robot/{id}", timeout=2)
        if req.status_code == 200:
            return req.json().get("state") == "Occupied"
        return False
    except: return False

def put_semaphore(id, state):
    try:
        requests.put(f"{URL_BASE}/update_semaphore/{id}?state={state}", timeout=2)
    except: pass

def put_mission_state(id, state):
    try:
        requests.put(f"{URL_BASE}/update_mission/{id}?state={state}", timeout=2)
    except: pass
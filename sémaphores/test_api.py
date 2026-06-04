import requests

URL_BASE = "http://192.168.1.100:8000" 
NOM_SEMAPHORE = "SEMA_01"

print("Test de communication API...")

print("\n--- TEST GET ---")
try:
    reponse_get = requests.get(f"{URL_BASE}/get_semaphore")
    print(f"Status GET : {reponse_get.status_code}")
    print(f"Data GET : {reponse_get.json()}")
except Exception as e:
    print(f"Erreur GET : {e}")

print("\n--- TEST POST ---")
try:
    parametres = {
        "nom": NOM_SEMAPHORE,
        "caractere_affiche": "A",
        "disponible": 1,
        "etat": "VEILLE"
    }
    
    reponse_post = requests.post(f"{URL_BASE}/post_semaphore", params=parametres)
    print(f"Status POST : {reponse_post.status_code}")
    print(f"Data POST : {reponse_post.text}")
except Exception as e:
    print(f"Erreur POST : {e}")
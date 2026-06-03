from fastapi import FastAPI
from stockage import lire_semaphore, ajouter_semaphore

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_semaphore", tags=["Semaphore"])
def read_semaphore():
    return lire_semaphore()

@app.post("/post_semaphore", tags=["Semaphore"])
def send_semaphore(id_semaphore, nom, caractere_affiche, disponible, etat):
    return ajouter_semaphore()
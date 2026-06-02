from fastapi import FastAPI
from stockage import lire_semaphore

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_semaphore", tags=["Semaphore"])
def read_semaphore():
    return lire_semaphore()
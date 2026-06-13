from fastapi import APIRouter
# Couche stockage : tout le SQL est defini dans stockage/config.py
from stockage.config import (
    ajouter_config,
    lire_config,
    modifier_config,
)

router = APIRouter(prefix="/api", tags=["Config"])

# =======================
# Routes
# =======================

@router.post("/add_config")
def add_config(nombre_x: int, nombre_y: int, nombre_semaphore: int, nombre_robot: int):
    return ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)


@router.get("/get_config")
def get_config():
    return lire_config()


@router.put("/update_config")
def update_config(nombre_x: int | None = None, nombre_y: int | None = None,
                  nombre_semaphore: int | None = None, nombre_robot: int | None = None):
    config = lire_config()
    if not config:
        return {"status": "error", "detail": "Config introuvable"}
    champs = {}
    if nombre_x is not None:
        champs["nombre_x"] = nombre_x
    if nombre_y is not None:
        champs["nombre_y"] = nombre_y
    if nombre_semaphore is not None:
        champs["nombre_semaphore"] = nombre_semaphore
    if nombre_robot is not None:
        champs["nombre_robot"] = nombre_robot
    modifier_config(config["id"], **champs)
    return {"id": config["id"], "status": "updated"}

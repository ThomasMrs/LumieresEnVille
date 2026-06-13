from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id
# Couche stockage : tout le SQL est defini dans stockage/shape.py
from stockage.shape import (
    ajouter_shape,
    lire_shape,
    supprimer_shapes,
    modifier_shape,
)

router = APIRouter(prefix="/api", tags=["Shape"])

# =======================
# Routes
# =======================

@router.get("/list_shapes")
def read_shapes():
    return lire_shape()


@router.get("/shape/{id}")
def read_one_shape(id: str):
    if not valider_id("shape", id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    for s in lire_shape():
        if s["id"] == id:
            return s


@router.post("/add_shape")
def add_shape(name: str, image: str):
    return ajouter_shape(name, image)


@router.put("/update_shape/{id}")
def update_shape(id: str, name: str | None = None, image: str | None = None):
    if not valider_id("shape", id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    champs = {}
    if name is not None:
        champs["name"] = name
    if image is not None:
        champs["image"] = image
    modifier_shape(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_shapes")
def delete_shapes():
    supprimer_shapes()
    return {"status": "deleted"}

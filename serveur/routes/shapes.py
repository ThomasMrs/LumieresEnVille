from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id
from stockage.shape import (
    ajouter_shape,
    lire_shape,
    supprimer_shapes,
    modifier_shape,
    importer_shape_csv,
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


@router.post("/import_shape_csv")
def import_shape_csv(filename: str):
    chemin = Path(__file__).parent.parent / "templates" / filename
    resultat = importer_shape_csv(str(chemin))
    if resultat is None:
        return HTMLResponse(status_code=404, content="404 - Fichier CSV introuvable")
    return resultat

@router.delete("/delete_shapes")
def delete_shapes():
    supprimer_shapes()
    return {"status": "deleted"}

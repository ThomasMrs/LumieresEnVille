from fastapi import APIRouter
from fastapi.responses import HTMLResponse
# Couche stockage : on reutilise la connexion centralisee
from stockage.db import get_connection

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return HTMLResponse(status_code=200, content="Serveur ON")
    except Exception:
        return HTMLResponse(status_code=503, content="Serveur OFF")


@router.get("/health_all")
def health_all():
    tables = ["semaphore", "robot", "team", "mission", "shape", "config", "segment"]
    try:
        conn = get_connection()
        counts = {}
        for table in tables:
            ligne = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()
            counts[table] = ligne["n"]
        conn.close()
        return {"status": "ok", "database": "lumieres.db", "tables": counts}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

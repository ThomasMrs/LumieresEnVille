import sqlite3
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from database import DB_PATH

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return HTMLResponse(status_code=200, content="Serveur ON")
    except Exception:
        return HTMLResponse(status_code=503, content="Serveur OFF")

@router.get("/health_all")
def health_all():
    tables = ["semaphore", "robot", "team", "mission", "shape", "config"]
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) AS n FROM {table}")
            counts[table] = cursor.fetchone()["n"]
        conn.close()
        return {"status": "ok", "database": "lumieres.db", "tables": counts}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

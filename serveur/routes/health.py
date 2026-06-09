import sqlite3
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health():
    try:
        conn = sqlite3.connect("lumieres.db")
        conn.execute("SELECT 1")
        conn.close()
        return JSONResponse(status_code=200, content={"message": "Serveur ON", "status": 200})
    except Exception:
        return JSONResponse(status_code=503, content={"message": "Serveur OFF", "status": 503})

@router.get("/health_all")
def health():
    tables = ["semaphore", "robot", "team", "mission", "shape"]
    try:
        conn = sqlite3.connect("lumieres.db")
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
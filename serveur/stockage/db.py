import sqlite3
from database import DB_PATH as _DB_PAR_DEFAUT

# Chemin de la base utilise par toute la couche stockage
DB_PATH = _DB_PAR_DEFAUT


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # acces aux colonnes par nom
    return conn


def existe_id(table, id_a_verifier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id_a_verifier,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat is not None

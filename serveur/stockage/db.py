import sqlite3
from database import DB_PATH as _DB_PAR_DEFAUT

# Chemin de la base utilise par toute la couche stockage.
# On peut le remplacer (par exemple dans les tests) pour cibler une base
# temporaire sans toucher a la vraie base lumieres.db.
DB_PATH = _DB_PAR_DEFAUT


def get_connection():
    """Ouvre une connexion sqlite3.

    row_factory = sqlite3.Row permet de lire les colonnes par leur nom
    (ex. ligne["name"]) et de transformer facilement une ligne en dict.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def existe_id(table, id_a_verifier):
    """Renvoie True si un enregistrement avec cet id existe dans la table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id_a_verifier,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat is not None

import sqlite3
from database import DB_PATH as _DB_PAR_DEFAUT

# Chemin de la base utilise par toute la couche stockage
DB_PATH = _DB_PAR_DEFAUT


def get_connection():
    """Ouvre une connexion sqlite3

    permet de lire les colonnes par leur nom et de transformer facilement une ligne en dictionnaire"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def existe_id(table, id_a_verifier):
    """Renvoie True si un enregistrement avec cet id existe dans la table"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id_a_verifier,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat is not None

import sqlite3
import uuid

# Connexion à la base de données
conn = sqlite3.connect('lumieres.db')
cursor = conn.cursor()

# Connexion de la table semaphores
cursor.execute("""CREATE TABLE IF NOT EXISTS semaphores (
    id TEXT PRIMARY KEY,
    nom TEXT,
    caractere_affiche TEXT,
    disponible INTEGER,
    etat TEXT
)""")

# Connexion de la table robots
cursor.execute("""CREATE TABLE IF NOT EXISTS robots (
    id TEXT PRIMARY KEY,
    nom TEXT,
    position_x REAL,
    position_y REAL,
    statut TEXT,
    disponible INTEGER
)""")

# Connexion de la table missions
cursor.execute("""CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    semaphore_id TEXT,
    symbole TEXT,
    heure_debut TEXT,
    duree INTEGER,
    statut TEXT,
    FOREIGN KEY (semaphore_id) REFERENCES semaphores(id)
)""")

# Connexion de la table controleurs
cursor.execute("""CREATE TABLE IF NOT EXISTS controleurs (
    id TEXT PRIMARY KEY,
    nom TEXT,
    adresse_ip TEXT,
    autorise INTEGER
)""")

# Connexion de la table routes
cursor.execute("""CREATE TABLE IF NOT EXISTS routes (
    id TEXT PRIMARY KEY,
    taille REAL,
    vitesse REAL
)""")

conn.commit()

# Fermer la connexion
conn.close()


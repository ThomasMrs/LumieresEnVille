from pathlib import Path
import sqlite3

DB_PATH = str(Path(__file__).parent / "lumieres.db")

# Connexion à la base de données (nom imposé par le contrat d'équipe)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Table semaphore
cursor.execute("""CREATE TABLE IF NOT EXISTS semaphore (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'Available',
    duration    INTEGER NOT NULL DEFAULT 30,
    type        TEXT NOT NULL,
    coord_x     INTEGER NOT NULL,
    coord_y     INTEGER NOT NULL
)""")

# Table robot
cursor.execute("""CREATE TABLE IF NOT EXISTS robot (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'Available',
    speed       REAL NOT NULL DEFAULT 1.0,
    position_x  REAL NOT NULL DEFAULT 0.0,
    position_y  REAL NOT NULL DEFAULT 0.0
)""")

# Table team
cursor.execute("""CREATE TABLE IF NOT EXISTS team (
    id        TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    ip        TEXT,
    allowed   INTEGER NOT NULL DEFAULT 0
)""")

# Table shape
cursor.execute("""CREATE TABLE IF NOT EXISTS shape (
    id     TEXT PRIMARY KEY,
    name   TEXT NOT NULL,
    image  TEXT NOT NULL
)""")

# Table mission (créée après les tables référencées par ses clés étrangères)
cursor.execute("""CREATE TABLE IF NOT EXISTS mission (
    id            TEXT PRIMARY KEY,
    name          TEXT,
    semaphore_id  TEXT,
    robot_id      TEXT,
    shape_id      TEXT,
    state         TEXT DEFAULT 'Pending',
    start_date    TEXT DEFAULT '',
    end_date      TEXT DEFAULT '',
    team          TEXT DEFAULT '',
    time          TEXT DEFAULT '',
    FOREIGN KEY (semaphore_id) REFERENCES semaphore(id),
    FOREIGN KEY (robot_id)     REFERENCES robot(id),
    FOREIGN KEY (shape_id)     REFERENCES shape(id),
    FOREIGN KEY (team)         REFERENCES team(name)
)""")

# Table config (une seule ligne possible, id = 1)
cursor.execute("""CREATE TABLE IF NOT EXISTS config (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    grille          TEXT NOT NULL,
    nbr_semaphore   INTEGER NOT NULL,
    nbr_robot       INTEGER NOT NULL
)""")

conn.commit()
conn.close()
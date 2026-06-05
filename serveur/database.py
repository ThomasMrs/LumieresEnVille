import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('lumieres.db')
cursor = conn.cursor()

# Création de la table semaphores
cursor.execute("""CREATE TABLE IF NOT EXISTS semaphores (
    id TEXT PRIMARY KEY,
    name TEXT,
    state TEXT,
    type TEXT,
    duration INTEGER
)""")

# Création de la table robots
cursor.execute("""CREATE TABLE IF NOT EXISTS robots (
    id TEXT PRIMARY KEY,
    name TEXT,
    state TEXT,
    speed REAL,
    position_x REAL,
    position_y REAL
)""")

# Création de la table missions
cursor.execute("""CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    name TEXT,
    semaphore_id TEXT,
    robot_id TEXT,
    state TEXT,
    start_date TEXT,
    end_date TEXT,
    team_id TEXT,
    time, TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (semaphore_id) REFERENCES semaphores(id),
    FOREIGN KEY (robot_id) REFERENCES robots(id)
    FOREIGN KEY (shape_id) REFERENCES shape(id)
)""")

# Création de la table teams
cursor.execute("""CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    name TEXT,
    ip TEXT,
    allowed INTEGER
)""")

# Création de la table shapes
cursor.execute("""CREATE TABLE IF NOT EXISTS shapes (
    id TEXT PRIMARY KEY,
    name TEXT,
    image TEXT
)""")

conn.commit()
conn.close()
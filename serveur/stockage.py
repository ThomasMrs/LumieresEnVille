import sqlite3
import uuid

# --- Semaphores --- #

def ajouter_semaphore(name, state):
    id_semaphore = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO semaphores (id, name, state) VALUES (?, ?, ?)",
        (id_semaphore, name, state)
    )
    conn.commit()
    conn.close()

def lire_semaphore():
    conn = sqlite3.connect('lumieres.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM semaphores")
    resultat = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultat

def supprimer_semaphores():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM semaphores")
    conn.commit()
    conn.close()

def modifier_semaphore(id_semaphore, name, state, duration):
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE semaphores SET name = ?, state = ?, duration = ? WHERE id = ?",
        (name, state, duration, id_semaphore)
    )
    conn.commit()
    conn.close()

# --- Robots --- #

def ajouter_robots(name, state, speed, position_x, position_y):
    id_robots = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO robots (id, name, state, speed, position_x, position_y) VALUES (?, ?, ?, ?, ?, ?)",
        (id_robots, name, state, speed, position_x, position_y)
    )
    conn.commit()
    conn.close()

def lire_robots():
    conn = sqlite3.connect('lumieres.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM robots")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats

def supprimer_robots():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM robots")
    conn.commit()
    conn.close()

def modifier_robots(id_robots, name, state, speed, position_x, position_y):
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE robots SET name = ?, state = ?, speed = ?, position_x = ?, position_y = ? WHERE id = ?",
        (name, state, speed, position_x, position_y, id_robots)
    )
    conn.commit()
    conn.close()

# --- Teams --- #

def ajouter_equipe(name, ip, allowed):
    id_equipe = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teams (id, name, ip, allowed) VALUES (?, ?, ?, ?)",
        (id_equipe, name, ip, allowed)
    )
    conn.commit()
    conn.close()

def lire_equipe():
    conn = sqlite3.connect('lumieres.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats

def auth_equipe():
    conn = sqlite3.connect('lumieres.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE allowed = 1")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats

def supprimer_equipes():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams")
    conn.commit()
    conn.close()

def modifier_equipes(id_equipe, name, ip, allowed):
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE teams SET name = ?, ip = ?, allowed = ? WHERE id = ?",
        (name, ip, allowed, id_equipe)
    )
    conn.commit()
    conn.close()

# --- Missions --- #

def ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team_id, time):
    id_missions = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO missions (id, name, semaphore_id, robot_id, state, start_date, end_date, team_id, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (id_missions, name, semaphore_id, robot_id, state, start_date, end_date, team_id, time),
    )
    conn.commit() 
    conn.close()
     
def lire_missions():
    conn = sqlite3.connect('lumieres.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM missions")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats

def supprimer_missions():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM missions")
    conn.commit()
    conn.close()

def modifier_missions(id_mission, name, semaphore_id, robot_id, state, start_date, end_date, team):
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE missions SET name = ?, semaphore_id = ?, robot_id = ?, state = ?, start_date = ?, end_date = ?, team = ? WHERE id = ?",
        (name, semaphore_id, robot_id, state, start_date, end_date, team, id_mission)
    )
    conn.commit()
    conn.close()
import sqlite3
import uuid


def ajouter_semaphore(nom, caractere_affiche, disponible, etat): 
    id_semaphore = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO semaphores (id, nom, caractere_affiche, disponible, etat) VALUES (?, ?, ?, ?, ?)",
    (id_semaphore, nom, caractere_affiche, disponible, etat)
    
)
    conn.commit()
    conn.close()
    
#ajouter_semaphore("Sémaphore 2", "B", 1, "libre")

def lire_semaphore():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM semaphores")
    resultat = cursor.fetchall()
    conn.close()
    return resultat

def supprimer_semaphores():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM semaphores")
    conn.commit()
    conn.close()
    
#print(lire_semaphore())    

def ajouter_robots(nom, position_x, position_y, statut, disponible): 
    id_robots = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO robots (id, nom, position_x, position_y, statut, disponible) VALUES (?, ?, ?, ?, ?, ?)",
    (id_robots, nom, position_x, position_y, statut, disponible) 
)
    conn.commit()
    conn.close()
    
def lire_robots():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM robots")
    resultats = cursor.fetchall()
    conn.close()
    return resultats

def ajouter_equipe(nom, adresse_ip, autorise): 
    id_equipe = str(uuid.uuid4())
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO controleurs (id, nom, adresse_ip, autorise) VALUES (?, ?, ?, ?)",
    (id_equipe, nom, adresse_ip, autorise) 
    )
    conn.commit()
    conn.close()
    
def lire_equipe():
    conn = sqlite3.connect('lumieres.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM controleurs")
    resultats = cursor.fetchall()
    conn.close()
    return resultats


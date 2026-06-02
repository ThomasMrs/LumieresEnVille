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
    resultats = cursor.fetchall()
    conn.close()
    return resultats


#print(lire_semaphore())    

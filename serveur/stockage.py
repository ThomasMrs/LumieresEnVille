import sqlite3
import uuid

conn = sqlite3.connect('lumieres.db')
cursor = conn.cursor()

id_semaphore = str(uuid.uuid4())

cursor.execute(
    "INSERT INTO semaphores (id, nom, caractere_affiche, disponible, etat) VALUES (?, ?, ?, ?, ?)",
    ( id_semaphore, "Semaphore 1", "A", 1, "disponible" )
)

def ajouter_semaphore(nom, caractere_affiche, disponible, etat):
    ajouter_semaphore("Sémaphore 2", "B", 1, "libre")

conn.commit()
conn.close()
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from routes.semaphores import ajouter_semaphore, lire_semaphore
from routes.robots import ajouter_robots, lire_robots
from routes.teams import ajouter_equipe
from routes.missions import ajouter_missions, lire_missions
from routes.shapes import ajouter_shape, lire_shape
from stockage.shape import importer_shape_csv
from routes.config import ajouter_config, lire_config
from routes.grille import creer_grille

# =======================
# Config
# =======================

# Petite grille
ajouter_config(5, 5, 3, 3)
print("Config 5x5 créée")

# Grille generee
resultat = creer_grille("Grille numéro 1")
print(f"Grille créée : {resultat['segments']} segments")

# =======================
# Semaphores (3 types)
# =======================

# Grille 5x5 centree : base en (0, 0), x va de -2 a 2, y de 1 a 5
ajouter_semaphore("Sémaphore Caractere", 30, "caractere", -2, 1)
ajouter_semaphore("Sémaphore Helice", 45, "helice", 0, 2)
ajouter_semaphore("Sémaphore Table", 20, "table", 2, 4)

semaphores = lire_semaphore()
print(f"{len(semaphores)} semaphores insérés")

# =======================
# Robots (3)
# =======================

ajouter_robots(name="Robot-roulant-01", speed=1.5, position_x=0.0, position_y=0.0,
               type="Roulant", state="Available")
ajouter_robots(name="Robot-volant-02", speed=2.0, position_x=2.0, position_y=3.0,
               type="Volant", state="Available")
ajouter_robots(name="Robot-sautant-03", speed=0.8, position_x=-1.0, position_y=1.0,
               type="Sautant", state="Available")

robots = lire_robots()
print(f"{len(robots)} robots insérés")

# =======================
# Teams (3)
# =======================

ajouter_equipe("Lux Sky Troopers", "192.168.1.96", 1)
ajouter_equipe("Equipe Pokemon", "192.168.1.24", 1)
ajouter_equipe("Equipe Masilia", "192.168.1.22", 1)

print("3 teams insérées")

# =======================
# Shapes (3)
# =======================

ajouter_shape("Caractere : Etoile", "*")
ajouter_shape("Caractere : Lettre A", "A")
ajouter_shape("Caractere : Barre a roue", "T")

# Import de tous les CSV presents dans templates
dossier_templates = Path(__file__).parent.parent / "templates"
for chemin_csv in sorted(dossier_templates.glob("*.csv")):
    resultat_csv = importer_shape_csv(str(chemin_csv))
    print(f"Shape CSV importée ({chemin_csv.name}) : {resultat_csv}")

shapes = lire_shape()
print(f"{len(shapes)} shapes insérées")

# =======================
# Missions - tous les etats
# =======================

s_ids = [s["id"] for s in semaphores]
r_ids = [r["id"] for r in robots]
sh_ids = [s["id"] for s in shapes]

# --- Etat : Awaiting (en attente de tout) ---
ajouter_missions("Mission Attente 1", s_ids[0], None, "Awaiting",
                 "2026-07-01", "2026-07-05", "Lux Sky Troopers", "30", sh_ids[0],
                 255, 0, 0)
ajouter_missions("Mission Attente 2", s_ids[1], None, "Awaiting",
                 "2026-07-02", "2026-07-06", "Equipe Beta", "45", sh_ids[1],
                 0, 255, 0)
ajouter_missions("Mission Attente 3", s_ids[2], None, "Awaiting",
                 "2026-07-03", "2026-07-07", "Equipe Gamma", "60", sh_ids[2],
                 0, 0, 255)

# --- Etat : Pending_robot (semaphore ok, robot manquant) ---
ajouter_missions("Mission PendRobot 1", s_ids[0], None, "Pending_robot",
                 "2026-06-10", "2026-06-11", "Lux Sky Troopers", "60", sh_ids[0],
                 255, 128, 0)
ajouter_missions("Mission PendRobot 2", s_ids[1], None, "Pending_robot",
                 "2026-06-12", "2026-06-13", "Equipe Beta", "90", sh_ids[1],
                 128, 0, 255)
ajouter_missions("Mission PendRobot 3", s_ids[2], None, "Pending_robot",
                 "2026-06-14", "2026-06-15", "Equipe Gamma", "45", sh_ids[2],
                 0, 128, 255)

# --- Etat : Pending_semaphore (robot ok, semaphore occupe) ---
ajouter_missions("Mission PendSema 1", s_ids[0], r_ids[0], "Pending_semaphore",
                 "2026-06-15", "2026-06-16", "Lux Sky Troopers", "120", sh_ids[0],
                 255, 0, 128)
ajouter_missions("Mission PendSema 2", s_ids[1], r_ids[1], "Pending_semaphore",
                 "2026-06-16", "2026-06-17", "Equipe Beta", "30", sh_ids[1],
                 0, 255, 128)
ajouter_missions("Mission PendSema 3", s_ids[2], r_ids[2], "Pending_semaphore",
                 "2026-06-17", "2026-06-18", "Equipe Gamma", "60", sh_ids[2],
                 128, 255, 0)

# --- Etat : Done (terminee) ---
ajouter_missions("Mission Done 1", s_ids[0], r_ids[0], "Done",
                 "2026-06-01", "2026-06-02", "Lux Sky Troopers", "60", sh_ids[0],
                 200, 50, 50)
ajouter_missions("Mission Done 2", s_ids[1], r_ids[1], "Done",
                 "2026-06-03", "2026-06-04", "Equipe Beta", "120", sh_ids[1],
                 50, 200, 50)
ajouter_missions("Mission Done 3", s_ids[2], r_ids[2], "Done",
                 "2026-06-05", "2026-06-06", "Equipe Gamma", "90", sh_ids[2],
                 50, 50, 200)

# --- Missions avec differentes configs (tous champs remplis) ---

ajouter_missions("Mission Complete", s_ids[0], r_ids[0], "Awaiting",
                 "2026-07-01", "2026-07-10", "Lux Sky Troopers", "180", sh_ids[0],
                 255, 215, 0)
ajouter_missions("Mission Doublon A", s_ids[0], r_ids[1], "Awaiting",
                 "2026-09-01", "2026-09-05", "Lux Sky Troopers", "60", sh_ids[0],
                 220, 20, 60)
ajouter_missions("Mission Doublon B", s_ids[0], r_ids[2], "Pending_robot",
                 "2026-09-01", "2026-09-05", "Equipe Beta", "60", sh_ids[0],
                 60, 20, 220)
ajouter_missions("Mission Rapide", s_ids[1], r_ids[0], "Done",
                 "2026-06-20", "2026-06-20", "Lux Sky Troopers", "10", sh_ids[1],
                 255, 105, 180)
ajouter_missions("Mission Longue", s_ids[2], r_ids[1], "Done",
                 "2026-06-20", "2026-06-25", "Equipe Beta", "500", sh_ids[2],
                 75, 0, 130)

missions = lire_missions()
print(f"{len(missions)} missions insérées")

# =======================
# Recap
# =======================

print("\n--- Recap ---")
print(f"Config    : {lire_config()}")
print(f"Semaphores: {len(semaphores)}")
print(f"Robots    : {len(robots)}")
print(f"Shapes    : {len(shapes)}")
print(f"Missions  : {len(missions)}")

etats = {}
for m in missions:
    etats[m["state"]] = etats.get(m["state"], 0) + 1
print(f"Etats     : {etats}")

print("\nDonnées de test insérées avec succès.")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from routes.semaphores import ajouter_semaphore, lire_semaphore
from routes.robots import ajouter_robots, lire_robots
from routes.teams import ajouter_equipe
from routes.missions import ajouter_missions, lire_missions
from routes.shapes import ajouter_shape, lire_shape
from routes.config import ajouter_config, lire_config
from routes.grille import creer_grille

# =======================
# Config
# =======================

# Petite grille
ajouter_config(5, 5, 3, 3)
print("Config 5x5 créée")

# Grille generee
resultat = creer_grille("Grille Test")
print(f"Grille créée : {resultat['segments']} segments")

# =======================
# Semaphores (3 types)
# =======================

ajouter_semaphore("Ascii", 30, "Ascii", 1, 1)
ajouter_semaphore("Helice", 45, "Helice", 3, 2)
ajouter_semaphore("Tracant", 20, "Tracant", 4, 4)

semaphores = lire_semaphore()
print(f"{len(semaphores)} semaphores insérés")

# =======================
# Robots (3)
# =======================

ajouter_robots(name="Robot-01", speed=1.5, position_x=0, position_y=0)
ajouter_robots(name="Robot-02", speed=2.0, position_x=2, position_y=3)
ajouter_robots(name="Robot-03", speed=0.8, position_x=4, position_y=1)

robots = lire_robots()
print(f"{len(robots)} robots insérés")

# =======================
# Teams (3)
# =======================

ajouter_equipe("Lux Sky Troopers", "192.168.1.10", 1)
ajouter_equipe("Equipe Beta", "192.168.1.20", 1)
ajouter_equipe("Equipe Gamma", "192.168.1.30", 0)

print("3 teams insérées")

# =======================
# Shapes (3)
# =======================

ajouter_shape("Etoile", "*")
ajouter_shape("Lettre A", "A")
ajouter_shape("Barre a roue", "T")

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
                 "", "", "Lux Sky Troopers", "", sh_ids[0])
ajouter_missions("Mission Attente 2", s_ids[1], None, "Awaiting",
                 "", "", "Equipe Beta", "", sh_ids[1])
ajouter_missions("Mission Attente 3", s_ids[2], None, "Awaiting",
                 "2026-07-01", "", "Equipe Gamma", "", sh_ids[2])

# --- Etat : Pending_robot (semaphore ok, robot manquant) ---
ajouter_missions("Mission PendRobot 1", s_ids[0], None, "Pending_robot",
                 "2026-06-10", "", "Lux Sky Troopers", "60", sh_ids[0])
ajouter_missions("Mission PendRobot 2", s_ids[1], None, "Pending_robot",
                 "2026-06-12", "", "Equipe Beta", "90", sh_ids[1])
ajouter_missions("Mission PendRobot 3", s_ids[2], None, "Pending_robot",
                 "", "", "Equipe Gamma", "45", sh_ids[2])

# --- Etat : Pending_semaphore (robot ok, semaphore occupe) ---
ajouter_missions("Mission PendSema 1", s_ids[0], r_ids[0], "Pending_semaphore",
                 "2026-06-15", "", "Lux Sky Troopers", "120", sh_ids[0])
ajouter_missions("Mission PendSema 2", s_ids[1], r_ids[1], "Pending_semaphore",
                 "2026-06-16", "", "Equipe Beta", "30", sh_ids[1])
ajouter_missions("Mission PendSema 3", s_ids[2], r_ids[2], "Pending_semaphore",
                 "2026-06-17", "", "Equipe Gamma", "60", sh_ids[2])

# --- Etat : Done (terminee) ---
ajouter_missions("Mission Done 1", s_ids[0], r_ids[0], "Done",
                 "2026-06-01", "2026-06-02", "Lux Sky Troopers", "60", sh_ids[0])
ajouter_missions("Mission Done 2", s_ids[1], r_ids[1], "Done",
                 "2026-06-03", "2026-06-04", "Equipe Beta", "120", sh_ids[1])
ajouter_missions("Mission Done 3", s_ids[2], r_ids[2], "Done",
                 "2026-06-05", "2026-06-06", "Equipe Gamma", "90", sh_ids[2])

# --- Missions avec differentes configs ---

# Tous les champs remplis
ajouter_missions("Mission Complete", s_ids[0], r_ids[0], "Awaiting",
                 "2026-07-01", "2026-07-10", "Lux Sky Troopers", "180", sh_ids[0])

# Sans robot, sans dates
ajouter_missions("Mission Minimale", s_ids[1], None, "Awaiting",
                 "", "", "Equipe Beta", "", sh_ids[1])

# Avec robot mais sans date de fin
ajouter_missions("Mission Sans Fin", s_ids[2], r_ids[2], "Pending_semaphore",
                 "2026-08-01", "", "Equipe Gamma", "45", sh_ids[2])

# Meme semaphore, meme shape, equipes differentes
ajouter_missions("Mission Doublon A", s_ids[0], r_ids[1], "Awaiting",
                 "2026-09-01", "2026-09-05", "Lux Sky Troopers", "60", sh_ids[0])
ajouter_missions("Mission Doublon B", s_ids[0], r_ids[2], "Pending_robot",
                 "2026-09-01", "2026-09-05", "Equipe Beta", "60", sh_ids[0])

# Temps differents
ajouter_missions("Mission Rapide", s_ids[1], r_ids[0], "Done",
                 "2026-06-20", "2026-06-20", "Lux Sky Troopers", "10", sh_ids[1])
ajouter_missions("Mission Longue", s_ids[2], r_ids[1], "Done",
                 "2026-06-20", "2026-06-25", "Equipe Beta", "500", sh_ids[2])

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

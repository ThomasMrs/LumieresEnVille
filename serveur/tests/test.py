import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from routes.semaphores import ajouter_semaphore, lire_semaphore
from routes.robots import ajouter_robots, lire_robots
from routes.teams import ajouter_equipe
from routes.missions import ajouter_missions
from routes.shapes import ajouter_shape, lire_shape
from routes.config import ajouter_config, lire_config

# --- Semaphores (3) ---
ajouter_semaphore("Feu A", 30, "LED", 2, 3)
ajouter_semaphore("Feu B", 45, "HELICE", 5, 1)
ajouter_semaphore("Feu C", 20, "TRACANT", 8, 6)

semaphores = lire_semaphore()
print(f"{len(semaphores)} semaphores insérés")

# --- Robots (3) ---
ajouter_robots(name="Robot-01", speed=1.5, position_x=10.0, position_y=20.0)
ajouter_robots(name="Robot-02", speed=2.0, position_x=5.0, position_y=15.0)
ajouter_robots(name="Robot-03", speed=0.8, position_x=30.0, position_y=40.0)

robots = lire_robots()
print(f"{len(robots)} robots insérés")

# --- Teams (3) ---
ajouter_equipe("Lux Sky Troopers", "192.168.1.10", 1)
ajouter_equipe("Equipe Beta", "192.168.1.20", 1)
ajouter_equipe("Equipe Gamma", "192.168.1.30", 0)

print("3 teams insérées")

# --- Shapes (3) ---
ajouter_shape("Etoile", "*")
ajouter_shape("Lettre A", "A")
ajouter_shape("Drapeau Congo", "🇨🇬")
ajouter_shape("Singe", "🦧")
ajouter_shape("Barre à roue", "⎈")

shapes = lire_shape()
print(f"{len(shapes)} shapes insérées")

# --- Missions (4) ---
s_ids = [s["id"] for s in semaphores]
r_ids = [r["id"] for r in robots]
sh_ids = [s["id"] for s in shapes]

ajouter_missions("Mission Alpha", s_ids[0], r_ids[0], "pending",
                 "2026-06-05", "2026-06-06", "Lux Sky Troopers", 60, sh_ids[0])
ajouter_missions("Mission Beta", s_ids[1], r_ids[1], "pending",
                 "2026-06-07", "2026-06-08", "Equipe Beta", 120, sh_ids[1])
ajouter_missions("Mission Gamma", s_ids[2], r_ids[2], "en cours",
                 "2026-06-08", None, "Lux Sky Troopers", 90, sh_ids[2])
ajouter_missions("Mission Delta", s_ids[0], None, "pending",
                 None, None, "Equipe Beta", None, sh_ids[0])
ajouter_missions("Mission Singe", s_ids[1], r_ids[0], "pending",
                 "2026-06-09", "2026-06-10", "Lux Sky Troopers", 45, sh_ids[3])
ajouter_missions("Mission Barre", s_ids[2], r_ids[1], "pending",
                 "2026-06-10", "2026-06-11", "Equipe Beta", 30, sh_ids[4])

print("6 missions insérées")

# --- Config (1) ---
ajouter_config("10x10", 3, 3)
config = lire_config()
print(f"Config insérée : grille={config['grille']}, semaphores={config['nbr_semaphore']}, robots={config['nbr_robot']}")

print("\nDonnées de test insérées avec succès.")

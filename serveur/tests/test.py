from stockage import (
    ajouter_equipe, ajouter_missions, ajouter_robots, ajouter_semaphore,
    lire_semaphore, lire_robots,
)

ajouter_semaphore("Feu Nord", "rouge")

ajouter_robots("Robot-01", "actif", 1.5, 10.0, 20.0)

ajouter_equipe("Equipe Alpha", "192.168.1.100", 1)

semaphore_id = lire_semaphore()[-1]["id"]

robot_id = lire_robots()[-1]["id"]

ajouter_missions("Mission Test", semaphore_id, robot_id, "en cours",
                 "2026-06-05", "2026-06-06", "Equipe Alpha", 60)

print("4 ajouts effectués.")
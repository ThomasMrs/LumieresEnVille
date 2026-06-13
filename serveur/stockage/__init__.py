# Couche STOCKAGE de l'architecture 3 tiers.
#
# Ce paquet regroupe TOUT l'acces a la base de donnees sqlite3.
# Les routes (IHM / API) et les regles de gestion (gestion.py) ne font
# JAMAIS de SQL directement : elles appellent les fonctions de ce paquet.

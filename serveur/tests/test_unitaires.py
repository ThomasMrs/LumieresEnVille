"""Tests unitaires du Service Web"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Permet d'importer database, stockage, gestion, routes... depuis serveur/
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import init_db
from stockage import db as db_module
from stockage import semaphore as semaphore_store
from stockage import shape as shape_store
from stockage import config as config_store
from stockage import segment as segment_store
from stockage import mission as mission_store
from gestion import (
    valider_id,
    valider_etat,
    valider_type_semaphore,
    valider_coordonnees,
)
from routes.missions import get_available_missions


class BaseTemporaire(unittest.TestCase):
    """Classe de base : prepare une base temporaire avant chaque test
    et la supprime apres."""

    def setUp(self):
        # 1) Cree un fichier de base temporaire
        fichier = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        fichier.close()
        self.chemin_db = fichier.name
        # 2) Cree les tables dans cette base temporaire
        init_db(self.chemin_db)
        # 3) Redirige la couche stockage vers la base temporaire
        self._ancien_chemin = db_module.DB_PATH
        db_module.DB_PATH = self.chemin_db

    def tearDown(self):
        # Remet le chemin d'origine et supprime la base temporaire
        db_module.DB_PATH = self._ancien_chemin
        if os.path.exists(self.chemin_db):
            os.remove(self.chemin_db)


class TestConfigEtCoordonnees(BaseTemporaire):

    def test_config_creee_et_relue(self):
        config_store.ajouter_config(5, 5, 2, 3)
        config = config_store.lire_config()
        self.assertEqual(config["nombre_x"], 5)
        self.assertEqual(config["nombre_y"], 5)
        self.assertEqual(config["nombre_robot"], 3)

    def test_coordonnees_dans_la_grille(self):
        config_store.ajouter_config(5, 5, 2, 3)
        self.assertTrue(valider_coordonnees(0, 0))
        self.assertTrue(valider_coordonnees(4, 4))

    def test_coordonnees_hors_grille(self):
        config_store.ajouter_config(5, 5, 2, 3)
        self.assertFalse(valider_coordonnees(5, 0))   # x trop grand
        self.assertFalse(valider_coordonnees(-1, 0))  # x negatif

    def test_coordonnees_sans_config(self):
        # Sans config, aucune coordonnee ne peut etre validee
        self.assertFalse(valider_coordonnees(0, 0))


class TestSemaphore(BaseTemporaire):

    def setUp(self):
        super().setUp()
        config_store.ajouter_config(5, 5, 2, 3)

    def test_ajout_et_lecture(self):
        resultat = semaphore_store.ajouter_semaphore("S1", 30, "Helice", 1, 1)
        self.assertEqual(resultat["status"], "ok")
        liste = semaphore_store.lire_semaphore()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0]["name"], "S1")

    def test_valider_id_existant_et_inexistant(self):
        resultat = semaphore_store.ajouter_semaphore("S1", 30, "Helice", 1, 1)
        self.assertTrue(valider_id("semaphore", resultat["id"]))
        self.assertFalse(valider_id("semaphore", "id-qui-n-existe-pas"))

    def test_modification(self):
        resultat = semaphore_store.ajouter_semaphore("S1", 30, "Helice", 1, 1)
        semaphore_store.modifier_semaphore(resultat["id"], name="S1-modifie", state="Occupied")
        liste = semaphore_store.lire_semaphore()
        self.assertEqual(liste[0]["name"], "S1-modifie")
        self.assertEqual(liste[0]["state"], "Occupied")

    def test_suppression(self):
        semaphore_store.ajouter_semaphore("S1", 30, "Helice", 1, 1)
        semaphore_store.supprimer_semaphores()
        self.assertEqual(semaphore_store.lire_semaphore(), [])


class TestValidations(BaseTemporaire):

    def test_type_semaphore(self):
        self.assertTrue(valider_type_semaphore("Ascii"))
        self.assertTrue(valider_type_semaphore("Tracant"))
        self.assertTrue(valider_type_semaphore("Helice"))
        self.assertFalse(valider_type_semaphore("HELICE"))   # casse incorrecte
        self.assertFalse(valider_type_semaphore("Autre"))

    def test_etat_semaphore_et_robot(self):
        self.assertTrue(valider_etat("Available", "semaphore"))
        self.assertTrue(valider_etat("Occupied", "robot"))
        self.assertFalse(valider_etat("Awaiting", "semaphore"))

    def test_etat_mission(self):
        self.assertTrue(valider_etat("Awaiting", "mission"))
        self.assertTrue(valider_etat("Done", "mission"))
        self.assertFalse(valider_etat("Available", "mission"))


class TestMissionsDisponibles(BaseTemporaire):

    def setUp(self):
        super().setUp()
        config_store.ajouter_config(5, 5, 2, 3)
        sema = semaphore_store.ajouter_semaphore("S1", 30, "Helice", 1, 1)
        forme = shape_store.ajouter_shape("Lettre A", "A")
        self.sema_id = sema["id"]
        self.shape_id = forme["id"]

    def _ajouter(self, state, robot_id, team):
        return mission_store.ajouter_missions(
            "M", self.sema_id, robot_id, state, "", "", team, "", self.shape_id
        )

    def test_seules_les_missions_awaiting_sans_robot(self):
        self._ajouter("Awaiting", None, "EquipeA")          # disponible
        self._ajouter("Awaiting", "robot-1", "EquipeA")     # robot deja assigne -> non
        self._ajouter("Done", None, "EquipeA")              # terminee -> non
        self._ajouter("Awaiting", None, "EquipeB")          # disponible (autre equipe)

        disponibles = get_available_missions()
        self.assertEqual(len(disponibles), 2)
        for m in disponibles:
            self.assertEqual(m["state"], "Awaiting")
            self.assertFalse(m["robot_id"])

    def test_filtre_par_equipe(self):
        self._ajouter("Awaiting", None, "EquipeA")
        self._ajouter("Awaiting", None, "EquipeB")
        disponibles_a = get_available_missions(team="EquipeA")
        self.assertEqual(len(disponibles_a), 1)
        self.assertEqual(disponibles_a[0]["team"], "EquipeA")


class TestSegment(BaseTemporaire):

    def test_ajout_et_lecture(self):
        config_store.ajouter_config(5, 5, 2, 3)
        segment_store.ajouter_segment(0, 0, 1, 0)
        liste = segment_store.lire_segment()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0]["coord_b_x"], 1)

    def test_remplacer_segments(self):
        config_store.ajouter_config(5, 5, 2, 3)
        segment_store.ajouter_segment(0, 0, 1, 0)
        from uuid import uuid4
        nouveaux = [
            (str(uuid4()), 0, 0, 0, 1),
            (str(uuid4()), 1, 1, 2, 1),
        ]
        segment_store.remplacer_segments(nouveaux)
        liste = segment_store.lire_segment()
        self.assertEqual(len(liste), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

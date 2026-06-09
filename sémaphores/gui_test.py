"""
GUI de test — Sélectionner sémaphore / shape / mission et visualiser la forme.
Se connecte au serveur web pour récupérer les données, plus besoin de copier-coller les IDs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import math

# --- Configuration ---
URL_BASE = "http://127.0.0.1:8000/api"


# =============================================================================
#  Fenêtre principale
# =============================================================================

class GuiTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lux Sky Troopers — Test Formes Sémaphore")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        # Données chargées depuis le serveur
        self.semaphores = []
        self.shapes = []
        self.missions = []

        self._construire_interface()
        self.rafraichir_donnees()

    # -----------------------------------------------------------------
    #  Construction de l'interface
    # -----------------------------------------------------------------
    def _construire_interface(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2e", foreground="white", font=("Helvetica", 11))
        style.configure("Header.TLabel", background="#1e1e2e", foreground="#89b4fa", font=("Helvetica", 13, "bold"))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TLabelframe", background="#1e1e2e", foreground="#cdd6f4", font=("Helvetica", 11, "bold"))
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa")

        # --- Panneau gauche : listes ----
        panneau_gauche = tk.Frame(self.root, bg="#1e1e2e", padx=15, pady=15)
        panneau_gauche.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(panneau_gauche, text="Données serveur", style="Header.TLabel").pack(anchor="w")

        # Bouton rafraîchir
        btn_refresh = ttk.Button(panneau_gauche, text="↻ Rafraîchir", command=self.rafraichir_donnees)
        btn_refresh.pack(fill=tk.X, pady=(5, 15))

        # URL serveur
        frame_url = tk.Frame(panneau_gauche, bg="#1e1e2e")
        frame_url.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(frame_url, text="URL :").pack(side=tk.LEFT)
        self.entry_url = tk.Entry(frame_url, width=30, bg="#313244", fg="white", insertbackground="white",
                                  font=("Helvetica", 10))
        self.entry_url.insert(0, URL_BASE)
        self.entry_url.pack(side=tk.LEFT, padx=5)

        # --- Sémaphores ---
        lf_sema = ttk.LabelFrame(panneau_gauche, text="Sémaphores")
        lf_sema.pack(fill=tk.BOTH, expand=True, pady=5)

        self.liste_sema = tk.Listbox(lf_sema, height=6, bg="#313244", fg="#a6e3a1",
                                     selectbackground="#585b70", font=("Courier", 10),
                                     exportselection=False)
        self.liste_sema.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Shapes ---
        lf_shape = ttk.LabelFrame(panneau_gauche, text="Shapes")
        lf_shape.pack(fill=tk.BOTH, expand=True, pady=5)

        self.liste_shape = tk.Listbox(lf_shape, height=6, bg="#313244", fg="#f9e2af",
                                      selectbackground="#585b70", font=("Courier", 10),
                                      exportselection=False)
        self.liste_shape.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Missions ---
        lf_mission = ttk.LabelFrame(panneau_gauche, text="Missions")
        lf_mission.pack(fill=tk.BOTH, expand=True, pady=5)

        self.liste_mission = tk.Listbox(lf_mission, height=6, bg="#313244", fg="#cba6f7",
                                        selectbackground="#585b70", font=("Courier", 10),
                                        exportselection=False)
        self.liste_mission.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Boutons d'action
        frame_actions = tk.Frame(panneau_gauche, bg="#1e1e2e")
        frame_actions.pack(fill=tk.X, pady=10)

        ttk.Button(frame_actions, text="▶ Afficher Shape",
                   command=self.afficher_shape_selectionnee).pack(fill=tk.X, pady=2)
        ttk.Button(frame_actions, text="▶ Afficher Mission",
                   command=self.afficher_mission_selectionnee).pack(fill=tk.X, pady=2)
        ttk.Button(frame_actions, text="✕ Effacer canvas",
                   command=self.effacer_canvas).pack(fill=tk.X, pady=2)

        # --- Info sélection ---
        self.label_info = ttk.Label(panneau_gauche, text="Aucune sélection", wraplength=280)
        self.label_info.pack(anchor="w", pady=(10, 0))

        # --- Panneau droit : canvas de visualisation ---
        panneau_droit = tk.Frame(self.root, bg="#11111b", padx=15, pady=15)
        panneau_droit.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(panneau_droit, text="Aperçu forme", style="Header.TLabel",
                  background="#11111b").pack(anchor="w")

        self.canvas = tk.Canvas(panneau_droit, width=500, height=500, bg="black",
                                highlightthickness=1, highlightbackground="#45475a")
        self.canvas.pack(pady=10)

        # Label ID copié
        self.label_id = tk.Label(panneau_droit, text="", bg="#11111b", fg="#6c7086",
                                 font=("Courier", 9))
        self.label_id.pack(anchor="w")

    # -----------------------------------------------------------------
    #  Communication serveur
    # -----------------------------------------------------------------
    def _get_url(self):
        return self.entry_url.get().strip().rstrip("/")

    def rafraichir_donnees(self):
        url = self._get_url()
        try:
            r_sema = requests.get(f"{url}/list_semaphore", timeout=3)
            self.semaphores = r_sema.json() if r_sema.status_code == 200 else []
        except Exception:
            self.semaphores = []

        try:
            r_shape = requests.get(f"{url}/list_shapes", timeout=3)
            self.shapes = r_shape.json() if r_shape.status_code == 200 else []
        except Exception:
            self.shapes = []

        try:
            r_mission = requests.get(f"{url}/list_missions", timeout=3)
            self.missions = r_mission.json() if r_mission.status_code == 200 else []
        except Exception:
            self.missions = []

        self._remplir_liste(self.liste_sema, self.semaphores,
                            lambda s: f"{s.get('name', '?'):15s} | {s.get('type', '?'):10s} | ({s.get('coord_x', '?')},{s.get('coord_y', '?')})")
        self._remplir_liste(self.liste_shape, self.shapes,
                            lambda s: f"{s.get('name', '?'):15s} | {s.get('image', '?')[:30]}")
        self._remplir_liste(self.liste_mission, self.missions,
                            lambda m: f"{m.get('name') or '(sans nom)':15s} | {m.get('state', '?'):10s} | {m.get('team', '?')}")

        total = len(self.semaphores) + len(self.shapes) + len(self.missions)
        self.label_info.config(text=f"Chargé : {len(self.semaphores)} séma, "
                                    f"{len(self.shapes)} shapes, {len(self.missions)} missions")

    @staticmethod
    def _remplir_liste(listbox, donnees, formateur):
        listbox.delete(0, tk.END)
        for item in donnees:
            listbox.insert(tk.END, formateur(item))

    # -----------------------------------------------------------------
    #  Sélection et affichage
    # -----------------------------------------------------------------
    def _selection(self, listbox, donnees):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionne un élément dans la liste.")
            return None
        return donnees[sel[0]]

    def afficher_shape_selectionnee(self):
        shape = self._selection(self.liste_shape, self.shapes)
        if not shape:
            return
        image_str = shape.get("image", "")
        nom = shape.get("name", "?")
        self._dessiner_points(image_str, f"Shape : {nom}")
        self.label_id.config(text=f"ID : {shape.get('id', '?')}")

    def afficher_mission_selectionnee(self):
        mission = self._selection(self.liste_mission, self.missions)
        if not mission:
            return

        shape_id = mission.get("shape_id")
        if not shape_id:
            messagebox.showwarning("Attention", "Cette mission n'a pas de shape_id.")
            return

        # Chercher la shape correspondante
        shape = next((s for s in self.shapes if s["id"] == shape_id), None)
        if not shape:
            messagebox.showwarning("Attention", f"Shape {shape_id} introuvable.")
            return

        image_str = shape.get("image", "")
        nom_mission = mission.get("name") or "(sans nom)"
        nom_shape = shape.get("name", "?")
        sema_id = mission.get("semaphore_id", "?")

        # Chercher le nom du sémaphore
        sema = next((s for s in self.semaphores if s["id"] == sema_id), None)
        sema_nom = sema.get("name", sema_id) if sema else sema_id

        self._dessiner_points(image_str,
                              f"Mission : {nom_mission}\nShape : {nom_shape}\nSémaphore : {sema_nom}")
        self.label_id.config(text=f"Mission ID : {mission.get('id', '?')}  |  "
                                  f"Shape ID : {shape_id}  |  Séma ID : {sema_id}")

    def effacer_canvas(self):
        self.canvas.delete("all")
        self.label_id.config(text="")

    # -----------------------------------------------------------------
    #  Dessin sur le canvas
    # -----------------------------------------------------------------
    def _dessiner_points(self, image_str, titre=""):
        """Dessine la forme depuis le format 'x,y;x,y;...' sur le canvas."""
        self.canvas.delete("all")

        # Titre en haut
        if titre:
            self.canvas.create_text(250, 20, text=titre, fill="#89b4fa",
                                    font=("Helvetica", 11, "bold"), anchor="n")

        if not image_str or image_str.strip() == "":
            self.canvas.create_text(250, 250, text="(pas de données image)",
                                    fill="#6c7086", font=("Helvetica", 14))
            return

        # Parser les points "x,y;x,y;..."
        points = []
        try:
            for paire in image_str.strip().split(";"):
                paire = paire.strip()
                if not paire:
                    continue
                coords = paire.split(",")
                x = float(coords[0].strip())
                y = float(coords[1].strip())
                points.append((x, y))
        except (ValueError, IndexError):
            self.canvas.create_text(250, 250, text=f"Format image invalide:\n{image_str[:60]}",
                                    fill="#f38ba8", font=("Helvetica", 11))
            return

        if not points:
            self.canvas.create_text(250, 250, text="(aucun point)",
                                    fill="#6c7086", font=("Helvetica", 14))
            return

        # Trouver les bornes pour centrer
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        range_x = max_x - min_x if max_x != min_x else 1
        range_y = max_y - min_y if max_y != min_y else 1

        # Zone de dessin (marge de 60px)
        marge = 60
        zone = 500 - 2 * marge
        echelle = min(zone / range_x, zone / range_y)

        # Centrer
        cx = 250
        cy = 270  # un peu plus bas pour laisser place au titre

        for (px, py) in points:
            sx = cx + (px - (min_x + max_x) / 2) * echelle
            sy = cy + (py - (min_y + max_y) / 2) * echelle
            r = max(3, min(8, echelle * 0.3))
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                                    fill="#a6e3a1", outline="#a6e3a1")

        # Nombre de points
        self.canvas.create_text(250, 485, text=f"{len(points)} points",
                                fill="#6c7086", font=("Helvetica", 9))

    # -----------------------------------------------------------------
    #  Lancement
    # -----------------------------------------------------------------
    def lancer(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GuiTest()
    app.lancer()

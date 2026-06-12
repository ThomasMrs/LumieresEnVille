import tkinter as tk

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sémaphore - Panneau de Contrôle")
        self.root.configure(bg="black")
        
        self.frame_local = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief="groove")
        self.frame_local.pack(fill="x", padx=20, pady=10)
        
        tk.Label(self.frame_local, text="🔧 Tests Manuels (Hors-Ligne)", bg="#1a1a1a", fg="gray", font=("Arial", 9)).pack(pady=2)
        
        self.btn_table = tk.Button(
            self.frame_local, text="✒️ Ouvrir Table Traçante", 
            bg="#333333", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_table.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        self.btn_helice = tk.Button(
            self.frame_local, text="🌀 Ouvrir Hélice LED", 
            bg="#333333", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_helice.pack(side="right", expand=True, fill="x", padx=10, pady=5)
        # ----------------------------------------------

        self.canvas = tk.Canvas(self.root, width=500, height=350, bg="black", highlightthickness=0)
        self.canvas.pack(padx=20, pady=5)
        
        self.txt_statut = self.canvas.create_text(250, 30, text="Initialisation...", fill="white", font=("Arial", 12))
        self.txt_details = self.canvas.create_text(250, 70, text="En attente...", fill="yellow", font=("Arial", 10))
        
        self.frame_choix = tk.Frame(self.root, bg="black")
        self.frame_choix.pack(fill="x", padx=20, pady=10)

    def set_commande_table(self, callback):
        self.btn_table.config(command=callback)

    def set_commande_helice(self, callback):
        self.btn_helice.config(command=callback)

    def mettre_a_jour_statut(self, texte):
        self.canvas.itemconfig(self.txt_statut, text=texte)

    def mettre_a_jour_details(self, texte):
        self.canvas.itemconfig(self.txt_details, text=texte)

    def afficher_missions(self, missions, callback):
        for btn in self.frame_choix.winfo_children(): btn.destroy()
        tk.Label(self.frame_choix, text="📡 Missions Serveur (API) :", bg="black", fg="cyan", font=("Arial", 10, "bold")).pack(pady=5)
        for m in missions:
            text_bouton = f"{m.get('name')} (ID: {m.get('id')})"
            tk.Button(self.frame_choix, text=text_bouton, command=lambda mc=m: callback(mc)).pack(fill="x", pady=2)

    def afficher_forme(self, symbole_ascii):
        self.canvas.delete("dessin")
        if not symbole_ascii:
            symbole_ascii = "?"
            
        self.canvas.create_text(
            250, 220, 
            text=symbole_ascii, 
            fill="cyan", 
            font=("Courier", 130, "bold"), 
            tags="dessin"
        )
        self.canvas.update()
import tkinter as tk

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sémaphore - Contrôle")
        self.root.configure(bg="black")
        self.canvas = tk.Canvas(self.root, width=500, height=400, bg="black", highlightthickness=0)
        self.canvas.pack(padx=20, pady=10)
        
        self.txt_statut = self.canvas.create_text(250, 40, text="Initialisation...", fill="white", font=("Arial", 12))
        self.txt_details = self.canvas.create_text(250, 95, text="En attente...", fill="yellow", font=("Arial", 10))
        self.frame_choix = tk.Frame(self.root, bg="black")
        self.frame_choix.pack(fill="x", padx=20, pady=10)

    def mettre_a_jour_statut(self, texte):
        self.canvas.itemconfig(self.txt_statut, text=texte)

    def mettre_a_jour_details(self, texte):
        self.canvas.itemconfig(self.txt_details, text=texte)

    def afficher_missions(self, missions, callback):
        for btn in self.frame_choix.winfo_children(): btn.destroy()
        tk.Label(self.frame_choix, text="Missions prêtes :", bg="black", fg="white").pack()
        for m in missions:
            text_bouton = f"{m.get('name')} (ID: {m.get('id')})"
            tk.Button(self.frame_choix, text=text_bouton, command=lambda mc=m: callback(mc)).pack(fill="x", pady=2)

    def afficher_forme(self, shape_name):
        self.canvas.delete("dessin")
        val = str(shape_name).strip()
        
        if val == "Lettre A":
            self.canvas.create_line(250, 150, 150, 350, fill="yellow", width=5, tags="dessin")
            self.canvas.create_line(250, 150, 350, 350, fill="yellow", width=5, tags="dessin")
            self.canvas.create_line(200, 260, 300, 260, fill="yellow", width=5, tags="dessin")
        elif val == "Etoile":
            self.canvas.create_line(250, 150, 250, 350, fill="cyan", width=3, tags="dessin")
            self.canvas.create_line(150, 250, 350, 250, fill="cyan", width=3, tags="dessin")
            self.canvas.create_line(180, 180, 320, 320, fill="cyan", width=3, tags="dessin")
            self.canvas.create_line(180, 320, 320, 180, fill="cyan", width=3, tags="dessin")
        elif val == "Barre a roue":
            self.canvas.create_line(150, 250, 350, 250, fill="orange", width=10, tags="dessin")
        else:
            self.canvas.create_rectangle(150, 150, 350, 350, outline="magenta", width=3, tags="dessin")
        self.canvas.update()
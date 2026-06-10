import tkinter as tk
import math
import csv
import os

# Fichier et dimensions
dossier = os.path.dirname(__file__)
fichier_csv = os.path.join(dossier, "etoile-symbole (1).csv")

L, H = 600, 600
CX, CY = 300, 300
R_MAX = 250
PAS_LED = R_MAX / 10 # 10 leds par branche

table_points = {}

# Lecture du CSV
try:
    with open(fichier_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for lg in reader:
            if len(lg) >= 4:
                try:
                    r_brut = float(lg[1].replace(",", "."))
                    deg_brut = float(lg[2].replace(",", "."))
                    stylo = int(lg[3])
                    
                    if stylo == 1:
                        # Arrondi pour trouver l'index de la LED (1 à 10)
                        num_led = max(1, min(10, int(r_brut / 3.0)))
                        angle = int(deg_brut) % 360
                        
                        if angle not in table_points:
                            table_points[angle] = []
                        table_points[angle].append(num_led)
                except:
                    pass
except:
    print("Erreur de chargement du fichier CSV.")

# Fenêtre Tkinter
root = tk.Tk()
root.title("Simu POV - 4 Branches")
canvas = tk.Canvas(root, width=L, height=H, bg="black")
canvas.pack(padx=10, pady=10)

angle_m = 0

def rotation():
    global angle_m
    canvas.delete("pale") # On efface uniquement les lignes des bras gris
    
    # On gère les 4 branches de la croix
    for i in range(4):
        angle_p = (angle_m + (i * 90)) % 360
        rad = math.radians(angle_p)
        
        # Dessin de la structure de la pale
        x_bout = CX + R_MAX * math.cos(rad)
        y_bout = CY - R_MAX * math.sin(rad)
        canvas.create_line(CX, CY, x_bout, y_bout, fill="#222222", width=2, tags="pale")
        
        # Vérification des LEDs à allumer pour cet angle précis
        if angle_p in table_points:
            for led in table_points[angle_p]:
                dist = led * PAS_LED
                x_led = CX + dist * math.cos(rad)
                y_led = CY - dist * math.sin(rad)
                # Point lumineux sans tag "pale" pour créer la persistance rétinienne
                canvas.create_oval(x_led-4, y_led-4, x_led+4, y_led+4, fill="lime", outline="lime")
                
    angle_m = (angle_m + 1) % 360
    root.after(10, rotation)

rotation()
root.mainloop()
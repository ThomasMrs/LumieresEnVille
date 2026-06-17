"""Convertit un fichier SVG (paths en courbes de Bezier) en une forme
au format du projet : lignes 'label;x;y;actif'.

- Chaque sous-chemin (commande M) demarre par un point 'stylo leve' (actif=0)
  puis trace les points suivants en actif=1 : les morceaux disjoints
  (corps, yeux, nez...) ne sont donc pas relies par un trait.
- Les coordonnees SVG (y vers le bas) sont mises a l'echelle dans [0, TAILLE]
  et l'axe y est inverse pour que la forme soit a l'endroit.
"""
import re
import sys

TAILLE = 100.0          # boite cible (0..TAILLE)
PAS_BEZIER = 8          # nb de segments par courbe (plus grand = plus precis)


def lire_paths(chemin_svg):
    texte = open(chemin_svg, encoding="utf-8").read()
    return re.findall(r'<path[^>]*\sd="([^"]+)"', texte)


def tokens(d):
    """Decoupe une chaine 'd' en commandes (lettres) et nombres (float)."""
    for t in re.findall(r"[MmLlHhVvCcSsZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d):
        yield t


def bezier_cubique(p0, p1, p2, p3, pas):
    pts = []
    for i in range(1, pas + 1):
        t = i / pas
        u = 1 - t
        x = (u**3 * p0[0] + 3 * u**2 * t * p1[0]
             + 3 * u * t**2 * p2[0] + t**3 * p3[0])
        y = (u**3 * p0[1] + 3 * u**2 * t * p1[1]
             + 3 * u * t**2 * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


def parser_path(d):
    """Renvoie une liste de sous-chemins ; chaque sous-chemin = liste de (x, y)."""
    it = list(tokens(d))
    i = 0
    cmd = None
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    prev_ctrl = None
    sous_chemins = []
    courant = None

    def nb():
        nonlocal i
        v = float(it[i]); i += 1
        return v

    while i < len(it):
        if re.match(r"[A-Za-z]", it[i]):
            cmd = it[i]; i += 1
        rel = cmd.islower()

        if cmd in ("M", "m"):
            x = nb(); y = nb()
            if rel:
                x += cur[0]; y += cur[1]
            cur = (x, y); start = cur
            courant = [cur]
            sous_chemins.append(courant)
            prev_ctrl = None
            cmd = "l" if cmd == "m" else "L"  # les coords suivantes = lineto
        elif cmd in ("L", "l"):
            x = nb(); y = nb()
            if rel:
                x += cur[0]; y += cur[1]
            cur = (x, y); courant.append(cur); prev_ctrl = None
        elif cmd in ("H", "h"):
            x = nb()
            if rel:
                x += cur[0]
            cur = (x, cur[1]); courant.append(cur); prev_ctrl = None
        elif cmd in ("V", "v"):
            y = nb()
            if rel:
                y += cur[1]
            cur = (cur[0], y); courant.append(cur); prev_ctrl = None
        elif cmd in ("C", "c"):
            c1 = (nb(), nb()); c2 = (nb(), nb()); end = (nb(), nb())
            if rel:
                c1 = (c1[0] + cur[0], c1[1] + cur[1])
                c2 = (c2[0] + cur[0], c2[1] + cur[1])
                end = (end[0] + cur[0], end[1] + cur[1])
            courant += bezier_cubique(cur, c1, c2, end, PAS_BEZIER)
            cur = end; prev_ctrl = c2
        elif cmd in ("S", "s"):
            c2 = (nb(), nb()); end = (nb(), nb())
            if rel:
                c2 = (c2[0] + cur[0], c2[1] + cur[1])
                end = (end[0] + cur[0], end[1] + cur[1])
            c1 = cur if prev_ctrl is None else (2 * cur[0] - prev_ctrl[0],
                                                2 * cur[1] - prev_ctrl[1])
            courant += bezier_cubique(cur, c1, c2, end, PAS_BEZIER)
            cur = end; prev_ctrl = c2
        elif cmd in ("Z", "z"):
            courant.append(start); cur = start; prev_ctrl = None
        else:
            i += 1  # securite
    return sous_chemins


def convertir(chemin_svg):
    sous_chemins = []
    for d in lire_paths(chemin_svg):
        sous_chemins += parser_path(d)

    # Bornes globales pour la mise a l'echelle
    xs = [p[0] for sc in sous_chemins for p in sc]
    ys = [p[1] for sc in sous_chemins for p in sc]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    echelle = TAILLE / max(maxx - minx, maxy - miny)

    lignes = []
    n = 0
    for sc in sous_chemins:
        for k, (x, y) in enumerate(sc):
            sx = round((x - minx) * echelle, 1)
            sy = round((maxy - y) * echelle, 1)   # inversion de l'axe y
            n += 1
            actif = 0 if k == 0 else 1            # 1er point = stylo leve
            lignes.append(f"P{n};{sx};{sy};{actif}")
    return "\n".join(lignes)


if __name__ == "__main__":
    print(convertir(sys.argv[1]))

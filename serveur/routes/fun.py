"""Pages "troll" accessibles depuis l'IHM : Star Wars, Pokemon, Airbus.
Routes purement decoratives (GET), independantes de la logique metier.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api", tags=["Fun"])


def page(titre: str, corps: str, fond: str) -> str:
    """Squelette commun : titre, fond colore, contenu et bouton retour IHM."""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titre}</title>
    <link rel="stylesheet" href="/style.css">
    <style>
        body {{
            display: block;
            max-width: 760px;
            text-align: center;
            background: {fond};
        }}
        .troll {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 18px;
            padding: 36px 30px;
            box-shadow: 0 18px 50px -15px rgba(0,0,0,0.5);
        }}
        .troll h1 {{ font-size: 2rem; justify-content: center; }}
        .troll p {{ font-size: 1.1rem; line-height: 1.7; margin: 14px 0; }}
        .troll .gros {{ font-size: 3rem; margin: 10px 0; }}
        .troll blockquote {{
            font-style: italic; color: #475569;
            border-left: 4px solid #6366f1; padding-left: 14px; text-align: left;
        }}
        .retour {{
            display: inline-block; margin-top: 24px; text-decoration: none;
        }}
        .retour button {{ margin: 0; }}
    </style>
</head>
<body>
    <section class="troll">
        {corps}
        <a class="retour" href="/api/ihm">
            <button type="button">&larr; Retour a l'IHM</button>
        </a>
    </section>
</body>
</html>
"""


@router.get("/ihm/starwars", response_class=HTMLResponse)
def page_starwars():
    corps = """
        <h1>Star Wars : Boss Final 🚀</h1>
        <p>Pilote ton <b>X-Wing</b> et affronte <b>Mathieu, Maître des Sites</b> !<br>
           ⬅️ ➡️ pour bouger, <b>Espace</b> pour tirer. (Souris aussi)</p>

        <canvas id="space" width="420" height="520"
                style="border-radius:14px; background:#03040d; cursor:crosshair;
                       box-shadow:0 10px 30px -8px rgba(0,0,0,.6); touch-action:none;">
        </canvas>
        <p id="hud" style="font-size:1.1rem; font-weight:700; margin-top:12px;">
            Score : 0 &nbsp;•&nbsp; Vies : ❤️❤️❤️
        </p>
        <button type="button" id="rejouer-sw" style="display:none; margin-top:6px;">🔄 Rejouer</button>

        <script>
        (function () {
            const canvas = document.getElementById('space');
            const ctx = canvas.getContext('2d');
            const W = canvas.width, H = canvas.height;
            const hud = document.getElementById('hud');
            const rejouer = document.getElementById('rejouer-sw');

            let joueur, boss, tirsJ, tirsB, etoiles, etat, score, frame, clavier;

            function nouvellesEtoiles() {
                const arr = [];
                for (let i = 0; i < 70; i++) {
                    arr.push({ x: Math.random() * W, y: Math.random() * H,
                               v: 0.4 + Math.random() * 1.6, t: Math.random() * 2 + 0.6 });
                }
                return arr;
            }

            function init() {
                joueur = { x: W / 2, y: H - 50, w: 34, h: 28, vies: 3, cooldown: 0, invincible: 0 };
                boss = { x: W / 2, y: 70, w: 90, h: 60, pv: 200, max: 200, dir: 1, cadence: 0, phase: 0 };
                tirsJ = [];
                tirsB = [];
                etoiles = nouvellesEtoiles();
                score = 0;
                frame = 0;
                etat = 'jeu';   // 'jeu' | 'gagne' | 'perdu'
                clavier = {};
                rejouer.style.display = 'none';
                majHud();
            }

            function majHud() {
                const coeurs = '❤️'.repeat(Math.max(0, joueur.vies)) || '💀';
                hud.textContent = 'Score : ' + score + '  •  Vies : ' + coeurs;
            }

            function tirerJoueur() {
                if (joueur.cooldown > 0) return;
                tirsJ.push({ x: joueur.x, y: joueur.y - 18, v: 8 });
                joueur.cooldown = 9;
            }

            function tirerBoss() {
                // salve dirigee vers le joueur + dispersion
                const dx = joueur.x - boss.x;
                const dist = Math.max(1, Math.hypot(dx, joueur.y - boss.y));
                for (let k = -1; k <= 1; k++) {
                    tirsB.push({
                        x: boss.x + k * 24, y: boss.y + boss.h / 2,
                        vx: (dx / dist) * 2.2 + k * 1.1, vy: 3.4 + Math.random()
                    });
                }
            }

            function collision(ax, ay, aw, ah, bx, by, bw, bh) {
                return Math.abs(ax - bx) < (aw + bw) / 2 && Math.abs(ay - by) < (ah + bh) / 2;
            }

            function maj() {
                frame++;
                // etoiles defilantes
                for (const e of etoiles) {
                    e.y += e.v;
                    if (e.y > H) { e.y = 0; e.x = Math.random() * W; }
                }
                if (etat !== 'jeu') return;

                // deplacement joueur
                if (clavier['ArrowLeft'] || clavier['a']) joueur.x -= 5.5;
                if (clavier['ArrowRight'] || clavier['d']) joueur.x += 5.5;
                joueur.x = Math.max(joueur.w / 2, Math.min(W - joueur.w / 2, joueur.x));
                if (clavier[' ']) tirerJoueur();
                if (joueur.cooldown > 0) joueur.cooldown--;
                if (joueur.invincible > 0) joueur.invincible--;

                // boss : va-et-vient + accelere quand blesse
                const rage = 1 + (1 - boss.pv / boss.max);
                boss.x += boss.dir * 1.8 * rage;
                if (boss.x < boss.w / 2 + 6) { boss.x = boss.w / 2 + 6; boss.dir = 1; }
                if (boss.x > W - boss.w / 2 - 6) { boss.x = W - boss.w / 2 - 6; boss.dir = -1; }
                boss.cadence++;
                if (boss.cadence > Math.max(28, 70 - score)) { boss.cadence = 0; tirerBoss(); }

                // tirs joueur
                for (const t of tirsJ) t.y -= t.v;
                tirsJ = tirsJ.filter(t => t.y > -20);
                for (const t of tirsJ) {
                    if (collision(t.x, t.y, 6, 14, boss.x, boss.y, boss.w, boss.h)) {
                        t.y = -999;
                        boss.pv -= 6;
                        score += 5;
                        if (boss.pv <= 0) { boss.pv = 0; etat = 'gagne'; finir(); }
                    }
                }
                tirsJ = tirsJ.filter(t => t.y > -900);
                majHud();

                // tirs boss
                for (const t of tirsB) { t.x += t.vx; t.y += t.vy; }
                tirsB = tirsB.filter(t => t.y < H + 20 && t.x > -20 && t.x < W + 20);
                for (const t of tirsB) {
                    if (joueur.invincible <= 0 &&
                        collision(t.x, t.y, 8, 8, joueur.x, joueur.y, joueur.w * 0.7, joueur.h * 0.7)) {
                        t.y = H + 999;
                        joueur.vies--;
                        joueur.invincible = 70;
                        majHud();
                        if (joueur.vies <= 0) { etat = 'perdu'; finir(); }
                    }
                }
                tirsB = tirsB.filter(t => t.y < H + 900);
            }

            function finir() {
                rejouer.style.display = 'inline-block';
            }

            function dessinerVaisseauJoueur() {
                if (joueur.invincible > 0 && Math.floor(frame / 4) % 2 === 0) return;
                ctx.save();
                ctx.translate(joueur.x, joueur.y);
                // X-Wing stylise
                ctx.fillStyle = '#cbd5e1';
                ctx.beginPath();
                ctx.moveTo(0, -18); ctx.lineTo(8, 10); ctx.lineTo(-8, 10); ctx.closePath();
                ctx.fill();
                ctx.fillStyle = '#ef4444';
                ctx.fillRect(-16, 4, 32, 5);          // ailes
                ctx.fillStyle = '#38bdf8';
                ctx.beginPath(); ctx.arc(0, -6, 4, 0, Math.PI * 2); ctx.fill();   // cockpit
                // reacteur
                ctx.fillStyle = 'rgba(56,189,248,.8)';
                ctx.fillRect(-3, 10, 6, 6 + Math.random() * 6);
                ctx.restore();
            }

            function dessinerBoss() {
                ctx.save();
                ctx.translate(boss.x, boss.y);
                // soucoupe sombre
                ctx.fillStyle = '#1e293b';
                ctx.beginPath();
                ctx.ellipse(0, 0, boss.w / 2, boss.h / 2, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#334155';
                ctx.beginPath();
                ctx.ellipse(0, -8, boss.w / 3.2, boss.h / 3, 0, 0, Math.PI * 2);
                ctx.fill();
                // oeil rouge de Mathieu
                ctx.fillStyle = '#f87171';
                ctx.beginPath(); ctx.arc(0, -8, 7, 0, Math.PI * 2); ctx.fill();
                // hublots
                ctx.fillStyle = '#fbbf24';
                for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.arc(i * 16, 10, 3, 0, Math.PI * 2); ctx.fill(); }
                ctx.restore();

                // nom + barre de PV du boss
                ctx.fillStyle = '#e2e8f0';
                ctx.font = 'bold 13px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('☠️ MATHIEU, MAITRE DES SITES', W / 2, 18);
                ctx.fillStyle = '#7f1d1d';
                ctx.fillRect(W / 2 - 130, 24, 260, 8);
                ctx.fillStyle = '#ef4444';
                ctx.fillRect(W / 2 - 130, 24, 260 * (boss.pv / boss.max), 8);
            }

            function dessiner() {
                ctx.clearRect(0, 0, W, H);
                // etoiles
                for (const e of etoiles) {
                    ctx.fillStyle = 'rgba(255,255,255,' + (0.3 + e.v / 3) + ')';
                    ctx.fillRect(e.x, e.y, e.t, e.t);
                }
                // tirs joueur (lasers rouges)
                ctx.fillStyle = '#fca5a5';
                for (const t of tirsJ) ctx.fillRect(t.x - 2, t.y - 8, 4, 14);
                // tirs boss (lasers verts)
                for (const t of tirsB) {
                    ctx.fillStyle = '#4ade80';
                    ctx.fillRect(t.x - 3, t.y - 3, 6, 8);
                }

                dessinerBoss();
                if (etat !== 'perdu') dessinerVaisseauJoueur();

                if (etat === 'gagne') {
                    ctx.fillStyle = 'rgba(0,0,0,.55)';
                    ctx.fillRect(0, 0, W, H);
                    ctx.fillStyle = '#fde047';
                    ctx.font = 'bold 30px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('🏆 VICTOIRE !', W / 2, H / 2 - 14);
                    ctx.fillStyle = '#e2e8f0';
                    ctx.font = '16px sans-serif';
                    ctx.fillText('Mathieu a perdu ses droits admin.', W / 2, H / 2 + 16);
                    ctx.fillText('Score : ' + score, W / 2, H / 2 + 42);
                } else if (etat === 'perdu') {
                    ctx.fillStyle = 'rgba(0,0,0,.6)';
                    ctx.fillRect(0, 0, W, H);
                    ctx.fillStyle = '#f87171';
                    ctx.font = 'bold 28px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('💥 GAME OVER', W / 2, H / 2 - 14);
                    ctx.fillStyle = '#e2e8f0';
                    ctx.font = '16px sans-serif';
                    ctx.fillText('Mathieu a pushé en force sur main...', W / 2, H / 2 + 16);
                    ctx.fillText('Score : ' + score, W / 2, H / 2 + 42);
                }
            }

            function boucle() {
                maj();
                dessiner();
                requestAnimationFrame(boucle);
            }

            // controles
            window.addEventListener('keydown', function (e) {
                clavier[e.key] = true;
                if (e.key === ' ' || e.key.startsWith('Arrow')) e.preventDefault();
            });
            window.addEventListener('keyup', function (e) { clavier[e.key] = false; });
            canvas.addEventListener('mousemove', function (e) {
                if (etat !== 'jeu') return;
                const r = canvas.getBoundingClientRect();
                joueur.x = Math.max(joueur.w / 2, Math.min(W - joueur.w / 2,
                           (e.clientX - r.left) * (W / r.width)));
            });
            canvas.addEventListener('mousedown', tirerJoueur);
            rejouer.addEventListener('click', init);

            init();
            boucle();
        })();
        </script>
    """
    return page("Star Wars", corps, "radial-gradient(circle at 50% 0%, #1e293b, #000)")


@router.get("/ihm/pokemon", response_class=HTMLResponse)
def page_pokemon():
    corps = """
        <h1>Combat Pokémon ⚡</h1>
        <p>Un <b>Stormtrooper</b> sauvage te barre la route !</p>

        <div id="arene" style="position:relative; background:linear-gradient(#bae6fd,#dcfce7);
             border-radius:16px; padding:18px; box-shadow:inset 0 0 30px rgba(0,0,0,.1);">

            <!-- Ennemi : Stormtrooper -->
            <div style="text-align:right;">
                <div style="display:inline-block; background:#fff; border:2px solid #334155;
                     border-radius:10px; padding:8px 12px; text-align:left; min-width:190px;">
                    <b>Stormtrooper</b> Nv.66
                    <div style="background:#e2e8f0; border-radius:6px; height:12px; margin-top:5px; overflow:hidden;">
                        <div id="pv-ennemi-barre" style="height:100%; width:100%; background:#22c55e;"></div>
                    </div>
                    <span id="pv-ennemi-txt" style="font-size:.8rem;">100 / 100</span>
                </div>
                <div id="sprite-ennemi" style="font-size:4rem; line-height:1;">🥷</div>
            </div>

            <!-- Joueur : Pikachu -->
            <div style="text-align:left; margin-top:6px;">
                <div id="sprite-joueur" style="font-size:4rem; line-height:1;">⚡🐭</div>
                <div style="display:inline-block; background:#fff; border:2px solid #334155;
                     border-radius:10px; padding:8px 12px; text-align:left; min-width:190px;">
                    <b>Pikachu</b> Nv.50
                    <div style="background:#e2e8f0; border-radius:6px; height:12px; margin-top:5px; overflow:hidden;">
                        <div id="pv-joueur-barre" style="height:100%; width:100%; background:#22c55e;"></div>
                    </div>
                    <span id="pv-joueur-txt" style="font-size:.8rem;">100 / 100</span>
                </div>
            </div>
        </div>

        <!-- Journal de combat -->
        <div id="journal" style="background:#0f172a; color:#e2e8f0; text-align:left;
             border-radius:12px; padding:12px 14px; margin-top:14px; min-height:60px; font-size:.95rem;">
            Que va faire Pikachu ?
        </div>

        <!-- Attaques -->
        <div id="attaques" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:14px;">
            <button type="button" data-i="0">⚡ Éclair</button>
            <button type="button" data-i="1">💥 Charge</button>
            <button type="button" data-i="2">🌩️ Tonnerre</button>
            <button type="button" data-i="3">🎮 Frappe Pixel</button>
        </div>
        <button type="button" id="rejouer" style="display:none; margin-top:12px;">🔄 Rejouer</button>

        <script>
        (function () {
            const ATTAQUES = [
                { nom: 'Éclair',       min: 12, max: 20, prec: 1.0 },
                { nom: 'Charge',       min: 8,  max: 15, prec: 1.0 },
                { nom: 'Tonnerre',     min: 22, max: 34, prec: 0.7 },
                { nom: 'Frappe Pixel', min: 14, max: 24, prec: 0.9 }
            ];

            const joueur = { pv: 100, max: 100 };
            const ennemi = { pv: 100, max: 100 };
            let tourEnCours = false;

            const elJoueurBarre = document.getElementById('pv-joueur-barre');
            const elJoueurTxt = document.getElementById('pv-joueur-txt');
            const elEnnemiBarre = document.getElementById('pv-ennemi-barre');
            const elEnnemiTxt = document.getElementById('pv-ennemi-txt');
            const journal = document.getElementById('journal');
            const boutons = Array.from(document.querySelectorAll('#attaques button'));
            const rejouer = document.getElementById('rejouer');

            function alea(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

            function couleurBarre(pct) {
                if (pct > 50) return '#22c55e';
                if (pct > 20) return '#facc15';
                return '#ef4444';
            }

            function majBarres() {
                const pj = Math.max(0, joueur.pv) / joueur.max * 100;
                const pe = Math.max(0, ennemi.pv) / ennemi.max * 100;
                elJoueurBarre.style.width = pj + '%';
                elJoueurBarre.style.background = couleurBarre(pj);
                elJoueurTxt.textContent = Math.max(0, joueur.pv) + ' / ' + joueur.max;
                elEnnemiBarre.style.width = pe + '%';
                elEnnemiBarre.style.background = couleurBarre(pe);
                elEnnemiTxt.textContent = Math.max(0, ennemi.pv) + ' / ' + ennemi.max;
            }

            function log(txt) { journal.innerHTML = txt; }

            function activerBoutons(actif) {
                boutons.forEach(b => b.disabled = !actif);
            }

            function finPartie(victoire) {
                activerBoutons(false);
                rejouer.style.display = 'inline-block';
                if (victoire) {
                    document.getElementById('sprite-ennemi').textContent = '💫';
                    log('🎉 Le Stormtrooper est K.O. ! La Force n\\'a rien pu faire contre la foudre. Pikachu gagne !');
                } else {
                    document.getElementById('sprite-joueur').textContent = '😵';
                    log('💀 Pikachu est K.O. ! Pour une fois, un Stormtrooper a visé juste...');
                }
            }

            function riposteEnnemi() {
                // Running gag : les Stormtroopers ratent (presque) toujours leur cible.
                if (Math.random() < 0.45) {
                    log('Le Stormtrooper tire au blaster... et rate complètement ! 😅 (À ton tour)');
                    activerBoutons(true);
                    tourEnCours = false;
                    return;
                }
                const degats = alea(6, 16);
                ennemi.degats = degats;
                joueur.pv -= degats;
                majBarres();
                log('🔫 Le Stormtrooper touche Pikachu (' + degats + ' dégâts).');
                if (joueur.pv <= 0) { majBarres(); return finPartie(false); }
                setTimeout(function () {
                    log('Que va faire Pikachu ?');
                    activerBoutons(true);
                    tourEnCours = false;
                }, 700);
            }

            function attaquer(i) {
                if (tourEnCours) return;
                tourEnCours = true;
                activerBoutons(false);
                const atk = ATTAQUES[i];
                if (Math.random() > atk.prec) {
                    log('Pikachu utilise ' + atk.nom + '... mais l\\'attaque échoue ! 💨');
                } else {
                    const degats = alea(atk.min, atk.max);
                    ennemi.pv -= degats;
                    majBarres();
                    log('⚡ Pikachu utilise ' + atk.nom + ' ! (' + degats + ' dégâts)');
                    if (ennemi.pv <= 0) { majBarres(); return finPartie(true); }
                }
                setTimeout(riposteEnnemi, 800);
            }

            function init() {
                joueur.pv = joueur.max;
                ennemi.pv = ennemi.max;
                tourEnCours = false;
                document.getElementById('sprite-ennemi').textContent = '🥷';
                document.getElementById('sprite-joueur').textContent = '⚡🐭';
                rejouer.style.display = 'none';
                majBarres();
                log('Un Stormtrooper sauvage apparaît ! Que va faire Pikachu ?');
                activerBoutons(true);
            }

            boutons.forEach(b => b.addEventListener('click', () => attaquer(parseInt(b.dataset.i))));
            rejouer.addEventListener('click', init);
            init();
        })();
        </script>
    """
    return page("Combat Pokemon", corps, "linear-gradient(135deg, #ef4444, #fbbf24)")


@router.get("/ihm/airbus", response_class=HTMLResponse)
def page_airbus():
    corps = """
        <h1>Flappy Airbus ✈️</h1>
        <p>Clique, tape <b>Espace</b> ou touche l'écran pour faire monter l'avion.<br>
           Évite les tours de contrôle ! 🗼</p>

        <style>
            #scene { display:inline-block; line-height:0; border-radius:14px;
                     box-shadow:0 10px 30px -10px rgba(0,0,0,.4); }
            #scene:fullscreen, #scene:-webkit-full-screen {
                display:flex; align-items:center; justify-content:center;
                width:100vw; height:100vh; background:#03040d; box-shadow:none; border-radius:0; }
            #jeu { border-radius:14px; background:#bff0ff; cursor:pointer; touch-action:manipulation; }
        </style>

        <div id="scene">
            <canvas id="jeu" width="360" height="480"></canvas>
        </div>

        <div style="margin-top:12px;">
            <button type="button" id="plein-ecran">⛶ Plein écran</button>
        </div>
        <p id="score" style="font-size:1.3rem; font-weight:700; margin-top:12px;">Score : 0 &nbsp;•&nbsp; Record : 0</p>
        <a id="postuler" href="https://www.airbus.com/en/careers" target="_blank" rel="noopener"
           style="display:none; text-decoration:none;">
            <button type="button" style="background:linear-gradient(135deg,#0ea5e9,#0369a1);">
                ✈️ Trop nul en vol ? Postule chez Airbus !
            </button>
        </a>

        <script>
        (function () {
            const canvas = document.getElementById('jeu');
            const ctx = canvas.getContext('2d');
            const W = canvas.width, H = canvas.height;
            const scoreEl = document.getElementById('score');
            const postulerEl = document.getElementById('postuler');

            const GRAVITE = 0.42, POUSSEE = -7.0, SOL = 46;
            const LARG_TOUR = 58;
            const PROF_X = 14, PROF_Y = -10;   // vecteur d'extrusion 3D (vers le coin sup. droit)
            const PAS = 1000 / 60;             // pas de simulation fixe -> vitesse stable a tout FPS

            let avion, tours, score, record = 0, etat;   // etat: 'pret' | 'jeu' | 'mort'
            let particules, trainee, secousse, flashSol, nuages, fondX;
            let bonus, bouclier, ralenti;   // bouclier/ralenti : compteurs de frames restantes
            let fps = 60;

            try { record = parseInt(localStorage.getItem('flappyAirbusRecord') || '0') || 0; } catch (e) {}

            // --- Difficulte progressive (ralentie par le bonus slow-mo) ---
            function vitesseJeu()  {
                const base = 2.3 + Math.min(2.0, score * 0.04);   // accelere
                return ralenti > 0 ? base * 0.55 : base;
            }
            function ecartTrou()   { return Math.max(118, 168 - score * 1.5); }    // se resserre

            function init() {
                avion = { x: 92, y: H / 2, vy: 0, r: 15, batt: 0 };
                tours = [];
                for (let i = 0; i < 3; i++) tours.push(creerTour(W + 60 + i * 200));
                particules = [];
                trainee = [];
                nuages = [
                    { x: 60,  y: 70,  v: 0.25, s: 1.0 },
                    { x: 230, y: 130, v: 0.18, s: 0.7 },
                    { x: 320, y: 50,  v: 0.30, s: 1.2 }
                ];
                bonus = [];
                bouclier = 0;
                ralenti = 0;
                for (const t of tours) creerBonus(t.x, t.trou, t.ecart);
                score = 0;
                secousse = 0;
                flashSol = 0;
                fondX = 0;
                etat = 'pret';
                majScore();
            }

            const TYPES_BONUS = {
                etoile:   { emoji: '⭐', couleur: '#fbbf24' },
                bouclier: { emoji: '🛡️', couleur: '#38bdf8' },
                ralenti:  { emoji: '⏳', couleur: '#a78bfa' }
            };

            function creerBonus(x, yTrou, ecart) {
                // 45% de chance d'apparaitre, au centre du trou de la tour
                if (Math.random() > 0.45) return;
                const r = Math.random();
                const type = r < 0.55 ? 'etoile' : (r < 0.8 ? 'bouclier' : 'ralenti');
                bonus.push({ x: x + LARG_TOUR / 2, y: yTrou + ecart / 2, type: type, pris: false, pulse: Math.random() * 6 });
            }

            function majScore() {
                scoreEl.textContent = 'Score : ' + score + '  •  Record : ' + record;
            }

            function creerTour(x) {
                const ec = ecartTrou();
                const trou = 60 + Math.random() * (H - SOL - ec - 120);
                return { x: x, trou: trou, ecart: ec, passe: false, teinte: 200 + Math.random() * 20 };
            }

            function pousser() {
                if (etat === 'mort') { init(); return; }
                if (etat === 'pret') etat = 'jeu';
                avion.vy = POUSSEE;
                avion.batt = 6;
                // petites volutes facon reacteur a chaque battement
                for (let i = 0; i < 5; i++) {
                    particules.push({
                        x: avion.x - 14, y: avion.y + 6,
                        vx: -1.5 - Math.random() * 1.5, vy: (Math.random() - 0.5) * 2,
                        vie: 22, max: 22, r: 3 + Math.random() * 2, type: 'fumee'
                    });
                }
            }

            function exploser() {
                secousse = 14;
                for (let i = 0; i < 34; i++) {
                    const a = Math.random() * Math.PI * 2, v = 1.5 + Math.random() * 5;
                    particules.push({
                        x: avion.x, y: avion.y,
                        vx: Math.cos(a) * v, vy: Math.sin(a) * v,
                        vie: 40, max: 40, r: 2 + Math.random() * 4,
                        type: Math.random() < 0.6 ? 'feu' : 'debris'
                    });
                }
            }

            function rectsSeChevauchent(ax, ay, aw, ah, bx, by, bw, bh) {
                return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
            }

            function mourir() {
                if (etat === 'mort') return;
                etat = 'mort';
                flashSol = 1;
                exploser();
                if (score > record) {
                    record = score;
                    try { localStorage.setItem('flappyAirbusRecord', String(record)); } catch (e) {}
                }
                majScore();
            }

            function maj() {
                // particules toujours animees (meme apres le crash)
                for (const p of particules) {
                    p.x += p.vx; p.y += p.vy; p.vie--;
                    if (p.type !== 'fumee') p.vy += 0.12;
                }
                particules = particules.filter(p => p.vie > 0);
                if (secousse > 0) secousse *= 0.85;
                if (flashSol > 0) flashSol *= 0.92;

                // nuages parallaxe (toujours)
                for (const n of nuages) {
                    n.x -= n.v * (etat === 'jeu' ? 2 : 1);
                    if (n.x < -70) { n.x = W + 40; n.y = 40 + Math.random() * 150; }
                }

                if (etat !== 'jeu') return;
                fondX = (fondX + vitesseJeu() * 0.5) % 170;

                if (bouclier > 0) bouclier--;
                if (ralenti > 0) ralenti--;

                avion.vy += GRAVITE;
                avion.y += avion.vy;
                if (avion.batt > 0) avion.batt--;

                // trainee de condensation
                trainee.push({ x: avion.x - 16, y: avion.y + 5, vie: 16 });
                if (trainee.length > 18) trainee.shift();
                for (const t of trainee) t.vie--;

                const v = vitesseJeu();
                for (const t of tours) {
                    t.x -= v;
                    if (!t.passe && t.x + LARG_TOUR < avion.x) {
                        t.passe = true;
                        score++;
                        majScore();
                        // etincelles vertes de score
                        for (let i = 0; i < 8; i++) particules.push({
                            x: avion.x, y: avion.y,
                            vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3 - 1,
                            vie: 26, max: 26, r: 2 + Math.random() * 2, type: 'score'
                        });
                    }
                    const bx = avion.x - avion.r + 3, by = avion.y - avion.r + 3, bw = avion.r * 2 - 6, bh = avion.r * 2 - 6;
                    const basY = t.trou + t.ecart;
                    if (bouclier <= 0 &&
                        (rectsSeChevauchent(bx, by, bw, bh, t.x, 0, LARG_TOUR, t.trou) ||
                         rectsSeChevauchent(bx, by, bw, bh, t.x, basY, LARG_TOUR, H - basY - SOL))) {
                        return mourir();
                    }
                }
                if (tours.length && tours[0].x + LARG_TOUR < 0) {
                    tours.shift();
                    const nv = creerTour(tours[tours.length - 1].x + 200);
                    tours.push(nv);
                    creerBonus(nv.x, nv.trou, nv.ecart);
                }

                // deplacement + collecte des bonus
                for (const b of bonus) {
                    b.x -= v;
                    b.pulse += 0.15;
                    if (!b.pris && Math.hypot(b.x - avion.x, b.y - avion.y) < avion.r + 16) {
                        b.pris = true;
                        ramasserBonus(b.type);
                    }
                }
                bonus = bonus.filter(b => !b.pris && b.x > -30);

                if (avion.y + avion.r > H - SOL || avion.y - avion.r < 0) {
                    avion.y = Math.min(avion.y, H - SOL - avion.r);
                    if (bouclier > 0) { avion.vy = POUSSEE * 0.7; }   // le bouclier fait rebondir
                    else return mourir();
                }
            }

            function ramasserBonus(type) {
                const conf = TYPES_BONUS[type];
                let couleurP = conf.couleur;
                if (type === 'etoile') { score += 3; majScore(); }
                else if (type === 'bouclier') { bouclier = 360; }   // ~6 s d'invincibilite
                else if (type === 'ralenti') { ralenti = 300; }     // ~5 s de slow-mo
                for (let i = 0; i < 14; i++) {
                    const a = Math.random() * Math.PI * 2, vv = 1 + Math.random() * 3;
                    particules.push({
                        x: avion.x, y: avion.y,
                        vx: Math.cos(a) * vv, vy: Math.sin(a) * vv,
                        vie: 28, max: 28, r: 2 + Math.random() * 2, type: 'bonus', col: couleurP
                    });
                }
            }

            function dessinerNuage(n) {
                ctx.fillStyle = 'rgba(255,255,255,.85)';
                ctx.beginPath();
                ctx.arc(n.x, n.y, 16 * n.s, 0, Math.PI * 2);
                ctx.arc(n.x + 18 * n.s, n.y + 4, 20 * n.s, 0, Math.PI * 2);
                ctx.arc(n.x + 40 * n.s, n.y, 15 * n.s, 0, Math.PI * 2);
                ctx.arc(n.x + 20 * n.s, n.y - 8, 16 * n.s, 0, Math.PI * 2);
                ctx.fill();
            }

            // --- Helpers de rendu 3D (extrusion vers PROF_X / PROF_Y) ---
            function faceCote(x, yHaut, yBas, couleur) {
                ctx.fillStyle = couleur;
                ctx.beginPath();
                ctx.moveTo(x, yHaut);
                ctx.lineTo(x + PROF_X, yHaut + PROF_Y);
                ctx.lineTo(x + PROF_X, yBas + PROF_Y);
                ctx.lineTo(x, yBas);
                ctx.closePath();
                ctx.fill();
            }
            function faceHaut(x, y, w, couleur) {
                ctx.fillStyle = couleur;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + PROF_X, y + PROF_Y);
                ctx.lineTo(x + w + PROF_X, y + PROF_Y);
                ctx.lineTo(x + w, y);
                ctx.closePath();
                ctx.fill();
            }

            function frontTour(x, h0, h1) {
                const g = ctx.createLinearGradient(x, 0, x + LARG_TOUR, 0);
                g.addColorStop(0, 'hsl(215,16%,47%)');
                g.addColorStop(0.5, 'hsl(215,16%,62%)');
                g.addColorStop(1, 'hsl(215,16%,49%)');
                ctx.fillStyle = g;
                ctx.fillRect(x, h0, LARG_TOUR, h1 - h0);
            }

            function dessinerTour(t) {
                const basY = t.trou + t.ecart;
                const xr = t.x + LARG_TOUR;
                const solY = H - SOL;

                // faces laterales (profondeur) - dessinees en premier (derriere)
                faceCote(xr, 0, t.trou, 'hsl(215,16%,33%)');
                faceCote(xr, basY, solY, 'hsl(215,16%,33%)');

                // faces avant
                frontTour(t.x, 0, t.trou);
                frontTour(t.x, basY, solY);

                // fenetres facon tour de controle
                ctx.fillStyle = 'rgba(186,230,253,.6)';
                for (let y = 16; y < t.trou - 16; y += 22)
                    ctx.fillRect(t.x + 10, y, LARG_TOUR - 20, 8);
                for (let y = basY + 20; y < solY - 10; y += 22)
                    ctx.fillRect(t.x + 10, y, LARG_TOUR - 20, 8);

                // chapeau rouge du pilier haut (cote 3D, pas de toit visible : il pointe vers le bas)
                ctx.fillStyle = '#ef4444';
                ctx.fillRect(t.x - 5, t.trou - 14, LARG_TOUR + 10, 14);
                faceCote(xr + 5, t.trou - 14, t.trou, 'hsl(0,72%,46%)');

                // toit rouge du pilier bas (toit eclaire visible -> faceHaut)
                ctx.fillStyle = '#ef4444';
                ctx.fillRect(t.x - 5, basY, LARG_TOUR + 10, 14);
                faceCote(xr + 5, basY, basY + 14, 'hsl(0,72%,46%)');
                faceHaut(t.x - 5, basY, LARG_TOUR + 10, 'hsl(0,85%,72%)');
            }

            function dessinerAvion() {
                ctx.save();
                ctx.translate(avion.x, avion.y);
                const angle = Math.max(-0.5, Math.min(0.95, avion.vy / 11));
                ctx.rotate(angle);
                // fuselage Airbus blanc/bleu
                ctx.fillStyle = '#f8fafc';
                ctx.beginPath();
                ctx.moveTo(-16, 0);
                ctx.quadraticCurveTo(-16, -8, -2, -8);
                ctx.lineTo(16, -5);
                ctx.quadraticCurveTo(22, 0, 16, 5);
                ctx.lineTo(-2, 8);
                ctx.quadraticCurveTo(-16, 8, -16, 0);
                ctx.fill();
                // bande bleue + hublots
                ctx.fillStyle = '#0ea5e9';
                ctx.fillRect(-14, -1.5, 30, 3);
                ctx.fillStyle = '#0369a1';
                for (let i = -10; i < 14; i += 6) { ctx.beginPath(); ctx.arc(i, -3, 1.3, 0, Math.PI * 2); ctx.fill(); }
                // aile (bat plus bas quand on pousse)
                ctx.fillStyle = '#cbd5e1';
                const ay = avion.batt > 0 ? 7 : 4;
                ctx.beginPath();
                ctx.moveTo(-2, 2); ctx.lineTo(-12, ay + 7); ctx.lineTo(4, 3); ctx.fill();
                // derive arriere
                ctx.beginPath();
                ctx.moveTo(-14, -1); ctx.lineTo(-20, -9); ctx.lineTo(-13, -2); ctx.fill();
                ctx.restore();
            }

            function dessiner() {
                ctx.save();
                if (secousse > 0.4)
                    ctx.translate((Math.random() - 0.5) * secousse, (Math.random() - 0.5) * secousse);

                // ciel degrade
                const ciel = ctx.createLinearGradient(0, 0, 0, H);
                ciel.addColorStop(0, '#38bdf8');
                ciel.addColorStop(0.6, '#bae6fd');
                ciel.addColorStop(1, '#e0f2fe');
                ctx.fillStyle = ciel;
                ctx.fillRect(0, 0, W, H);

                // logos AIRBUS en filigrane
                ctx.save();
                ctx.fillStyle = 'rgba(15, 23, 42, .06)';
                ctx.font = 'bold 26px Arial, sans-serif';
                ctx.textAlign = 'left';
                for (let y = 60; y < H; y += 110)
                    for (let x = -170; x < W; x += 170)
                        ctx.fillText('AIRBUS', x + (170 - fondX), y);
                ctx.restore();

                for (const n of nuages) dessinerNuage(n);

                // skyline lointain (parallaxe lente, donne de la profondeur)
                const HAUTEURS = [34, 52, 26, 44, 30, 58, 38];
                const dec2 = (fondX * 0.55) % 80;
                ctx.fillStyle = 'rgba(71,85,105,.22)';
                for (let x = -dec2 - 80; x < W + 80; x += 80) {
                    const idx = ((Math.round((x + dec2) / 80) % HAUTEURS.length) + HAUTEURS.length) % HAUTEURS.length;
                    const bh = HAUTEURS[idx];
                    ctx.fillRect(x, H - SOL - bh, 50, bh);
                    ctx.fillRect(x + 56, H - SOL - bh * 0.7, 18, bh * 0.7);
                }

                for (const t of tours) dessinerTour(t);

                // trainee de condensation
                for (const t of trainee) {
                    ctx.fillStyle = 'rgba(255,255,255,' + (t.vie / 30) + ')';
                    ctx.beginPath(); ctx.arc(t.x, t.y, 4, 0, Math.PI * 2); ctx.fill();
                }

                // sol herbe + piste
                ctx.fillStyle = '#16a34a';
                ctx.fillRect(0, H - SOL, W, SOL);
                ctx.fillStyle = '#15803d';
                ctx.fillRect(0, H - SOL, W, 5);
                ctx.fillStyle = '#334155';
                ctx.fillRect(0, H - 22, W, 22);
                ctx.fillStyle = '#fbbf24';
                const dash = (fondX * 2) % 40;
                for (let x = -dash; x < W; x += 40) ctx.fillRect(x, H - 12, 20, 3);

                // ombre portee de l'avion (depth cue 3D) - plus diffuse en altitude
                if (etat !== 'mort') {
                    const distSol = Math.max(0, (H - SOL) - avion.y);
                    ctx.save();
                    ctx.globalAlpha = Math.max(0.06, 0.32 - distSol * 0.0007);
                    ctx.fillStyle = '#000';
                    ctx.beginPath();
                    ctx.ellipse(avion.x + distSol * 0.12, H - SOL + 5,
                                Math.max(7, 17 - distSol * 0.018), 4, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }

                // bonus flottants
                for (const b of bonus) {
                    const conf = TYPES_BONUS[b.type];
                    const oy = Math.sin(b.pulse) * 4;
                    ctx.save();
                    ctx.globalAlpha = 0.9;
                    ctx.beginPath();
                    ctx.arc(b.x, b.y + oy, 15, 0, Math.PI * 2);
                    ctx.fillStyle = conf.couleur + '33';
                    ctx.fill();
                    ctx.lineWidth = 2; ctx.strokeStyle = conf.couleur; ctx.stroke();
                    ctx.restore();
                    ctx.font = '20px serif';
                    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
                    ctx.fillText(conf.emoji, b.x, b.y + oy + 1);
                    ctx.textBaseline = 'alphabetic';
                }

                // particules
                for (const p of particules) {
                    const a = p.vie / p.max;
                    if (p.type === 'feu')         ctx.fillStyle = 'rgba(' + 251 + ',' + Math.floor(146 * a) + ',0,' + a + ')';
                    else if (p.type === 'debris') ctx.fillStyle = 'rgba(71,85,105,' + a + ')';
                    else if (p.type === 'score')  ctx.fillStyle = 'rgba(34,197,94,' + a + ')';
                    else if (p.type === 'bonus')  { ctx.globalAlpha = a; ctx.fillStyle = p.col; }
                    else                          ctx.fillStyle = 'rgba(226,232,240,' + (a * 0.7) + ')';
                    ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
                    ctx.globalAlpha = 1;
                }

                if (etat !== 'mort') dessinerAvion();

                // bulle de bouclier autour de l'avion
                if (bouclier > 0 && etat !== 'mort') {
                    const clignote = bouclier < 90 && Math.floor(Date.now() / 100) % 2 === 0;
                    if (!clignote) {
                        ctx.save();
                        ctx.beginPath();
                        ctx.arc(avion.x, avion.y, 26, 0, Math.PI * 2);
                        ctx.strokeStyle = 'rgba(56,189,248,.9)';
                        ctx.lineWidth = 2.5; ctx.stroke();
                        ctx.fillStyle = 'rgba(56,189,248,.14)'; ctx.fill();
                        ctx.restore();
                    }
                }

                // flash blanc au crash
                if (flashSol > 0.02) {
                    ctx.fillStyle = 'rgba(255,255,255,' + flashSol + ')';
                    ctx.fillRect(0, 0, W, H);
                }
                ctx.restore();

                // HUD
                ctx.fillStyle = '#0f172a';
                ctx.textAlign = 'center';
                if (etat === 'pret') {
                    ctx.font = 'bold 22px sans-serif';
                    ctx.fillText('Prêt au décollage ?', W / 2, H / 2 - 60);
                    ctx.font = '15px sans-serif';
                    ctx.fillText('Clique / Espace pour voler', W / 2, H / 2 - 36);
                } else if (etat === 'jeu') {
                    ctx.font = 'bold 40px sans-serif';
                    ctx.fillStyle = 'rgba(255,255,255,.85)';
                    ctx.fillText(score, W / 2, 64);
                    ctx.strokeStyle = 'rgba(15,23,42,.4)';
                    ctx.lineWidth = 1.5;
                    ctx.strokeText(score, W / 2, 64);
                    // jauges de bonus actifs en haut a gauche
                    let jy = 16;
                    function jauge(emoji, reste, total, couleur) {
                        ctx.textAlign = 'left';
                        ctx.font = '14px serif';
                        ctx.fillText(emoji, 8, jy + 11);
                        ctx.fillStyle = 'rgba(15,23,42,.25)';
                        ctx.fillRect(28, jy + 2, 64, 8);
                        ctx.fillStyle = couleur;
                        ctx.fillRect(28, jy + 2, 64 * (reste / total), 8);
                        jy += 18;
                    }
                    if (bouclier > 0) jauge('🛡️', bouclier, 360, '#38bdf8');
                    if (ralenti > 0)  jauge('⏳', ralenti, 300, '#a78bfa');
                } else if (etat === 'mort') {
                    ctx.fillStyle = 'rgba(15,23,42,.55)';
                    ctx.fillRect(40, H / 2 - 78, W - 80, 156);
                    ctx.fillStyle = '#fff';
                    ctx.font = 'bold 26px sans-serif';
                    ctx.fillText('💥 Crash !', W / 2, H / 2 - 40);
                    ctx.font = '18px sans-serif';
                    ctx.fillText('Score : ' + score, W / 2, H / 2 - 8);
                    ctx.fillStyle = score >= record && score > 0 ? '#fde047' : '#cbd5e1';
                    ctx.fillText((score >= record && score > 0 ? '🏆 Nouveau record !' : 'Record : ' + record), W / 2, H / 2 + 18);
                    ctx.fillStyle = '#fff';
                    ctx.font = '15px sans-serif';
                    ctx.fillText('Clique pour rejouer', W / 2, H / 2 + 48);
                }

                // compteur FPS (toujours visible, en haut a droite)
                ctx.fillStyle = 'rgba(15,23,42,.55)';
                ctx.font = 'bold 12px monospace';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'alphabetic';
                ctx.fillText(fps + ' FPS', W - 8, 16);
            }

            // --- Boucle a pas fixe : la physique avance a 60 Hz quel que soit le rafraichissement ---
            let tPrec = performance.now(), reste = 0, fAccum = 0, fCompte = 0;

            function boucle(t) {
                if (t === undefined) t = performance.now();
                let dt = t - tPrec;
                tPrec = t;
                if (dt > 200) dt = 200;   // evite un saut geant apres un onglet en arriere-plan

                // mesure du FPS (lissee sur ~250 ms)
                fAccum += dt; fCompte++;
                if (fAccum >= 250) { fps = Math.round(1000 * fCompte / fAccum); fAccum = 0; fCompte = 0; }

                reste += dt;
                let pas = 0;
                while (reste >= PAS && pas < 5) { maj(); reste -= PAS; pas++; }

                dessiner();
                postulerEl.style.display = (etat === 'mort') ? 'inline-block' : 'none';
                requestAnimationFrame(boucle);
            }

            // --- Plein ecran ---
            const scene = document.getElementById('scene');
            const btnPlein = document.getElementById('plein-ecran');

            function plein() {
                const actif = document.fullscreenElement || document.webkitFullscreenElement;
                if (actif) {
                    (document.exitFullscreen || document.webkitExitFullscreen).call(document);
                } else {
                    (scene.requestFullscreen || scene.webkitRequestFullscreen).call(scene);
                }
            }

            function ajusterTaille() {
                const actif = document.fullscreenElement || document.webkitFullscreenElement;
                if (actif) {
                    const ratio = W / H;
                    let h = window.innerHeight * 0.98, w = h * ratio;
                    if (w > window.innerWidth) { w = window.innerWidth * 0.98; h = w / ratio; }
                    canvas.style.width = w + 'px';
                    canvas.style.height = h + 'px';
                    btnPlein.textContent = '⛶ Quitter le plein écran';
                } else {
                    canvas.style.width = '';
                    canvas.style.height = '';
                    btnPlein.textContent = '⛶ Plein écran';
                }
            }

            btnPlein.addEventListener('click', plein);
            document.addEventListener('fullscreenchange', ajusterTaille);
            document.addEventListener('webkitfullscreenchange', ajusterTaille);
            window.addEventListener('resize', ajusterTaille);

            canvas.addEventListener('mousedown', pousser);
            canvas.addEventListener('touchstart', function (e) { e.preventDefault(); pousser(); }, { passive: false });
            window.addEventListener('keydown', function (e) {
                if (e.code === 'Space' || e.key === ' ') { e.preventDefault(); pousser(); }
                if (e.key === 'f' || e.key === 'F') plein();
            });

            init();
            requestAnimationFrame(boucle);
        })();
        </script>
    """
    return page("Flappy Airbus", corps, "linear-gradient(135deg, #0ea5e9, #e0f2fe)")

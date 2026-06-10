const API = "http://localhost:8000";

let cache = { semaphores: [], robots: [], shapes: [], missions: [], teams: [] };

document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
});

function tronquerID(id) {
    if (!id) return "-";
    return id.length > 8 ? id.slice(0, 8) + "..." : id;
}

function badge(state) {
    if (!state) return '<span class="badge badge-pending">-</span>';
    const s = state.toLowerCase().replace(/\s+/g, "");
    let cls = "badge-pending";
    if (s === "available") cls = "badge-available";
    else if (s === "occupied" || s === "inprogress" || s === "encours") cls = "badge-inprogress";
    else if (s === "disabled" || s === "done") cls = "badge-done";
    else if (s === "pending") cls = "badge-pending";
    return `<span class="badge ${cls}">${state}</span>`;
}

function badgeBool(val) {
    if (val === true || val === 1) return '<span class="badge badge-yes">Oui</span>';
    return '<span class="badge badge-no">Non</span>';
}

function nomParId(liste, id) {
    if (!id) return "-";
    const item = liste.find(x => x.id === id);
    return item ? (item.name || tronquerID(id)) : tronquerID(id);
}

async function charger() {
    try {
        const [rSema, rRobot, rMission, rShape, rTeam] = await Promise.all([
            fetch(API + "/api/list_semaphore"),
            fetch(API + "/api/list_robots"),
            fetch(API + "/api/list_missions"),
            fetch(API + "/api/list_shapes"),
            fetch(API + "/api/list_teams"),
        ]);

        cache.semaphores = rSema.ok ? await rSema.json() : [];
        cache.robots = rRobot.ok ? await rRobot.json() : [];
        cache.missions = rMission.ok ? await rMission.json() : [];
        cache.shapes = rShape.ok ? await rShape.json() : [];
        cache.teams = rTeam.ok ? await rTeam.json() : [];

        // Status
        document.getElementById("status-dot").className = "dot dot-on";
        document.getElementById("status-text").textContent = "Connecte";

        afficherTout();
    } catch (e) {
        document.getElementById("status-dot").className = "dot dot-off";
        document.getElementById("status-text").textContent = "Hors ligne";
    }
}

function afficherTout() {
    document.getElementById("count-sema").textContent = cache.semaphores.length;
    document.getElementById("count-robot").textContent = cache.robots.length;
    document.getElementById("count-mission").textContent = cache.missions.length;
    document.getElementById("count-shape").textContent = cache.shapes.length;
    document.getElementById("count-team").textContent = cache.teams.length;

    remplir("mini-sema", cache.semaphores, s =>
        `<td>${s.name || "-"}</td><td>${s.type || "-"}</td><td>(${s.coord_x},${s.coord_y})</td><td>${badge(s.state)}</td>`
    );
    remplir("mini-robot", cache.robots, r =>
        `<td>${r.name || "-"}</td><td>${r.speed ?? "-"}</td><td>(${r.position_x},${r.position_y})</td><td>${badge(r.state)}</td>`
    );
    remplir("mini-mission", cache.missions, m =>
        `<td>${m.name || "-"}</td>` +
        `<td>${nomParId(cache.semaphores, m.semaphore_id)}</td>` +
        `<td>${nomParId(cache.robots, m.robot_id)}</td>` +
        `<td>${nomParId(cache.shapes, m.shape_id)}</td>` +
        `<td>${m.team || "-"}</td>` +
        `<td>${badge(m.state)}</td>`
    );

    remplir("table-sema", cache.semaphores, s =>
        `<td class="id-cell" title="${s.id}" onclick="copier('${s.id}')">${tronquerID(s.id)}</td>` +
        `<td>${s.name || "-"}</td><td>${s.type || "-"}</td><td>${s.duration ?? "-"}</td>` +
        `<td>${s.coord_x ?? "-"}</td><td>${s.coord_y ?? "-"}</td><td>${badge(s.state)}</td>`
    );
    remplir("table-robot", cache.robots, r =>
        `<td class="id-cell" title="${r.id}" onclick="copier('${r.id}')">${tronquerID(r.id)}</td>` +
        `<td>${r.name || "-"}</td><td>${r.speed ?? "-"}</td>` +
        `<td>${r.position_x ?? "-"}</td><td>${r.position_y ?? "-"}</td><td>${badge(r.state)}</td>`
    );
    remplir("table-mission", cache.missions, m =>
        `<td class="id-cell" title="${m.id}" onclick="copier('${m.id}')">${tronquerID(m.id)}</td>` +
        `<td>${m.name || "-"}</td>` +
        `<td>${nomParId(cache.semaphores, m.semaphore_id)}</td>` +
        `<td>${nomParId(cache.robots, m.robot_id)}</td>` +
        `<td>${nomParId(cache.shapes, m.shape_id)}</td>` +
        `<td>${m.team || "-"}</td>` +
        `<td>${m.start_date || "-"}</td><td>${m.end_date || "-"}</td>` +
        `<td>${m.time || "-"}</td><td>${badge(m.state)}</td>`
    );
    remplir("table-shape", cache.shapes, s =>
        `<td class="id-cell" title="${s.id}" onclick="copier('${s.id}')">${tronquerID(s.id)}</td>` +
        `<td>${s.name || "-"}</td><td>${s.image || "-"}</td>`
    );
    remplir("table-team", cache.teams, t =>
        `<td class="id-cell" title="${t.id}" onclick="copier('${t.id}')">${tronquerID(t.id)}</td>` +
        `<td>${t.name || "-"}</td><td>${t.ip || "-"}</td><td>${badgeBool(t.allowed)}</td>`
    );

    remplirSelect("sel-sema", cache.semaphores, "Semaphore...");
    remplirSelect("sel-shape", cache.shapes, "Shape...");
}

function remplir(tbodyId, data, rowFn) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = data.map(item => `<tr>${rowFn(item)}</tr>`).join("");
}

function remplirSelect(selectId, data, placeholder) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    sel.innerHTML = `<option value="">${placeholder}</option>` +
        data.map(d => `<option value="${d.id}">${d.name || d.id}</option>`).join("");
}

function copier(texte) {
    navigator.clipboard.writeText(texte).then(() => {
        const old = document.title;
        document.title = "ID copie !";
        setTimeout(() => document.title = old, 1000);
    });
}

async function ajouter(groupe, endpoint) {
    const inputs = document.querySelectorAll(`[data-for="${groupe}"]`);
    const params = new URLSearchParams();

    inputs.forEach(el => {
        const val = el.value.trim();
        if (val !== "") params.append(el.name, val);
    });

    try {
        const resp = await fetch(`${API}${endpoint}?${params.toString()}`, { method: "POST" });
        if (resp.ok) {
            inputs.forEach(el => { el.value = ""; });
            charger(); // refresh
        } else {
            alert("Erreur " + resp.status);
        }
    } catch (e) {
        alert("Serveur injoignable");
    }
}

charger();
setInterval(charger, 5000);

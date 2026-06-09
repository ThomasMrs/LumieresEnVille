const API = "http://localhost:8000";

document.querySelectorAll(".card button").forEach(button => {
    button.addEventListener("click", async () => {
        const card = button.closest(".card");
        const params = new URLSearchParams();

        card.querySelectorAll("input").forEach(input => {
            if (input.value !== "") {              // champs vides ignorés
                params.append(input.name, input.value);
            }
        });

        const endpoint = button.dataset.endpoint;
        try {
            const response = await fetch(`${API}${endpoint}?${params.toString()}`, {
                method: "POST"
            });
            if (response.ok) {
                alert("Ajouté OK.");
                card.querySelectorAll("input").forEach(i => i.value = "");  // vide les champs
            } else {
                alert("Erreur " + response.status);
            }
        } catch (e) {
            alert("Serveur injoignable");
        }
    });
});
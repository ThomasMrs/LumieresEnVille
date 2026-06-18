package fr.lumieresenville.robots;

import java.util.ArrayList;
import java.util.List;

// Mini-lecteur JSON en Java pur (aucune dependance externe : "JAVA/JavaFX uniquement").
// Suffisant pour les reponses simples du serveur (tableaux d'objets plats).
// Centralise le code autrefois duplique dans AppRobots, Grille et ApercuGrilleRobots.
public final class JsonMini {

    private JsonMini() {
    }

    // Decoupe un tableau JSON "[{...},{...}]" en la liste de ses objets "{...}".
    public static List<String> objets(String json) {
        List<String> liste = new ArrayList<>();
        int profondeur = 0;
        int debut = -1;
        for (int i = 0; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '{') {
                if (profondeur == 0) {
                    debut = i;
                }
                profondeur++;
            } else if (c == '}') {
                profondeur--;
                if (profondeur == 0 && debut >= 0) {
                    liste.add(json.substring(debut, i + 1));
                }
            }
        }
        return liste;
    }

    // Renvoie la valeur (texte) du champ "nom" dans un objet JSON, "" si absent ou null.
    public static String champ(String objet, String nom) {
        int i = objet.indexOf("\"" + nom + "\"");
        if (i < 0) {
            return "";
        }
        i = objet.indexOf(':', i) + 1;
        while (i < objet.length() && objet.charAt(i) == ' ') {
            i++;
        }
        if (i >= objet.length()) {
            return "";
        }
        if (objet.charAt(i) == '"') {
            return objet.substring(i + 1, objet.indexOf('"', i + 1));
        }
        int fin = i;
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') {
            fin++;
        }
        String valeur = objet.substring(i, fin).trim();
        return valeur.equals("null") ? "" : valeur;
    }

    // Comme champ(), mais convertit la valeur en nombre (0 si vide / absent).
    public static double nombre(String objet, String nom) {
        String valeur = champ(objet, nom);
        return valeur.isBlank() ? 0 : Double.parseDouble(valeur);
    }
}

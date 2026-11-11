"""Fonctions partagées par les pages : session, erreurs, formatage."""

from datetime import datetime

import streamlit as st

import api
import style

COEFFICIENT_PREMIERE_CLASSE = 1.5  # identique à reservations_service.py


# --- Session -------------------------------------------------------------------

def utilisateur() -> dict | None:
    """Utilisateur connecté : {"id", "nom", "grade", "token_acces"} ou None."""
    return st.session_state.get("utilisateur")


def token() -> str:
    return utilisateur()["token_acces"]


def deconnecter():
    st.session_state.clear()
    st.cache_data.clear()


def flash(message: str):
    """Message de succès à afficher après le prochain st.rerun()."""
    st.session_state.flash = message


def afficher_flash():
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message, icon=":material/check_circle:")


def afficher_erreur(erreur: api.ErreurAPI):
    """Affiche l'erreur. Si le token n'est plus valide (connexion ailleurs), déconnecte."""
    if erreur.statut == 401 and "token" in erreur.message.lower():
        deconnecter()
        st.warning("Votre session a expiré (connexion depuis un autre appareil ?). Reconnectez-vous.")
        st.button("Retour à la connexion", on_click=lambda: None)
        st.stop()
    st.error(erreur.message, icon=":material/error:")


# --- Données mises en cache ---------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def liste_gares(jeton: str) -> list[dict]:
    """Toutes les gares de notre base (pour l'autocomplétion), triées par nom."""
    return api.rechercher_gares(jeton)


def choisir_gare(libelle: str, gares: list[dict], cle: str, index: int | None = None) -> dict | None:
    """Liste déroulante avec saisie pour filtrer (autocomplétion)."""
    return st.selectbox(
        libelle,
        gares,
        index=index,
        key=cle,
        format_func=lambda g: f"{g['nom']} — {g['ville']}" if g.get("ville") else g["nom"],
        placeholder="Tapez le nom d'une gare…",
    )


# --- Formatage ------------------------------------------------------------------

def lire_date(texte: str) -> datetime:
    return datetime.fromisoformat(texte)


JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def jour(d) -> str:
    """Ex. « mardi 01/12/2026 » (sans dépendre de la locale du serveur)."""
    return f"{JOURS[d.weekday()]} {d:%d/%m/%Y}"


def jour_court(d) -> str:
    """Ex. « mar. 01/12/2026 »."""
    return f"{JOURS[d.weekday()][:3]}. {d:%d/%m/%Y}"


def heure(texte: str) -> str:
    return lire_date(texte).strftime("%H:%M")


def date_heure(texte: str) -> str:
    return lire_date(texte).strftime("%d/%m/%Y %H:%M")


def duree(minutes: int | None) -> str:
    if minutes is None:
        return "—"
    h, m = divmod(minutes, 60)
    return f"{h} h {m:02d}" if h else f"{m} min"


def euros(montant: float) -> str:
    return f"{montant:,.2f} €".replace(",", " ").replace(".", ",")


def prix_classe(tarif_base: float, classe: int) -> float:
    return round(tarif_base * COEFFICIENT_PREMIERE_CLASSE, 2) if classe == 1 else tarif_base


def libelle_classe(classe: int) -> str:
    return "1re classe" if classe == 1 else "2de classe"


def afficher_billet(reservation: dict):
    """Affiche une réservation (réponse de l'API) sous forme de billet."""
    trajet = reservation["trajet"]
    depart = lire_date(trajet["heure_depart"])
    style.billet(
        id_reservation=reservation["id_reservation"],
        gare_depart=trajet.get("nom_gare_depart") or "Départ",
        gare_arrivee=trajet.get("nom_gare_arrivee") or "Arrivée",
        depart=depart.strftime("%H:%M"),
        arrivee=heure(trajet["heure_arrivee"]),
        date=jour_court(depart),
        duree=duree(trajet.get("temps_trajet")),
        num_train=str(trajet.get("num_train") or "—"),
        place=reservation["place"],
        classe=reservation["classe"],
        prix=euros(reservation["prix"]),
        passe=depart <= datetime.now(),
    )

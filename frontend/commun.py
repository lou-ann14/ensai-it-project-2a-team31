"""Fonctions partagées par les pages : session, erreurs, formatage."""

from datetime import datetime

import streamlit as st

import api
import style

COEFFICIENT_PREMIERE_CLASSE = 1.5  # identique à reservations_service.py


# --- Session -------------------------------------------------------------------

def utilisateur() -> dict | None:
    """
    Récupère l'utilisateur connecté.

    Return:
    ------
    dict | None
        l'utilisateur (id, nom, grade, token_acces), ou None si personne n'est connecté
    """
    return st.session_state.get("utilisateur")


def token() -> str:
    """
    Récupère le token de l'utilisateur connecté.

    Return:
    ------
    str
        le token
    """
    return utilisateur()["token_acces"]


def deconnecter():
    """Vide la session et les données en cache."""
    st.session_state.clear()
    st.cache_data.clear()


def flash(message: str):
    """
    Enregistre un message de succès, affiché après le prochain st.rerun().

    Param:
    ------
    message: str
        le message à afficher
    """
    st.session_state.flash = message


def afficher_flash():
    """Affiche le message enregistré par flash(), une seule fois."""
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message, icon=":material/check_circle:")


def afficher_erreur(erreur: api.ErreurAPI):
    """
    Affiche l'erreur. Si le token n'est plus valide (connexion ailleurs), déconnecte.

    Param:
    ------
    erreur: api.ErreurAPI
        l'erreur renvoyée par l'API
    """
    if erreur.statut == 401 and "token" in erreur.message.lower():
        deconnecter()
        st.warning("Votre session a expiré (connexion depuis un autre appareil ?). Reconnectez-vous.")
        st.button("Retour à la connexion", on_click=lambda: None)
        st.stop()
    st.error(erreur.message, icon=":material/error:")


# --- Données mises en cache ---------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def liste_gares(jeton: str) -> list[dict]:
    """
    Récupère toutes les gares de notre base (pour l'autocomplétion).

    Param:
    ------
    jeton: str
        le token de l'utilisateur connecté

    Return:
    ------
    list[dict]
        les gares, triées par nom
    """
    return api.rechercher_gares(jeton)


def choisir_gare(libelle: str, gares: list[dict], cle: str, index: int | None = None) -> dict | None:
    """
    Liste déroulante avec saisie pour filtrer (autocomplétion).

    Param:
    ------
    libelle: str
        le titre de la liste
    gares: list[dict]
        les gares proposées
    cle: str
        la clé Streamlit de la liste
    index: int | None
        la position de la gare choisie au départ, ou None

    Return:
    ------
    dict | None
        la gare choisie, ou None
    """
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
    """
    Transforme une date renvoyée par l'API en datetime.

    Param:
    ------
    texte: str
        la date au format ISO

    Return:
    ------
    datetime
        la date
    """
    return datetime.fromisoformat(texte)


JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def jour(d) -> str:
    """
    Écrit une date avec le jour de la semaine (sans dépendre de la langue du serveur).

    Param:
    ------
    d: date | datetime
        la date

    Return:
    ------
    str
        le jour et la date
    """
    return f"{JOURS[d.weekday()]} {d:%d/%m/%Y}"


def jour_court(d) -> str:
    """
    Écrit une date avec le jour de la semaine abrégé.

    Param:
    ------
    d: date | datetime
        la date

    Return:
    ------
    str
        le jour abrégé et la date
    """
    return f"{JOURS[d.weekday()][:3]}. {d:%d/%m/%Y}"


def heure(texte: str) -> str:
    """
    Donne l'heure d'une date renvoyée par l'API.

    Param:
    ------
    texte: str
        la date au format ISO

    Return:
    ------
    str
        l'heure et les minutes
    """
    return lire_date(texte).strftime("%H:%M")


def date_heure(texte: str) -> str:
    """
    Donne le jour et l'heure d'une date renvoyée par l'API.

    Param:
    ------
    texte: str
        la date au format ISO

    Return:
    ------
    str
        le jour et l'heure
    """
    return lire_date(texte).strftime("%d/%m/%Y %H:%M")


def duree(minutes: int | None) -> str:
    """
    Écrit une durée en heures et minutes.

    Param:
    ------
    minutes: int | None
        la durée en minutes, ou None si elle est inconnue

    Return:
    ------
    str
        la durée, ou un tiret si elle est inconnue
    """
    if minutes is None:
        return "—"
    h, m = divmod(minutes, 60)
    return f"{h} h {m:02d}" if h else f"{m} min"


def euros(montant: float) -> str:
    """
    Écrit un montant en euros.

    Param:
    ------
    montant: float
        le montant

    Return:
    ------
    str
        le montant, avec le symbole de l'euro
    """
    return f"{montant:,.2f} €".replace(",", " ").replace(".", ",")


def prix_classe(tarif_base: float, classe: int) -> float:
    """
    Calcule le prix d'une place.

    Param:
    ------
    tarif_base: float
        le prix de base du trajet
    classe: int
        1 ou 2

    Return:
    ------
    float
        le prix de la place
    """
    return round(tarif_base * COEFFICIENT_PREMIERE_CLASSE, 2) if classe == 1 else tarif_base


def libelle_classe(classe: int) -> str:
    """
    Donne le nom d'une classe.

    Param:
    ------
    classe: int
        1 ou 2

    Return:
    ------
    str
        le nom affiché à l'écran
    """
    return "1re classe" if classe == 1 else "2de classe"


def libelle_ligne(ligne: dict) -> str:
    """
    Donne le texte d'une ligne.

    Param:
    ------
    ligne: dict
        la ligne renvoyée par l'API

    Return:
    ------
    str
        les gares de départ et d'arrivée
    """
    return f"{ligne['gare_depart']['nom']} → {ligne['gare_arrivee']['nom']}"


def libelle_train(train: dict) -> str:
    """
    Donne le texte d'un train.

    Param:
    ------
    train: dict
        le train renvoyé par l'API

    Return:
    ------
    str
        le numéro, le type et les places du train
    """
    return (
        f"n°{train['num_train']} · {train['type_train'] or '—'} · "
        f"{train['places_premieres']} en 1re, {train['places_secondes']} en 2de"
    )


def afficher_billet(reservation: dict):
    """
    Affiche une réservation sous forme de billet.

    Param:
    ------
    reservation: dict
        la réservation renvoyée par l'API
    """
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

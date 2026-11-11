"""Client HTTP de l'API backend.

Toutes les fonctions lèvent ErreurAPI avec un message lisible (en français)
si l'API est injoignable ou renvoie une erreur.
"""

import os
from datetime import date, datetime

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip("/")
try:
    TIMEOUT = float(os.getenv("BACKEND_TIMEOUT", "10"))
except ValueError:
    TIMEOUT = 10.0
# Les appels à l'API SNCF (import de gares, calcul du temps de trajet) sont plus lents
TIMEOUT_SNCF = max(TIMEOUT, 30.0)


class ErreurAPI(Exception):
    """Erreur renvoyée par l'API (ou API injoignable : statut 0)."""

    def __init__(self, statut: int, message: str):
        super().__init__(message)
        self.statut = statut
        self.message = message


def _message_erreur(reponse: requests.Response) -> str:
    """Extrait le message d'erreur d'une réponse FastAPI."""
    try:
        detail = reponse.json().get("detail")
    except (ValueError, AttributeError):
        detail = None

    if isinstance(detail, list):  # erreur de validation Pydantic (422)
        morceaux = []
        for erreur in detail:
            champ = ".".join(str(x) for x in erreur.get("loc", [])[1:])
            morceaux.append(f"{champ} : {erreur.get('msg')}" if champ else str(erreur.get("msg")))
        return "Données invalides — " + " ; ".join(morceaux)
    if detail:
        return str(detail)
    if reponse.status_code >= 500:
        return f"Erreur interne du serveur ({reponse.status_code})."
    return f"Erreur {reponse.status_code}."


def _appeler(methode: str, chemin: str, token: str | None = None, timeout: float = TIMEOUT, **kwargs):
    entetes = {"X-Auth-Token": token} if token else {}
    try:
        reponse = requests.request(
            methode, f"{BACKEND_URL}{chemin}", headers=entetes, timeout=timeout, **kwargs
        )
    except requests.ConnectionError:
        raise ErreurAPI(0, f"Impossible de joindre l'API ({BACKEND_URL}). Le backend est-il lancé ?") from None
    except requests.Timeout:
        raise ErreurAPI(0, "L'API met trop de temps à répondre.") from None

    if not reponse.ok:
        raise ErreurAPI(reponse.status_code, _message_erreur(reponse))
    return reponse.json() if reponse.content else None


def _iso(moment: datetime | date) -> str:
    return moment.isoformat()


# --- Comptes -----------------------------------------------------------------

def login(nom_utilisateur: str, mdp: str) -> dict:
    return _appeler("POST", "/login/", json={"nom_utilisateur": nom_utilisateur, "mdp": mdp})


def creer_compte(nom_utilisateur: str, mdp: str) -> dict:
    return _appeler("POST", "/utilisateur/comptes", json={"nom_utilisateur": nom_utilisateur, "mdp": mdp})


# --- Utilisateur (tout compte connecté) ---------------------------------------

def rechercher_gares(token: str, nom: str | None = None, ville: str | None = None) -> list[dict]:
    params = {k: v for k, v in {"nom": nom, "ville": ville}.items() if v}
    return _appeler("GET", "/utilisateur/gares", token, params=params)


def rechercher_trajets(token: str, gare_depart: str, gare_arrivee: str, date_voyage: date) -> list[dict]:
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee, "date_voyage": _iso(date_voyage)}
    return _appeler("GET", "/utilisateur/trajets", token, params=params)


def trouver_train(token: str, num_train: int) -> dict:
    return _appeler("GET", f"/utilisateur/trains/{num_train}", token)


# --- Client --------------------------------------------------------------------

def reserver(token: str, id_client: int, id_trajet: int, place: str, classe: int) -> dict:
    corps = {"id_client": id_client, "id_trajet": id_trajet, "place": place, "classe": classe}
    return _appeler("POST", "/utilisateur/reservations", token, json=corps)


def historique_reservations(token: str, id_client: int) -> list[dict]:
    return _appeler("GET", "/utilisateur/reservations", token, params={"id_client": id_client})


def annuler_reservation(token: str, id_client: int, id_reservation: int) -> dict:
    return _appeler("DELETE", f"/utilisateur/reservations/{id_reservation}", token, params={"id_client": id_client})


# --- Collaborateur -----------------------------------------------------------

def importer_gares(token: str, texte: str) -> list[dict]:
    return _appeler("POST", "/collaborateur/gares/importer", token, params={"q": texte}, timeout=TIMEOUT_SNCF)


def creer_ligne(token: str, gare_depart: str, gare_arrivee: str, id_collaborateur: int) -> dict:
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee, "id_collaborateur": id_collaborateur}
    return _appeler("POST", "/collaborateur/lignes", token, params=params)


def modifier_ligne(token: str, id_ligne: int, gare_depart: str, gare_arrivee: str) -> dict:
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee}
    return _appeler("PUT", f"/collaborateur/lignes/{id_ligne}", token, params=params)


def supprimer_ligne(token: str, id_ligne: int) -> dict:
    return _appeler("DELETE", f"/collaborateur/lignes/{id_ligne}", token)


def creer_train(token: str, type_train: str, places_premieres: int, places_secondes: int, num_train: int) -> dict:
    corps = {
        "type_train": type_train,
        "places_premieres": places_premieres,
        "places_secondes": places_secondes,
        "num_train": num_train,
    }
    return _appeler("POST", "/collaborateur/trains", token, json=corps)


def modifier_capacite(token: str, train: dict, places_premieres: int, places_secondes: int) -> dict:
    # L'API attend un train complet : on renvoie le type et le numéro actuels
    corps = {
        "type_train": train["type_train"],
        "places_premieres": places_premieres,
        "places_secondes": places_secondes,
        "num_train": train["num_train"],
    }
    return _appeler("PUT", f"/collaborateur/trains/{train['num_train']}", token, json=corps)


def _corps_trajet(id_ligne: int, id_train: int, heure_depart: datetime, tarif_base: float) -> dict:
    return {"id_ligne": id_ligne, "id_train": id_train, "heure_depart": _iso(heure_depart), "tarif_base": tarif_base}


def creer_trajet(token: str, id_ligne: int, id_train: int, heure_depart: datetime, tarif_base: float) -> dict:
    corps = _corps_trajet(id_ligne, id_train, heure_depart, tarif_base)
    return _appeler("POST", "/collaborateur/trajets", token, json=corps, timeout=TIMEOUT_SNCF)


def modifier_trajet(token: str, id_trajet: int, id_ligne: int, id_train: int,
                    heure_depart: datetime, tarif_base: float) -> dict:
    corps = _corps_trajet(id_ligne, id_train, heure_depart, tarif_base)
    return _appeler("PUT", f"/collaborateur/trajets/{id_trajet}", token, json=corps, timeout=TIMEOUT_SNCF)


def supprimer_trajet(token: str, id_trajet: int) -> dict:
    return _appeler("DELETE", f"/collaborateur/trajets/{id_trajet}", token)


# --- Administrateur ----------------------------------------------------------

def rechercher_compte(token: str, id_utilisateur: int | None = None, nom_utilisateur: str | None = None) -> dict:
    params = {}
    if id_utilisateur is not None:
        params["id_utilisateur"] = id_utilisateur
    if nom_utilisateur:
        params["nom_utilisateur"] = nom_utilisateur
    return _appeler("GET", "/admin/utilisateurs", token, params=params)


def modifier_grade(token: str, id_utilisateur: int, nouveau_grade: str) -> dict:
    return _appeler("PUT", f"/admin/utilisateurs/{id_utilisateur}/grade", token,
                    params={"nouveau_grade": nouveau_grade})

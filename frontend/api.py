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
        """
        Crée l'erreur.

        Param:
        ------
        statut: int
            le code HTTP de la réponse (0 si l'API est injoignable)
        message: str
            le message à afficher
        """
        super().__init__(message)
        self.statut = statut
        self.message = message


def _message_erreur(reponse: requests.Response) -> str:
    """
    Extrait le message d'erreur d'une réponse FastAPI.

    Param:
    ------
    reponse: requests.Response
        la réponse de l'API

    Return:
    ------
    str
        le message à afficher
    """
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
    """
    Envoie une requête à l'API.

    Param:
    ------
    methode: str
        la méthode HTTP
    chemin: str
        le chemin de la route
    token: str | None
        le token de l'utilisateur, ou None si la route n'en demande pas
    timeout: float
        le temps d'attente maximum, en secondes
    kwargs: dict
        les autres paramètres de la requête (corps, paramètres de l'adresse)

    Return:
    ------
    dict | list | None
        le contenu JSON de la réponse, ou None si elle est vide

    Raises:
    ------
    ErreurAPI
        si l'API est injoignable ou renvoie une erreur
    """
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
    """
    Met une date au format attendu par l'API.

    Param:
    ------
    moment: datetime | date
        la date à convertir

    Return:
    ------
    str
        la date au format ISO
    """
    return moment.isoformat()


# --- Comptes -----------------------------------------------------------------

def login(nom_utilisateur: str, mdp: str) -> dict:
    """
    Connecte un utilisateur.

    Param:
    ------
    nom_utilisateur: str
        le nom d'utilisateur
    mdp: str
        le mot de passe

    Return:
    ------
    dict
        le compte de l'utilisateur, avec son token
    """
    return _appeler("POST", "/login/", json={"nom_utilisateur": nom_utilisateur, "mdp": mdp})


def creer_compte(nom_utilisateur: str, mdp: str) -> dict:
    """
    Crée un compte client.

    Param:
    ------
    nom_utilisateur: str
        le nom d'utilisateur
    mdp: str
        le mot de passe

    Return:
    ------
    dict
        le compte créé
    """
    return _appeler("POST", "/utilisateur/comptes", json={"nom_utilisateur": nom_utilisateur, "mdp": mdp})


# --- Utilisateur (tout compte connecté) ---------------------------------------

def rechercher_gares(token: str, nom: str | None = None, ville: str | None = None) -> list[dict]:
    """
    Cherche des gares par le début du nom et/ou de la ville (toutes si rien n'est donné).

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    nom: str | None
        le début du nom de la gare
    ville: str | None
        le début du nom de la ville

    Return:
    ------
    list[dict]
        les gares trouvées
    """
    params = {k: v for k, v in {"nom": nom, "ville": ville}.items() if v}
    return _appeler("GET", "/utilisateur/gares", token, params=params)


def rechercher_trajets(token: str, gare_depart: str, gare_arrivee: str, date_voyage: date | None = None) -> list[dict]:
    """
    Cherche les trajets entre deux gares, un jour donné ou, sans date, tous les trajets à venir.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    gare_depart: str
        le nom de la gare de départ
    gare_arrivee: str
        le nom de la gare d'arrivée
    date_voyage: date | None
        le jour du voyage, ou None

    Return:
    ------
    list[dict]
        les trajets trouvés, triés par heure de départ
    """
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee}
    if date_voyage is not None:
        params["date_voyage"] = _iso(date_voyage)
    return _appeler("GET", "/utilisateur/trajets", token, params=params)


def trouver_train(token: str, num_train: int) -> dict:
    """
    Cherche un train par son numéro.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    num_train: int
        le numéro du train

    Return:
    ------
    dict
        le train trouvé
    """
    return _appeler("GET", f"/utilisateur/trains/{num_train}", token)


# --- Client --------------------------------------------------------------------

# Pas d'id_client ni d'id_collaborateur : l'API identifie l'utilisateur grâce à son token.

def reserver(token: str, id_trajet: int, place: str | None, classe: int) -> dict:
    """
    Réserve une place sur un trajet.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_trajet: int
        l'id du trajet
    place: str | None
        le numéro de la place, ou None pour que l'API attribue la première place libre
    classe: int
        1 ou 2

    Return:
    ------
    dict
        la réservation créée
    """
    corps = {"id_trajet": id_trajet, "place": place, "classe": classe}
    return _appeler("POST", "/utilisateur/reservations", token, json=corps)


def places_libres(token: str, id_trajet: int) -> dict:
    """
    Cherche les places libres d'un trajet.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_trajet: int
        l'id du trajet

    Return:
    ------
    dict
        la capacité et les places libres de chaque classe (capacite_premiere, capacite_seconde,
        libres_premiere, libres_seconde)
    """
    return _appeler("GET", f"/utilisateur/trajets/{id_trajet}/places", token)


def historique_reservations(token: str) -> list[dict]:
    """
    Cherche les réservations de l'utilisateur connecté.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté

    Return:
    ------
    list[dict]
        ses réservations, passées et à venir
    """
    return _appeler("GET", "/utilisateur/reservations", token)


def annuler_reservation(token: str, id_reservation: int) -> dict:
    """
    Annule une réservation de l'utilisateur connecté.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_reservation: int
        l'id de la réservation

    Return:
    ------
    dict
        un message de confirmation
    """
    return _appeler("DELETE", f"/utilisateur/reservations/{id_reservation}", token)


# --- Collaborateur -----------------------------------------------------------

def importer_gares(token: str, texte: str) -> list[dict]:
    """
    Cherche des gares dans l'API SNCF et les enregistre dans notre base.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    texte: str
        le texte recherché

    Return:
    ------
    list[dict]
        les gares importées
    """
    return _appeler("POST", "/collaborateur/gares/importer", token, params={"q": texte}, timeout=TIMEOUT_SNCF)


def creer_ligne(token: str, gare_depart: str, gare_arrivee: str) -> dict:
    """
    Crée une ligne entre deux gares.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    gare_depart: str
        le nom de la gare de départ
    gare_arrivee: str
        le nom de la gare d'arrivée

    Return:
    ------
    dict
        un message de confirmation et l'id de la ligne
    """
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee}
    return _appeler("POST", "/collaborateur/lignes", token, params=params)


def modifier_ligne(token: str, id_ligne: int, gare_depart: str, gare_arrivee: str) -> dict:
    """
    Change les gares d'une ligne.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_ligne: int
        l'id de la ligne
    gare_depart: str
        le nom de la gare de départ
    gare_arrivee: str
        le nom de la gare d'arrivée

    Return:
    ------
    dict
        un message de confirmation et l'id de la ligne
    """
    params = {"gare_depart": gare_depart, "gare_arrivee": gare_arrivee}
    return _appeler("PUT", f"/collaborateur/lignes/{id_ligne}", token, params=params)


def supprimer_ligne(token: str, id_ligne: int) -> dict:
    """
    Supprime une ligne.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_ligne: int
        l'id de la ligne

    Return:
    ------
    dict
        un message de confirmation
    """
    return _appeler("DELETE", f"/collaborateur/lignes/{id_ligne}", token)


def creer_train(token: str, type_train: str, places_premieres: int, places_secondes: int, num_train: int) -> dict:
    """
    Crée un train.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    type_train: str
        le type du train
    places_premieres: int
        le nombre de places en première classe
    places_secondes: int
        le nombre de places en seconde classe
    num_train: int
        le numéro du train

    Return:
    ------
    dict
        le train créé
    """
    corps = {
        "type_train": type_train,
        "places_premieres": places_premieres,
        "places_secondes": places_secondes,
        "num_train": num_train,
    }
    return _appeler("POST", "/collaborateur/trains", token, json=corps)


def modifier_capacite(token: str, train: dict, places_premieres: int, places_secondes: int) -> dict:
    """
    Change le nombre de places d'un train.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    train: dict
        le train à modifier
    places_premieres: int
        le nouveau nombre de places en première classe
    places_secondes: int
        le nouveau nombre de places en seconde classe

    Return:
    ------
    dict
        le train modifié
    """
    # L'API attend un train complet : on renvoie le type et le numéro actuels
    corps = {
        "type_train": train["type_train"],
        "places_premieres": places_premieres,
        "places_secondes": places_secondes,
        "num_train": train["num_train"],
    }
    return _appeler("PUT", f"/collaborateur/trains/{train['num_train']}", token, json=corps)


def _corps_trajet(id_ligne: int, id_train: int, heure_depart: datetime, tarif_base: float) -> dict:
    """
    Prépare les données d'un trajet, pour sa création ou sa modification.

    Param:
    ------
    id_ligne: int
        l'id de la ligne
    id_train: int
        l'id du train utilisé
    heure_depart: datetime
        la date et l'heure de départ
    tarif_base: float
        le prix d'une place en seconde classe

    Return:
    ------
    dict
        les données à envoyer à l'API
    """
    return {"id_ligne": id_ligne, "id_train": id_train, "heure_depart": _iso(heure_depart), "tarif_base": tarif_base}


def creer_trajet(token: str, id_ligne: int, id_train: int, heure_depart: datetime, tarif_base: float) -> dict:
    """
    Planifie un trajet (le temps de trajet est calculé par l'API SNCF).

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_ligne: int
        l'id de la ligne
    id_train: int
        l'id du train utilisé
    heure_depart: datetime
        la date et l'heure de départ
    tarif_base: float
        le prix d'une place en seconde classe

    Return:
    ------
    dict
        un message de confirmation, l'id du trajet, son heure d'arrivée et sa durée
    """
    corps = _corps_trajet(id_ligne, id_train, heure_depart, tarif_base)
    return _appeler("POST", "/collaborateur/trajets", token, json=corps, timeout=TIMEOUT_SNCF)


def modifier_trajet(token: str, id_trajet: int, id_ligne: int, id_train: int,
                    heure_depart: datetime, tarif_base: float) -> dict:
    """
    Modifie un trajet (le temps de trajet est recalculé par l'API SNCF).

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_trajet: int
        l'id du trajet
    id_ligne: int
        l'id de la ligne
    id_train: int
        l'id du train utilisé
    heure_depart: datetime
        la date et l'heure de départ
    tarif_base: float
        le prix d'une place en seconde classe

    Return:
    ------
    dict
        un message de confirmation, l'id du trajet, son heure d'arrivée et sa durée
    """
    corps = _corps_trajet(id_ligne, id_train, heure_depart, tarif_base)
    return _appeler("PUT", f"/collaborateur/trajets/{id_trajet}", token, json=corps, timeout=TIMEOUT_SNCF)


def supprimer_trajet(token: str, id_trajet: int) -> dict:
    """
    Supprime un trajet.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_trajet: int
        l'id du trajet

    Return:
    ------
    dict
        un message de confirmation
    """
    return _appeler("DELETE", f"/collaborateur/trajets/{id_trajet}", token)


# --- Administrateur ----------------------------------------------------------

def rechercher_compte(token: str, id_utilisateur: int | None = None, nom_utilisateur: str | None = None) -> dict:
    """
    Cherche un compte par son id ou par son nom d'utilisateur.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_utilisateur: int | None
        l'id du compte
    nom_utilisateur: str | None
        le nom d'utilisateur du compte

    Return:
    ------
    dict
        le compte trouvé
    """
    params = {}
    if id_utilisateur is not None:
        params["id_utilisateur"] = id_utilisateur
    if nom_utilisateur:
        params["nom_utilisateur"] = nom_utilisateur
    return _appeler("GET", "/admin/utilisateurs", token, params=params)


def modifier_grade(token: str, id_utilisateur: int, nouveau_grade: str) -> dict:
    """
    Change le grade d'un compte.

    Param:
    ------
    token: str
        le token de l'utilisateur connecté
    id_utilisateur: int
        l'id du compte
    nouveau_grade: str
        le nouveau grade (CLIENT, COLLABORATEUR ou ADMIN)

    Return:
    ------
    dict
        le compte modifié
    """
    return _appeler("PUT", f"/admin/utilisateurs/{id_utilisateur}/grade", token,
                    params={"nouveau_grade": nouveau_grade})

import os

import requests
from src.utils.log_utils import get_logger
from datetime import datetime

logger = get_logger(__name__)

BASE_URL = "https://api.sncf.com/v1/coverage/sncf"


class SncfClient:
    """Client pour interroger l'API SNCF (authentification : token en identifiant, mot de passe vide)"""

    def __init__(self):
        token = os.getenv("SNCF_API_TOKEN")
        if not token:
            raise RuntimeError("SNCF_API_TOKEN manquant dans le fichier .env")
        self.auth = (token, "")

    def _get(self, chemin: str, params: dict) -> dict:
        """Envoie une requête GET à l'API et renvoie le JSON (lève une erreur si le code HTTP n'est pas 2xx)"""
        reponse = requests.get(f"{BASE_URL}/{chemin}", params=params, auth=self.auth, timeout=10)
        reponse.raise_for_status()
        return reponse.json()

    def rechercher_gares(self, texte: str) -> list[dict]:
        """Cherche des gares dont le nom correspond au texte.

        Return:
        ------
        list[dict]
            une liste de dictionnaires {"id_sncf": ..., "nom": ..., "ville": ...}
        """
        donnees = self._get("places", {"type[]": "stop_area", "q": texte})
        gares = []
        for place in donnees.get("places", []):
            stop_area = place["stop_area"]
            gares.append({
                "id_sncf": stop_area["id"],
                "nom": stop_area["name"],
                "ville": self._trouver_ville(stop_area),
            })
        return gares

    @staticmethod
    def _trouver_ville(stop_area: dict) -> str | None:
        """Renvoie le nom de la commune (niveau administratif 8) d'une gare, ou None si absente"""
        for region in stop_area.get("administrative_regions", []):
            if region.get("level") == 8:
                return region["name"]
        return None
    def duree_trajet(self, id_depart: str, id_arrivee: str, date_depart: datetime | None = None) -> int | None:
        """Calcule la durée du trajet le plus rapide entre deux gares.

        Param:
        ------
        id_depart, id_arrivee: str
            les identifiants SNCF des gares (ex : "stop_area:SNCF:87391003")
        date_depart: datetime | None
            la date et l'heure de départ souhaitées (par défaut : maintenant)

        Return:
        ------
        int | None
            la durée en secondes, ou None si aucun trajet n'est possible
        """
        params = {"from": id_depart, "to": id_arrivee}
        if date_depart:
            params["datetime"] = date_depart.strftime("%Y%m%dT%H%M%S")
        try:
            donnees = self._get("journeys", params)
        except requests.HTTPError as erreur:
            if erreur.response is not None and erreur.response.status_code == 404:
                return None
            raise
        itineraires = donnees.get("journeys", [])
        if not itineraires:
            return None
        return min(itineraire["duration"] for itineraire in itineraires)
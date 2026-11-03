import os

import requests
from src.utils.log_utils import get_logger

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
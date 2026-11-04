from datetime import datetime

from src.Classes.classes_DAO.gare_DAO import GareDAO
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.ligne_service import LigneService
from src.Classes.classes_service.trajet_service import TrajetService
from src.utils.log_utils import log


class CollaborateurService:
    """Classe qui gère les actions réservées aux collaborateurs"""

    @log
    def creer_ligne(self, gare_depart_id: int, gare_arrivee_id: int, id_collaborateur: int) -> Ligne:
        """
        Méthode servant à créer une ligne entre deux gares.

        Param:
        ------
        gare_depart_id: int
            l'id de la gare de départ
        gare_arrivee_id: int
            l'id de la gare d'arrivée
        id_collaborateur: int
            l'id du collaborateur qui crée la ligne

        Return:
        ------
        Ligne
            la ligne créée, avec son id_ligne renseigné

        Raises:
        ------
        ValueError
            si une gare ou le collaborateur n'existe pas, si les deux gares sont identiques
            ou si la ligne existe déjà
        """
        gare_depart = GareDAO().trouver_par_id(gare_depart_id)
        if gare_depart is None:
            raise ValueError(f"La gare #{gare_depart_id} n'existe pas.")
        gare_arrivee = GareDAO().trouver_par_id(gare_arrivee_id)
        if gare_arrivee is None:
            raise ValueError(f"La gare #{gare_arrivee_id} n'existe pas.")

        return LigneService().creer(gare_depart, gare_arrivee, id_collaborateur)

    @log
    def creer_trajet(
        self,
        id_ligne: int,
        id_train: int,
        heure_depart: datetime,
        heure_arrivee: datetime,
        tarif_base: float,
    ) -> Trajet:
        """
        Méthode servant à créer un trajet sur une ligne existante.

        Param:
        ------
        id_ligne: int
            l'id de la ligne
        id_train: int
            l'id du train utilisé
        heure_depart: datetime
            la date et l'heure de départ
        heure_arrivee: datetime
            la date et l'heure d'arrivée
        tarif_base: float
            le prix de base du trajet

        Return:
        ------
        Trajet
            le trajet créé, avec son id_trajet renseigné

        Raises:
        ------
        ValueError
            si une donnée est invalide, si la ligne ou le train n'existe pas
            ou si un trajet existe déjà sur cette ligne à cette heure de départ
        """
        return TrajetService().creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

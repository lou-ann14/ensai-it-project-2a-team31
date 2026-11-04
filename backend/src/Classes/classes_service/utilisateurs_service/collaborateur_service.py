from datetime import datetime

from src.Classes.classes_DAO.gare_DAO import GareDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.gare_service import GareService
from src.Classes.classes_service.ligne_service import LigneService
from src.Classes.classes_service.train_service import TrainService
from src.Classes.classes_service.trajet_service import TrajetService
from src.utils.log_utils import log


class CollaborateurService:
    """Classe qui gère les actions réservées aux collaborateurs"""

    @staticmethod
    def _trouver_gares(gare_depart_id: int, gare_arrivee_id: int):
        """Récupère les deux gares à partir de leur id (lève ValueError si l'une n'existe pas)."""
        gare_depart = GareDAO().trouver_par_id(gare_depart_id)
        if gare_depart is None:
            raise ValueError(f"La gare #{gare_depart_id} n'existe pas.")
        gare_arrivee = GareDAO().trouver_par_id(gare_arrivee_id)
        if gare_arrivee is None:
            raise ValueError(f"La gare #{gare_arrivee_id} n'existe pas.")
        return gare_depart, gare_arrivee

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
        gare_depart, gare_arrivee = self._trouver_gares(gare_depart_id, gare_arrivee_id)

        return LigneService().creer(gare_depart, gare_arrivee, id_collaborateur)

    @log
    def creer_trajet(
        self,
        id_ligne: int,
        id_train: int,
        heure_depart: datetime,
        tarif_base: float,
    ) -> Trajet:
        """
        Méthode servant à créer un trajet sur une ligne existante.
        L'heure d'arrivée et le temps de trajet sont calculés grâce à l'API SNCF.

        Param:
        ------
        id_ligne: int
            l'id de la ligne
        id_train: int
            l'id du train utilisé
        heure_depart: datetime
            la date et l'heure de départ
        tarif_base: float
            le prix de base du trajet

        Return:
        ------
        Trajet
            le trajet créé, avec son id_trajet renseigné

        Raises:
        ------
        ValueError
            si une donnée est invalide, si la ligne ou le train n'existe pas,
            si un trajet existe déjà sur cette ligne à cette heure de départ
            ou si l'API SNCF ne trouve aucun itinéraire entre les deux gares
        requests.RequestException
            si l'API SNCF est indisponible
        """
        return TrajetService().creer(id_ligne, id_train, heure_depart, tarif_base)

    @log
    def modifier_ligne(self, id_ligne: int, gare_depart_id: int, gare_arrivee_id: int) -> Ligne | None:
        """
        Méthode servant à modifier les gares d'une ligne.

        Param:
        ------
        id_ligne: int
            l'id de la ligne à modifier
        gare_depart_id: int
            l'id de la nouvelle gare de départ
        gare_arrivee_id: int
            l'id de la nouvelle gare d'arrivée

        Return:
        ------
        Ligne | None
            la ligne modifiée, ou None si elle n'existe pas

        Raises:
        ------
        ValueError
            si une gare n'existe pas, si les deux gares sont identiques,
            si une autre ligne relie déjà ces gares ou si la ligne a des trajets
        """
        if LigneService().trouver_par_id(id_ligne) is None:
            return None

        gare_depart, gare_arrivee = self._trouver_gares(gare_depart_id, gare_arrivee_id)
        ligne = Ligne(gare_depart, gare_arrivee, id_ligne=id_ligne)

        return ligne if LigneService().modifier(ligne) else None

    @log
    def supprimer_ligne(self, id_ligne: int) -> bool:
        """
        Méthode servant à supprimer une ligne.

        Param:
        ------
        id_ligne: int
            l'id de la ligne à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False si la ligne n'existe pas

        Raises:
        ------
        ValueError
            si des trajets existent encore sur cette ligne
        """
        return LigneService().supprimer(id_ligne)

    @log
    def modifier_trajet(
        self,
        id_trajet: int,
        id_ligne: int,
        id_train: int,
        heure_depart: datetime,
        tarif_base: float,
    ) -> Trajet | None:
        """
        Méthode servant à modifier un trajet.
        L'heure d'arrivée et le temps de trajet sont recalculés grâce à l'API SNCF.

        Param:
        ------
        id_trajet: int
            l'id du trajet à modifier
        id_ligne: int
            l'id de la ligne
        id_train: int
            l'id du train utilisé
        heure_depart: datetime
            la date et l'heure de départ
        tarif_base: float
            le prix de base du trajet

        Return:
        ------
        Trajet | None
            le trajet modifié, ou None s'il n'existe pas

        Raises:
        ------
        ValueError
            si une donnée est invalide, si la ligne ou le train n'existe pas,
            si un autre trajet existe déjà sur cette ligne à cette heure de départ
            ou si l'API SNCF ne trouve aucun itinéraire entre les deux gares
        requests.RequestException
            si l'API SNCF est indisponible
        """
        if TrajetService().trouver_par_id(id_trajet) is None:
            return None

        ligne = LigneService().trouver_par_id(id_ligne)
        if ligne is None:
            raise ValueError(f"La ligne #{id_ligne} n'existe pas : un trajet doit se faire sur une ligne existante.")

        # Seul l'id du train est connu : la base vérifie qu'il existe (clé étrangère).
        train = Train(type_train=None, places_premieres=None, places_secondes=None, num_train=None, id_train=id_train)
        # L'heure d'arrivée est provisoire : TrajetService.modifier la recalcule.
        trajet = Trajet(heure_depart, heure_depart, ligne, train, tarif_base, id_trajet=id_trajet)

        return trajet if TrajetService().modifier(id_trajet, trajet) else None

    @log
    def supprimer_trajet(self, id_trajet: int) -> bool:
        """
        Méthode servant à supprimer un trajet.

        Param:
        ------
        id_trajet: int
            l'id du trajet à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False si le trajet n'existe pas

        Raises:
        ------
        ValueError
            si des réservations existent encore sur ce trajet
        """
        return TrajetService().supprimer(id_trajet)

    @log
    def importer_gares(self, texte: str) -> list[Gare]:
        """
        Méthode servant à importer dans notre base les gares trouvées sur l'API SNCF.

        Param:
        ------
        texte: str
            le texte à rechercher (au moins 2 caractères)

        Return:
        ------
        list[Gare]
            les gares importées

        Raises:
        ------
        ValueError
            si le texte est trop court
        requests.RequestException
            si l'API SNCF est indisponible
        """
        return GareService().importer(texte)

    @log
    def creer_train(self, type_train: str, places_premieres: int, places_secondes: int, num_train: int) -> Train:
        """
        Méthode servant à créer un nouveau train.

        Param:
        ------
        type_train: str
            le type de train (ex: TGV, TER)
        places_premieres: int
            le nombre de places en première classe
        places_secondes: int
            le nombre de places en seconde classe
        num_train: int
            le numéro du train

        Return:
        ------
        Train
            le train créé, avec son id_train renseigné

        Raises:
        ------
        ValueError
            si la capacité est incorrecte ou si ce numéro de train existe déjà
        """
        return TrainService().creer(type_train, places_premieres, places_secondes, num_train)

    @log
    def modifier_capacite(self, num_train: int, places_premieres: int, places_secondes: int) -> Train | None:
        """
        Méthode servant à modifier la capacité d'un train.

        Param:
        ------
        num_train: int
            le numéro du train à modifier
        places_premieres: int
            le nouveau nombre de places en première classe
        places_secondes: int
            le nouveau nombre de places en seconde classe

        Return:
        ------
        Train | None
            le train modifié, ou None si la modification ne s'est pas exécutée

        Raises:
        ------
        ValueError
            si la capacité est incorrecte
        HTTPException 404
            si le train n'existe pas
        """
        train_service = TrainService()
        train = train_service.trouver_train_par_num(num_train)

        if not train_service.modifier_capacite(num_train, places_premieres, places_secondes):
            return None

        train.places_premieres = places_premieres
        train.places_secondes = places_secondes
        return train

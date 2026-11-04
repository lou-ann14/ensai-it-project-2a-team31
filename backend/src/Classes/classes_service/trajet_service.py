from datetime import date, datetime, timedelta

from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.utils.log_utils import log
from src.utils.sncf_client import SncfClient


class TrajetService:
    """Classe qui gère les opérations métier sur les trajets"""

    def __init__(self):
        self.trajet_dao = TrajetDAO()

    @log
    def creer(
        self,
        id_ligne: int,
        id_train: int,
        heure_depart: datetime,
        tarif_base: float,
    ) -> Trajet:
        """
        Méthode servant à créer un nouveau trajet.
        Le temps de trajet et l'heure d'arrivée sont calculés grâce à l'API SNCF.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne concernée
        id_train: int
            l'identifiant du train utilisé pour le trajet
        heure_depart: datetime
            la date et l'heure de départ
        tarif_base: float
            le prix de base du trajet

        Return:
        ------
        Trajet
            le trajet créé, avec son id_trajet, son heure d'arrivée et son temps de trajet renseignés

        Raises:
        ------
        ValueError
            si une donnée est invalide, si la ligne ou le train n'existe pas,
            si un trajet existe déjà sur cette ligne à cette heure de départ
            ou si l'API SNCF ne trouve aucun itinéraire entre les deux gares
        requests.RequestException
            si l'API SNCF est indisponible
        """
        self._verifier_donnees(id_ligne, id_train, heure_depart, tarif_base)
        ligne = self._verifier_ligne(id_ligne)

        if self._trajet_similaire_existe(ligne, heure_depart):
            raise ValueError("Un trajet existe déjà sur cette ligne à cette date et à cette heure.")

        duree = self._calculer_duree(ligne, heure_depart)

        # TODO : remplacer par TrainDAO.trouver_par_id quand cette méthode existera.
        # En attendant, seul l'id du train est connu : la base vérifie qu'il existe (clé étrangère).
        train = Train(type_train=None, places_premieres=None, places_secondes=None, num_train=None, id_train=id_train)
        trajet = Trajet(
            heure_depart=heure_depart,
            heure_arrivee=heure_depart + timedelta(seconds=duree),
            ligne=ligne,
            train=train,
            tarif_base=tarif_base,
            temps_trajet=round(duree / 60),
        )
        try:
            return self.trajet_dao.creer(trajet)
        except ForeignKeyViolation:
            raise ValueError(f"Le train #{id_train} n'existe pas.")

    @log
    def modifier(self, id_trajet: int, trajet: Trajet) -> bool:
        """
        Méthode servant à modifier les informations d'un trajet existant.
        Le temps de trajet et l'heure d'arrivée sont recalculés grâce à l'API SNCF.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à modifier
        trajet: Trajet
            l'objet Trajet contenant les nouvelles informations

        Return:
        ------
        bool
            True si la modification a réussi, False sinon

        Raises:
        ------
        ValueError
            si le trajet n'existe pas, si une donnée est invalide, si la ligne n'existe pas,
            si un autre trajet existe déjà sur cette ligne à cette heure de départ
            ou si l'API SNCF ne trouve aucun itinéraire entre les deux gares
        requests.RequestException
            si l'API SNCF est indisponible
        """
        if trajet is None:
            raise ValueError("Le trajet à modifier est obligatoire.")
        if self.trajet_dao.trouver_par_id(id_trajet) is None:
            raise ValueError(f"Le trajet #{id_trajet} n'existe pas.")

        id_ligne = trajet.ligne.id_ligne if trajet.ligne else None
        id_train = trajet.train.id_train if trajet.train else None
        self._verifier_donnees(id_ligne, id_train, trajet.heure_depart, trajet.tarif_base)
        ligne = self._verifier_ligne(id_ligne)

        if self._trajet_similaire_existe(ligne, trajet.heure_depart, id_trajet_ignore=id_trajet):
            raise ValueError("Un autre trajet existe déjà sur cette ligne à cette date et à cette heure.")

        duree = self._calculer_duree(ligne, trajet.heure_depart)
        trajet.heure_arrivee = trajet.heure_depart + timedelta(seconds=duree)
        trajet.horaires = f"{trajet.heure_depart}, {trajet.heure_arrivee}"
        trajet.temps_trajet = round(duree / 60)

        trajet.id_trajet = id_trajet
        try:
            return self.trajet_dao.modifier(trajet)
        except ForeignKeyViolation:
            raise ValueError(f"Le train #{id_train} n'existe pas.")

    @log
    def supprimer(self, id_trajet: int) -> bool:
        """
        Méthode servant à supprimer un trajet.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False sinon (trajet inexistant)

        Raises:
        ------
        ValueError
            si des réservations existent encore sur ce trajet
        """
        try:
            return self.trajet_dao.supprimer(id_trajet)
        except ForeignKeyViolation:
            raise ValueError("Impossible de supprimer un trajet qui a des réservations.")

    @log
    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare, date_voyage: datetime | date) -> list[Trajet]:
        """
        Méthode servant à rechercher des trajets disponibles.

        Param:
        ------
        gare_depart: Gare
            l'objet Gare de départ
        gare_arrivee: Gare
            l'objet Gare d'arrivée
        date_voyage: datetime | date
            la date de voyage souhaitée (seul le jour est pris en compte)

        Return:
        ------
        list[Trajet]
            la liste des trajets correspondants, triés par heure de départ (vide si aucun)

        Raises:
        ------
        ValueError
            si une gare ou la date est manquante, ou si les deux gares sont identiques
        """
        if gare_depart is None or gare_arrivee is None:
            raise ValueError("La gare de départ et la gare d'arrivée sont obligatoires.")
        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise ValueError("La gare de départ et la gare d'arrivée doivent être différentes.")
        if date_voyage is None:
            raise ValueError("La date de voyage est obligatoire.")

        return self.trajet_dao.rechercher(gare_depart=gare_depart, gare_arrivee=gare_arrivee, date=date_voyage)

    @log
    def trouver_par_id(self, id_trajet: int) -> Trajet | None:
        """
        Méthode servant à récupérer un trajet par son identifiant
        (utilisée par ReservationService pour vérifier l'existence d'un trajet).

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet

        Return:
        ------
        Trajet | None
            le trajet trouvé, ou None s'il n'existe pas
        """
        return self.trajet_dao.trouver_par_id(id_trajet)

    def _verifier_donnees(self, id_ligne, id_train, heure_depart, tarif_base) -> None:
        """Vérifie la validité des données d'un trajet (lève ValueError sinon)."""
        if id_ligne is None or id_train is None:
            raise ValueError("La ligne et le train sont obligatoires.")
        if not isinstance(heure_depart, datetime):
            raise TypeError("L'heure de départ doit être une date avec heure.")
        if tarif_base is None or tarif_base < 0:
            raise ValueError("Le tarif de base doit être positif ou nul.")

    def _calculer_duree(self, ligne, heure_depart: datetime) -> int:
        """Demande à l'API SNCF la durée du trajet sur cette ligne, en secondes (lève ValueError si aucune)."""
        id_sncf_depart = ligne.gare_depart.id_sncf
        id_sncf_arrivee = ligne.gare_arrivee.id_sncf
        if not id_sncf_depart or not id_sncf_arrivee:
            raise ValueError("Les gares de cette ligne ne viennent pas de l'API SNCF : temps de trajet impossible à calculer.")

        client = SncfClient()
        duree = client.duree_trajet(id_sncf_depart, id_sncf_arrivee, heure_depart)
        if duree is None:
            # L'API ne connaît les horaires que sur quelques semaines : pour une date
            # plus lointaine, on retient la durée du trajet selon les horaires actuels.
            duree = client.duree_trajet(id_sncf_depart, id_sncf_arrivee)
        if duree is None:
            raise ValueError("L'API SNCF ne trouve aucun itinéraire entre ces deux gares.")
        return duree

    def _verifier_ligne(self, id_ligne: int):
        """Vérifie que la ligne existe et la renvoie (lève ValueError sinon)."""
        ligne = LigneDAO().trouver_par_id(id_ligne)
        if ligne is None:
            raise ValueError(f"La ligne #{id_ligne} n'existe pas : un trajet doit se faire sur une ligne existante.")
        return ligne

    def _trajet_similaire_existe(self, ligne, heure_depart: datetime, id_trajet_ignore: int | None = None) -> bool:
        """Indique si un trajet existe déjà sur cette ligne avec exactement cette heure de départ."""
        trajets_du_jour = self.trajet_dao.rechercher(ligne.gare_depart, ligne.gare_arrivee, heure_depart)
        return any(
            trajet.heure_depart == heure_depart and trajet.id_trajet != id_trajet_ignore
            for trajet in trajets_du_jour
        )

from datetime import date, datetime

from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.trajet import Trajet
from src.utils.log_utils import log


class TrajetService:
    """Classe qui gère les opérations métier sur les trajets"""

    @log
    def creer(
        self,
        id_ligne: int,
        id_train: int,
        heure_depart: datetime,
        heure_arrivee: datetime,
        tarif_base: float,
    ) -> Trajet:
        """
        Méthode servant à créer un nouveau trajet.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne concernée
        id_train: int
            l'identifiant du train utilisé pour le trajet
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
        self._verifier_donnees(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)
        ligne = self._verifier_ligne(id_ligne)

        if self._trajet_similaire_existe(ligne, heure_depart):
            raise ValueError("Un trajet existe déjà sur cette ligne à cette date et à cette heure.")

        trajet = Trajet(
            id_trajet=None,
            heure_depart=heure_depart,
            heure_arrivee=heure_arrivee,
            id_ligne=id_ligne,
            id_train=id_train,
            tarif_base=tarif_base,
        )
        # TODO : remplacer par TrainDAO.trouver_par_id quand TrainDAO sera écrit
        try:
            return TrajetDAO().creer(trajet)
        except ForeignKeyViolation:
            raise ValueError(f"Le train #{id_train} n'existe pas.")

    @log
    def modifier(self, id_trajet: int, trajet: Trajet) -> bool:
        """
        Méthode servant à modifier les informations d'un trajet existant.

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
            si le trajet n'existe pas, si une donnée est invalide, si la ligne n'existe pas
            ou si un autre trajet existe déjà sur cette ligne à cette heure de départ
        """
        if trajet is None:
            raise ValueError("Le trajet à modifier est obligatoire.")
        if TrajetDAO().trouver_par_id(id_trajet) is None:
            raise ValueError(f"Le trajet #{id_trajet} n'existe pas.")

        self._verifier_donnees(
            trajet.id_ligne, trajet.id_train, trajet.heure_depart, trajet.heure_arrivee, trajet.tarif_base
        )
        ligne = self._verifier_ligne(trajet.id_ligne)

        if self._trajet_similaire_existe(ligne, trajet.heure_depart, id_trajet_ignore=id_trajet):
            raise ValueError("Un autre trajet existe déjà sur cette ligne à cette date et à cette heure.")

        trajet.id_trajet = id_trajet
        try:
            return TrajetDAO().modifier(trajet)
        except ForeignKeyViolation:
            raise ValueError(f"Le train #{trajet.id_train} n'existe pas.")

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
            return TrajetDAO().supprimer(id_trajet)
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

        return TrajetDAO().rechercher(gare_depart=gare_depart, gare_arrivee=gare_arrivee, date=date_voyage)

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
        return TrajetDAO().trouver_par_id(id_trajet)

    def _verifier_donnees(self, id_ligne, id_train, heure_depart, heure_arrivee, tarif_base) -> None:
        """Vérifie la validité des données d'un trajet (lève ValueError sinon)."""
        if id_ligne is None or id_train is None:
            raise ValueError("La ligne et le train sont obligatoires.")
        if not isinstance(heure_depart, datetime) or not isinstance(heure_arrivee, datetime):
            raise ValueError("Les heures de départ et d'arrivée doivent être des dates avec heure.")
        if heure_arrivee <= heure_depart:
            raise ValueError("L'heure d'arrivée doit être postérieure à l'heure de départ.")
        if tarif_base is None or tarif_base < 0:
            raise ValueError("Le tarif de base doit être positif ou nul.")

    def _verifier_ligne(self, id_ligne: int):
        """Vérifie que la ligne existe et la renvoie (lève ValueError sinon)."""
        ligne = LigneDAO().trouver_par_id(id_ligne)
        if ligne is None:
            raise ValueError(f"La ligne #{id_ligne} n'existe pas : un trajet doit se faire sur une ligne existante.")
        return ligne

    def _trajet_similaire_existe(self, ligne, heure_depart: datetime, id_trajet_ignore: int | None = None) -> bool:
        """Indique si un trajet existe déjà sur cette ligne avec exactement cette heure de départ."""
        # La recherche du DAO n'utilise que l'id des gares, pas leur nom
        gare_depart = Gare(ligne.id_gare_depart, None, None)
        gare_arrivee = Gare(ligne.id_gare_arrivee, None, None)
        trajets_du_jour = TrajetDAO().rechercher(gare_depart, gare_arrivee, heure_depart)
        return any(
            trajet.heure_depart == heure_depart and trajet.id_trajet != id_trajet_ignore
            for trajet in trajets_du_jour
        )
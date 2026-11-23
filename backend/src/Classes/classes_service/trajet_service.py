from datetime import date, datetime, timedelta

from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service import tarification
from src.Classes.classes_service.train_service import TrainService
from src.utils.log_utils import log
from src.utils.sncf_client import SncfClient


class TrajetService:
    """Classe qui gère les opérations métier sur les trajets"""

    def __init__(self):
        """Crée le DAO utilisé par le service."""
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
        # Le vrai train est chargé (et son existence vérifiée) AVANT d'appeler l'API SNCF
        train = TrainService().trouver_par_id(id_train)

        if self._trajet_similaire_existe(ligne, heure_depart):
            raise ValueError("Un trajet existe déjà sur cette ligne à cette date et à cette heure.")

        duree = self._calculer_duree(ligne, heure_depart)

        trajet = Trajet(
            heure_depart=heure_depart,
            heure_arrivee=heure_depart + timedelta(seconds=duree),
            ligne=ligne,
            train=train,
            tarif_base=float(tarif_base),
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
            si le trajet n'existe pas ou est déjà parti, si une donnée est invalide (dont une date de départ passée),
            si la ligne n'existe pas, si un autre trajet existe déjà sur cette ligne à cette heure
            de départ, si l'API SNCF ne trouve aucun itinéraire entre les deux gares,
            ou si le trajet a des réservations et que la modification changerait sa ligne
            ou lui donnerait un train trop petit pour les places déjà vendues
        requests.RequestException
            si l'API SNCF est indisponible
        """
        if trajet is None:
            raise ValueError("Le trajet à modifier est obligatoire.")
        ancien = self.trajet_dao.trouver_par_id(id_trajet)
        if ancien is None:
            raise ValueError(f"Le trajet #{id_trajet} n'existe pas.")
        # Un trajet déjà parti appartient à l'historique des clients : il n'est plus modifiable
        if ancien.heure_depart <= datetime.now(ancien.heure_depart.tzinfo):
            raise ValueError("Ce trajet est déjà parti : il ne peut plus être modifié.")

        id_ligne = trajet.ligne.id_ligne if trajet.ligne else None
        id_train = trajet.train.id_train if trajet.train else None
        self._verifier_donnees(id_ligne, id_train, trajet.heure_depart, trajet.tarif_base)
        ligne = self._verifier_ligne(id_ligne)
        # Avant l'appel à l'API SNCF : ne pas invalider les réservations déjà faites
        self._verifier_reservations(ancien, ligne, trajet.train)

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
    def rechercher(
        self, gare_depart: Gare, gare_arrivee: Gare, date_voyage: datetime | date | None = None
    ) -> list[Trajet]:
        """
        Méthode servant à rechercher des trajets disponibles.

        Param:
        ------
        gare_depart: Gare
            l'objet Gare de départ
        gare_arrivee: Gare
            l'objet Gare d'arrivée
        date_voyage: datetime | date | None
            la date de voyage souhaitée (seul le jour est pris en compte),
            ou None pour obtenir tous les trajets à venir

        Return:
        ------
        list[Trajet]
            la liste des trajets correspondants, triés par heure de départ (vide si aucun)

        Raises:
        ------
        ValueError
            si une gare est manquante ou si les deux gares sont identiques
        """
        if gare_depart is None or gare_arrivee is None:
            raise ValueError("La gare de départ et la gare d'arrivée sont obligatoires.")
        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise ValueError("La gare de départ et la gare d'arrivée doivent être différentes.")

        trajets = self.trajet_dao.rechercher(gare_depart=gare_depart, gare_arrivee=gare_arrivee, date=date_voyage)
        return self.ajouter_detail_prix(self.ajouter_places_restantes(trajets))

    @log
    def lister_a_venir(self) -> list[Trajet]:
        """
        Méthode servant à récupérer tous les trajets à venir, avec leurs places restantes.

        Return:
        ------
        list[Trajet]
            les trajets à venir, triés par heure de départ (vide si aucun)
        """
        return self.ajouter_places_restantes(self.trajet_dao.lister_a_venir())

    @staticmethod
    def ajouter_detail_prix(trajets: list[Trajet]) -> list[Trajet]:
        """
        Renseigne sur chaque trajet le détail de son prix en première et en seconde classe
        (TVA, péage réseau, coût d'exploitation, marge).
        Fonctionnalité F5 (tarification transparente).

        Param:
        ------
        trajets: list[Trajet]
            les trajets à compléter

        Return:
        ------
        list[Trajet]
            les mêmes trajets, avec detail_prix_premiere et detail_prix_seconde renseignés
        """
        for trajet in trajets:
            trajet.detail_prix_premiere = tarification.detail_prix(trajet.tarif_base, 1)
            trajet.detail_prix_seconde = tarification.detail_prix(trajet.tarif_base, 2)
        return trajets

    @log
    def places_libres(self, trajet: Trajet) -> dict[int, list[int]]:
        """
        Liste les numéros de place encore libres sur un trajet, classe par classe
        (les places vont de 1 à la capacité de la classe dans le train du trajet).

        Param:
        ------
        trajet: Trajet
            le trajet (son train doit être chargé, comme le fait TrajetDAO)

        Return:
        ------
        dict[int, list[int]]
            {1: places libres en première, 2: places libres en seconde}, triées par numéro

        Raises:
        ------
        ValueError
            si le trajet n'a pas de train
        """
        if trajet.train is None:
            raise ValueError("Aucun train n'est associé à ce trajet : il n'est pas réservable.")

        reservees = ReservationDAO().places_reservees(trajet.id_trajet)
        capacites = {1: trajet.train.places_premieres, 2: trajet.train.places_secondes}
        return {
            classe: [num for num in range(1, capacite + 1) if str(num) not in reservees.get(classe, set())]
            for classe, capacite in capacites.items()
        }

    @log
    def ajouter_places_restantes(self, trajets: list[Trajet]) -> list[Trajet]:
        """
        Calcule les places restantes de chaque trajet, en première et en seconde classe
        (capacité du train - places déjà réservées), et les renseigne sur les trajets.
        Fonctionnalité F5 (positionnement commercial) : le client voit les places restantes.

        Param:
        ------
        trajets: list[Trajet]
            les trajets à compléter (leur train doit être chargé, comme le fait TrajetDAO)

        Return:
        ------
        list[Trajet]
            les mêmes trajets, avec places_restantes_premiere et places_restantes_seconde renseignés
            (laissés à None pour un trajet sans train)
        """
        ids_trajets = [trajet.id_trajet for trajet in trajets if trajet.train is not None]
        reservees = ReservationDAO().compter_par_trajets(ids_trajets)

        for trajet in trajets:
            if trajet.train is None:
                continue
            par_classe = reservees.get(trajet.id_trajet, {})
            trajet.places_restantes_premiere = max(trajet.train.places_premieres - par_classe.get(1, 0), 0)
            trajet.places_restantes_seconde = max(trajet.train.places_secondes - par_classe.get(2, 0), 0)
        return trajets

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
        """
        Vérifie que les données d'un trajet sont valides.

        Param:
        ------
        id_ligne: int
            l'id de la ligne
        id_train: int
            l'id du train
        heure_depart: datetime
            la date et l'heure de départ
        tarif_base: float
            le prix de base du trajet

        Raises:
        ------
        ValueError
            si un id est manquant, si la date de départ est déjà passée
            ou si le tarif de base est manquant ou négatif
        TypeError
            si l'heure de départ n'est pas une date avec heure
        """
        if id_ligne is None or id_train is None:
            raise ValueError("La ligne et le train sont obligatoires.")
        if not isinstance(heure_depart, datetime):
            raise TypeError("L'heure de départ doit être une date avec heure.")
        # Un trajet passé ne serait jamais réservable : on refuse de le planifier.
        # (now() prend le fuseau de la date reçue, pour comparer deux dates de même nature)
        if heure_depart <= datetime.now(heure_depart.tzinfo):
            raise ValueError("La date de départ doit être dans le futur.")
        if tarif_base is None or tarif_base < 0:
            raise ValueError("Le tarif de base doit être positif ou nul.")

    @staticmethod
    def _verifier_reservations(ancien: Trajet, nouvelle_ligne, nouveau_train) -> None:
        """
        Si le trajet a déjà des réservations, refuse une modification qui les invaliderait :
        - changer de ligne (les passagers ont réservé ce parcours précis) ;
        - prendre un train trop petit : même règle que pour la capacité d'un train
          (nombre de réservations ou plus grand numéro de place réservé, par classe).
        Changer seulement l'horaire ou le tarif reste possible.

        Param:
        ------
            ancien (Trajet): le trajet qu'il faut peut-être modifier.
            nouvelle_ligne (Ligne): la ligne du trajet.
            nouveau_train (Train): le nouveau train pour ce trajet.

        Raises:
        ------
        ValueError
            si la modification invaliderait des réservations existantes
        """
        minimum = ReservationDAO().capacite_minimale_par_trajet(ancien.id_trajet)
        if not minimum:
            return  # aucune réservation : tout est modifiable

        if nouvelle_ligne.id_ligne != ancien.ligne.id_ligne:
            raise ValueError(
                "Impossible de changer la ligne d'un trajet qui a des réservations : "
                "les passagers ont réservé ce parcours."
            )

        for classe, capacite, libelle in (
            (1, nouveau_train.places_premieres, "première classe"),
            (2, nouveau_train.places_secondes, "seconde classe"),
        ):
            requis = minimum.get(classe, 0)
            if capacite < requis:
                places = "place" if capacite <= 1 else "places"
                raise ValueError(
                    f"Impossible d'utiliser le train numéro {nouveau_train.num_train} : "
                    f"il n'a que {capacite} {places} en {libelle}, alors que les réservations "
                    f"de ce trajet en demandent au moins {requis}."
                )

    def _calculer_duree(self, ligne, heure_depart: datetime) -> int:
        """
        Demande à l'API SNCF la durée du trajet sur cette ligne.

        Param:
        ------
        ligne: Ligne
            la ligne concernée
        heure_depart: datetime
            la date et l'heure de départ

        Return:
        ------
        int
            la durée du trajet, en secondes

        Raises:
        ------
        ValueError
            si les gares de la ligne ne viennent pas de l'API SNCF
            ou si aucun itinéraire n'est trouvé entre les deux gares
        requests.RequestException
            si l'API SNCF est indisponible
        """
        id_sncf_depart = ligne.gare_depart.id_sncf
        id_sncf_arrivee = ligne.gare_arrivee.id_sncf
        if not id_sncf_depart or not id_sncf_arrivee:
            raise ValueError(
                "Les gares de cette ligne ne viennent pas de l'API SNCF : temps de trajet impossible à calculer."
            )

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
        """Vérifie que la ligne existe et la renvoie (lève ValueError sinon).
        Param:
        ------
            id_ligne (int): l'id de la ligne à vérifier.
        Return:
        -------
            ligne(Ligne): la ligne vérifiée.
        Raises:
        -------
            ValueError: si la ligne n'exsite pas dans la base de données.
        """
        ligne = LigneDAO().trouver_par_id(id_ligne)
        if ligne is None:
            raise ValueError(f"La ligne #{id_ligne} n'existe pas : un trajet doit se faire sur une ligne existante.")
        return ligne

    def _trajet_similaire_existe(self, ligne, heure_depart: datetime, id_trajet_ignore: int | None = None) -> bool:
        """
        Indique si un trajet existe déjà sur cette ligne avec exactement la même heure de départ.

        Param:
        ------
        ligne: Ligne
            la ligne concernée
        heure_depart: datetime
            la date et l'heure de départ
        id_trajet_ignore: int | None
            l'id d'un trajet à ne pas prendre en compte (celui que l'on modifie)

        Return:
        ------
        bool
            True si un tel trajet existe, False sinon
        """
        trajets_du_jour = self.trajet_dao.rechercher(ligne.gare_depart, ligne.gare_arrivee, heure_depart)
        return any(
            trajet.heure_depart == heure_depart and trajet.id_trajet != id_trajet_ignore
            for trajet in trajets_du_jour
        )

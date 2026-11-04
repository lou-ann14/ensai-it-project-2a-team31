from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne


class LigneService:
    """Classe qui gère les opérations métier sur les lignes"""

    def creer(self, gare_depart: Gare, gare_arrivee: Gare, id_collaborateur: int | None = None) -> Ligne:
        """
        Méthode servant à créer une ligne.

        Param:
        ------
        gare_depart: Gare
            la gare de départ de la ligne
        gare_arrivee: Gare
            la gare d'arrivée de la ligne
        id_collaborateur: int | None
            l'id du collaborateur qui crée la ligne (optionnel)

        Return:
        ------
        Ligne
            la ligne créée, avec son id_ligne renseigné

        Raises:
        ------
        ValueError
            si une gare est manquante, si les deux gares sont identiques
            si la ligne existe déjà ou si le collaborateur n'existe pas
        """
        if gare_depart is None or gare_arrivee is None:
            raise ValueError("La gare de départ et la gare d'arrivée sont obligatoires.")
        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise ValueError("La gare de départ et la gare d'arrivée doivent être différentes.")
        if self.rechercher(gare_depart, gare_arrivee) is not None:
            raise ValueError("Une ligne existe déjà entre ces deux gares.")

        try:
            return LigneDAO().creer(gare_depart, gare_arrivee, id_collaborateur)
        except ForeignKeyViolation:
            raise ValueError(f"Le collaborateur #{id_collaborateur} n'existe pas.")

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne | None:
        """
        Méthode servant à rechercher la ligne reliant deux gares.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée

        Return:
        ------
        Ligne | None
            la ligne trouvée, ou None si aucune ligne ne relie ces deux gares
        """
        if gare_depart is None or gare_arrivee is None:
            return None
        return LigneDAO().rechercher(gare_depart=gare_depart, gare_arrivee=gare_arrivee)

    def trouver_par_id(self, id_ligne: int) -> Ligne | None:
        """
        Méthode servant à récupérer une ligne par son identifiant.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne

        Return:
        ------
        Ligne | None
            la ligne trouvée, ou None si elle n'existe pas
        """
        return LigneDAO().trouver_par_id(id_ligne)

    def modifier(self, ligne: Ligne) -> bool:
        """
        Méthode servant à modifier les gares d'une ligne.
        C'est refusé si des trajets existent sur cette ligne : leurs horaires et
        leur temps de trajet, calculés pour les anciennes gares, deviendraient faux.

        Param:
        ------
        ligne: Ligne
            la ligne contenant les nouvelles gares (identifiée par son id_ligne)

        Return:
        ------
        bool
            True si la modification a réussi, False sinon (ligne inexistante)

        Raises:
        ------
        ValueError
            si une gare est manquante, si les deux gares sont identiques,
            si une autre ligne relie déjà ces gares ou si la ligne a des trajets
        """
        if ligne.gare_depart is None or ligne.gare_arrivee is None:
            raise ValueError("La gare de départ et la gare d'arrivée sont obligatoires.")
        if ligne.gare_depart.id_gare == ligne.gare_arrivee.id_gare:
            raise ValueError("La gare de départ et la gare d'arrivée doivent être différentes.")

        autre_ligne = self.rechercher(ligne.gare_depart, ligne.gare_arrivee)
        if autre_ligne is not None and autre_ligne.id_ligne != ligne.id_ligne:
            raise ValueError("Une ligne existe déjà entre ces deux gares.")
        if LigneDAO().a_des_trajets(ligne.id_ligne):
            raise ValueError("Impossible de modifier une ligne qui a des trajets.")

        return LigneDAO().modifier(ligne)

    def supprimer(self, id_ligne: int) -> bool:
        """
        Méthode servant à supprimer une ligne.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False sinon (ligne inexistante)

        Raises:
        ------
        ValueError
            si des trajets existent encore sur cette ligne
        """
        try:
            return LigneDAO().supprimer(id_ligne)
        except ForeignKeyViolation:
            raise ValueError("Impossible de supprimer une ligne qui a des trajets.")

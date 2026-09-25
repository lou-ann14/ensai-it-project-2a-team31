from Classes_Objets import Gare, Ligne


class LigneDAO:

    def creer(self, ligne: Ligne) -> Ligne:
        """
        Persiste une nouvelle ligne dans la base de données.

        Param:
        ------
        ligne: Ligne
            l'objet Ligne contenant les informations de la ligne

        Return:
        ------
        Ligne
            l'objet Ligne après création (avec son ID assigné)
        """
        return ligne

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne:
        """
        Recherche une ligne reliant deux gares spécifiques.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée

        Return:
        ------
        Ligne
            l'objet Ligne correspondant au trajet
        """
        
        pass

    def trouver_par_id(id_ligne: int) -> Ligne:
        """
        Récupère une ligne spécifique par son identifiant.

        Param:
        ------
        id_ligne: int
            l'identifiant unique de la ligne

        Return:
        ------
        Ligne
            l'objet Ligne trouvé
        """
        pass

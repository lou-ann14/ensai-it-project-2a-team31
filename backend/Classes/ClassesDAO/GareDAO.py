from Classes_Objets.Gare import Gare


class GareDAO:
    def rechercher(self, nom: str | None, ville: str | None) -> Gare:
         """
        Recherche des gares en fonction du nom ou de la ville.

        Param:
        ------
        nom: str | None
            le nom de la gare (optionnel)
        ville: str | None
            la ville de la gare (optionnel)

        Return:
        ------
        Gare
            l'objet Gare correspondant à la recherche
        """
        pass

    def trouver_par_id(self, id_gare: int) -> Gare:
        """
        Récupère une gare spécifique par son identifiant.

        Param:
        ------
        id_gare: int
            l'identifiant unique de la gare

        Return:
        ------
        Gare
            l'objet Gare trouvé
        """
       
       
        pass

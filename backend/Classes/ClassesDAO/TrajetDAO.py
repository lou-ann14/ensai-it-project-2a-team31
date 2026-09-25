from Classes_Objets.Gare import Gare
from Classes_Objets.Trajet import Trajet


class TrajetDAO:
    """classe qui intéragit avec la base de données pour les objets de type Trajet
    """
    def creer(self, trajet: Trajet):
        """
        Enregistre un nouveau trajet dans la base de données.

        Param:
        ------
        trajet: Trajet
            l'objet Trajet à enregistrer

        Return:
        ------
        Trajet
            l'objet Trajet créé
        """
        pass

    def modifier(self, trajet: Trajet):
         """
        Met à jour les informations d'un trajet existant.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à modifier
        trajet: Trajet
            l'objet contenant les nouvelles données

        Return:
        ------
        Trajet
            l'objet Trajet mis à jour
        """
        pass

    def supprimer(self, trajet: Trajet):
        """
        Supprime un trajet de la base de données.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False sinon
        """
        pass

    def rechercher(self, gare_arrivee: Gare, gare_depart: Gare):
       """
        Recherche des trajets selon les critères de lieu et de date.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée
        date: datetime
            la date recherchée

        Return:
        ------
        list
            une liste d'objets Trajet
        """ 
        pass

    def trouver_par_id(self, id_trajet: int):
        """
        Récupère un trajet spécifique par son identifiant.

        Param:
        ------
        id_trajet: int
            l'identifiant unique du trajet

        Return:
        ------
        Trajet
            l'objet Trajet trouvé
        """
        pass

from Classes.Classes_Service.ReservationService import ReservationService
from Classes.Classes_Service.ClientService import ClientService
from Classes.Classes_Service.CollaborateurService import CollaborateurService
from Classes.Classes_Service.UtilisateurService import UtilisateurService
from Classes_Objets.Trajet import Trajet
from Classes_Objets.Gare import Gare
from datetime import datetime

class TrajetService():
    def creer(self, id_ligne: int, id_train: int, heure_depart: datetime, heure_arrivee: datetime, tarif_base: float):
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
        int
            l'id du nouveau trajet créé
        """
        
        pass
    
    def modifier(self, id_trajet: int, trajer: Trajet):
        """
        Méthode servant à modifier les informations d'un trajet existant.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à modifier
        trajer: Trajet
            l'objet Trajet contenant les nouvelles informations

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """
        pass

    def supprimer(self, id_trajet: int):

        """
        Méthode servant à supprimer un trajet.

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

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare, date: datetime):
        """
        Méthode servant à rechercher des trajets disponibles.

        Param:
        ------
        gare_depart: Gare
            l'objet Gare de départ
        gare_arrivee: Gare
            l'objet Gare d'arrivée
        date: datetime
            la date de voyage souhaitée

        Return:
        ------
        list
            une liste d'objets Trajet correspondant aux critères de recherche
        """
        pass



from Classes.Classes_Service.ReservationService import ReservationService
from Classes.Classes_Service.ClientService import ClientService
from Classes.Classes_Service.CollaborateurService import CollaborateurService
from Classes.Classes_Service.UtilisateurService import UtilisateurService


class TrajetService():
    def creer(id_ligne: int, id_train: int, heure_depart: datetime, heure_arrivee: datetime, tarif_base: float):
        pass
    
    def modifier(id_trajet: int, trajer: Trajet):
        pass

    def supprimer(id_trajet: int):
        pass

    def rechercher(gare_depart: Gare, gare_arrivee: Gare, date: datetime):
        pass
    


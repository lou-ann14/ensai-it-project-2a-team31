from classes.classes_service.reservation_service import reservation_service
from classes.classes_service.client_service import client_service
from classes.classes_service.collaborateur_service import collaborateur_service
from classes.classes_service.utilisateur_service import utilisateur_service
from classes_objets.trajet import trajet
from classes_objets.gare import gare
from datetime import datetime

class TrajetService():
    def creer(self, id_ligne: int, id_train: int, heure_depart: datetime, heure_arrivee: datetime, tarif_base: float):
        pass
    
    def modifier(self, id_trajet: int, trajer: Trajet):
        pass

    def supprimer(self, id_trajet: int):
        pass

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare, date: datetime):
        pass



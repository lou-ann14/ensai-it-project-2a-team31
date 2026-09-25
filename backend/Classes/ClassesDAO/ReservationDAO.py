from Classes_Objets import Reservation


class ReservationDAO:

    def creer(
        self,
        id_reservation: int,
        id_client: int,
        id_trajet: int,
        place: str,
        classe: int,
        prix: float
    ) -> Reservation:
        return Reservation(id_reservation, id_client, id_trajet, place, classe, prix)

    def annuler(self, id_reservation: int):
        pass

    def trouver_par_client(self, id_client: int):
        pass

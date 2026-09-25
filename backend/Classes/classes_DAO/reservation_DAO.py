from classes_objets import reservation


class ReservationDAO:

    def creer(
        self,
        id_reservation: int,
        id_client: int,
        id_trajet: int,
        place: str,
        classe: int,
        prix: float
<<<<<<< HEAD:backend/Classes/classes_DAO/reservation_DAO.py
    ) -> reservation:
        return reservation(id_reservation, id_client, id_trajet, place, classe, prix)
=======
        ) -> Reservation:
        """
        Enregistre une nouvelle réservation dans la base de données.

        Param:
        ------
        id_reservation: int
            l'identifiant de la réservation
        id_client: int
            l'identifiant du client
        id_trajet: int
            l'identifiant du trajet
        place: str
            le numéro de place
        classe: int
            la classe de voyage
        prix: float
            le prix payé

        Return:
        ------
        Reservation
            l'objet Reservation créé
        """

        return Reservation(id_reservation, id_client, id_trajet, place, classe, prix)
>>>>>>> edb78a65a60f6d3edff5f9e47a2f4c85404b8afb:backend/Classes/ClassesDAO/ReservationDAO.py

    def annuler(self, id_reservation: int):
         """
        Supprime ou marque une réservation comme annulée dans la base de données.

        Param:
        ------
        id_reservation: int
            l'identifiant de la réservation à annuler

        Return:
        ------
        bool
            True si l'annulation a réussi, False sinon
        """
        
        pass

    def trouver_par_client(self, id_client: int):
        """
        Récupère toutes les réservations d'un client spécifique.

        Param:
        ------
        id_client: int
            l'identifiant du client

        Return:
        ------
        list
            une liste d'objets Reservation
        """
        pass

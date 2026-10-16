from typing import Any

from psycopg2.extras import DictCursor


class ClientService:
    def __init__(self, conn):
        self.conn = conn

    def reserver_trajet(self, id_client: int, id_trajet: int, places: int, prix: float, tarif: str) -> int | None:
        query = """
            INSERT INTO reservations (id_trajet, id_client, places_restantes, prix, tarif)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_reservation;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_trajet, id_client, places, prix, tarif))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            return new_id

    def voir_historique_reservations(self, id_client: int) -> list[dict[str, Any]]:
        query = """
            SELECT r.id_reservation, r.places_restantes, r.prix, r.tarif, t.heure_depart, t.heure_arrivee
            FROM reservations r
            JOIN trajets t ON r.id_trajet = t.id_trajet
            WHERE r.id_client = %s; 
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (id_client,))
            return [dict(row) for row in cur.fetchall()]
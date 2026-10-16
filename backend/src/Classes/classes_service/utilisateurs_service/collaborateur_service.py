from datetime import datetime


class CollaborateurService:
    def __init__(self, conn):
        self.conn = conn

    def creer_ligne(self, gare_depart_id: int, gare_arrivee_id: int, id_collaborateur: int) -> int | None:
        query = """
            INSERT INTO lignes (gare_depart_id, gare_arrivee_id, id_collaborateur)
            VALUES (%s, %s, %s)
            RETURNING id_ligne;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (gare_depart_id, gare_arrivee_id, id_collaborateur))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            return new_id

    def creer_trajet(self, id_ligne: int, heure_depart: datetime, heure_arrivee: datetime, temps_trajet: int) -> int | None:
        query = """
            INSERT INTO trajets (id_ligne, heure_depart, heure_arrivee, temps_trajet)
            VALUES (%s, %s, %s, %s)
            RETURNING id_trajet;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_ligne, heure_depart, heure_arrivee, temps_trajet))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            return new_id
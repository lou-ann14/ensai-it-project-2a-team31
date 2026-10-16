from datetime import date, datetime
from typing import Any

from psycopg2.extras import DictCursor


class UtilisateurService:
    def __init__(self, conn):
        self.conn = conn

    def creer_compte(self, nom_utilisateur: str, mdp: str, role: str) -> int | None:
        query = """
            INSERT INTO utilisateurs (nom_utilisateur, mdp, role, date_inscription)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (nom_utilisateur, mdp, role, date.today()))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            return new_id

    def recherche_trajet(self, id_gare_depart: int, id_gare_arrivee: int, date_trajet: datetime) -> list[dict[str, Any]]:
        query = """
            SELECT t.id_trajet, t.heure_depart, t.heure_arrivee, t.temps_trajet
            FROM trajets t
            JOIN lignes l ON t.id_ligne = l.id_ligne
            WHERE l.gare_depart_id = %s 
              AND l.gare_arrivee_id = %s
              AND DATE(t.heure_depart) = DATE(%s);
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (id_gare_depart, id_gare_arrivee, date_trajet))
            return [dict(row) for row in cur.fetchall()]

    def recherche_gare(self, nom: str | None = None, ville: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT id_gare, nom, ville FROM gares WHERE 1=1"
        params = []
        if nom:
            query += " AND nom ILIKE %s"
            params.append(f"%{nom}%")
        if ville:
            query += " AND ville ILIKE %s"
            params.append(f"%{ville}%")
            
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]

    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str) -> bool:
        check_query = "SELECT id FROM utilisateurs WHERE id = %s AND mdp = %s;"
        update_query = "UPDATE utilisateurs SET mdp = %s WHERE id = %s;"
        with self.conn.cursor() as cur:
            cur.execute(check_query, (id_utilisateur, ancien_mdp))
            if cur.fetchone():
                cur.execute(update_query, (nouveau_mdp, id_utilisateur))
                self.conn.commit()
                return True
            return False

    def _rechercher(self, nom_utilisateur: str | None = None, id_utilisateur: int | None = None) -> dict[str, Any] | None:
        query = "SELECT id, nom_utilisateur, role, date_inscription FROM utilisateurs WHERE "
        if id_utilisateur:
            query += "id = %s;"
            param = id_utilisateur
        elif nom_utilisateur:
            query += "nom_utilisateur = %s;"
            param = nom_utilisateur
        else:
            return None

        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (param,))
            row = cur.fetchone()
            return dict(row) if row else None
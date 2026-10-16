from .utilisateur_service import UtilisateurService


class AdministrateurService:
    def __init__(self, conn, utilisateur_service: UtilisateurService):
        self.conn = conn
        self.utilisateur_service = utilisateur_service

    def gerer_habilitation(self, id_utilisateur: int, nouveau_role: str) -> None:
        query = "UPDATE utilisateurs SET role = %s WHERE id = %s;"
        with self.conn.cursor() as cur:
            cur.execute(query, (nouveau_role, id_utilisateur))
            self.conn.commit()

    def recherche_compte(self, nom_utilisateur: str | None = None, id_utilisateur: int | None = None):
        return self.utilisateur_service._rechercher(nom_utilisateur, id_utilisateur)
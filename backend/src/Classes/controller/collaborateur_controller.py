from fastapi import APIRouter, Depends, status
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import (
    CollaborateurService,
)
from src.schema.collaborateur_schema import (
    LigneCreationModel,
    LigneCreeeModel,
    TrajetCreationModel,
    TrajetCreeModel,
)
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_collaborateur_service():
    """Dependency Injection provider for CollaborateurService."""
    return CollaborateurService(DBConnexion().connexion)


@router.post(
    "/lignes",
    response_model=LigneCreeeModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Collaborateur"],
)
def creer_ligne(ligne: LigneCreationModel, collaborateur_service=Depends(get_collaborateur_service)):
    """Permet à un collaborateur de créer une ligne
    Param:
        ligne: la gare de départ, la gare d'arrivée et l'id du collaborateur
    Returns:
        LigneCreeeModel : un message de confirmation et l'id de la ligne créée
    """
    logger.info("Création d'une ligne")

    id_ligne = collaborateur_service.creer_ligne(
        ligne.gare_depart_id,
        ligne.gare_arrivee_id,
        ligne.id_collaborateur,
    )

    return {"message": "Création de la ligne réussie", "id_ligne": id_ligne}


@router.post(
    "/trajets",
    response_model=TrajetCreeModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Collaborateur"],
)
def creer_trajet(trajet: TrajetCreationModel, collaborateur_service=Depends(get_collaborateur_service)):
    """Permet à un collaborateur de créer un trajet
    Param:
        trajet: l'id de la ligne, les heures de départ et d'arrivée et le temps de trajet en minutes
    Returns:
        TrajetCreeModel : un message de confirmation et l'id du trajet créé
    """
    logger.info("Création d'un trajet")

    id_trajet = collaborateur_service.creer_trajet(
        trajet.id_ligne,
        trajet.heure_depart,
        trajet.heure_arrivee,
        trajet.temps_trajet,
    )

    return {"message": "Création du trajet réussie", "id_trajet": id_trajet}

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import (
    CollaborateurService,
)
from src.schema.collaborateur_schema import (
    LigneCreationModel,
    LigneCreeeModel,
    TrajetCreationModel,
    TrajetCreeModel,
)
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_collaborateur_service():
    """Dependency Injection provider for CollaborateurService."""
    return CollaborateurService()


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
    Raises:
        HTTPException: erreur 400 si une gare ou le collaborateur n'existe pas, si les deux gares
                       sont identiques ou si la ligne existe déjà
    """
    logger.info("Création d'une ligne")

    try:
        nouvelle_ligne = collaborateur_service.creer_ligne(
            ligne.gare_depart_id,
            ligne.gare_arrivee_id,
            ligne.id_collaborateur,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Création de la ligne réussie", "id_ligne": nouvelle_ligne.id_ligne}


@router.post(
    "/trajets",
    response_model=TrajetCreeModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Collaborateur"],
)
def creer_trajet(trajet: TrajetCreationModel, collaborateur_service=Depends(get_collaborateur_service)):
    """Permet à un collaborateur de créer un trajet
    Param:
        trajet: l'id de la ligne, l'id du train, l'heure de départ et le tarif de base
    Returns:
        TrajetCreeModel : un message de confirmation, l'id du trajet créé,
                          et l'heure d'arrivée et le temps de trajet calculés avec l'API SNCF
    Raises:
        HTTPException: erreur 400 si une donnée est invalide, si la ligne ou le train n'existe pas
                       si un trajet existe déjà sur cette ligne à cette heure
                       ou si l'API SNCF ne trouve aucun itinéraire
        HTTPException: erreur 502 si l'API SNCF est indisponible
    """
    logger.info("Création d'un trajet")

    try:
        nouveau_trajet = collaborateur_service.creer_trajet(
            trajet.id_ligne,
            trajet.id_train,
            trajet.heure_depart,
            trajet.tarif_base,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException:
        logger.exception("Erreur lors de l'appel à l'API SNCF")
        raise HTTPException(status_code=502, detail="L'API SNCF est indisponible ou a refusé la requête.")

    return {
        "message": "Création du trajet réussie",
        "id_trajet": nouveau_trajet.id_trajet,
        "heure_arrivee": nouveau_trajet.heure_arrivee,
        "temps_trajet": nouveau_trajet.temps_trajet,
    }

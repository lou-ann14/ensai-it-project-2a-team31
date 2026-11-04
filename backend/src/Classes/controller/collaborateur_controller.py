import requests
from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import (
    CollaborateurService,
)
from src.schema.collaborateur_schema import (
    LigneCreationModel,
    LigneCreeeModel,
    LigneModificationModel,
    LigneModifieeModel,
    MessageModel,
    TrajetCreationModel,
    TrajetCreeModel,
    TrajetModificationModel,
    TrajetModifieModel,
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


@router.put("/lignes/{id_ligne}", response_model=LigneModifieeModel, tags=["Collaborateur"])
def modifier_ligne(
    id_ligne: int,
    ligne: LigneModificationModel,
    collaborateur_service=Depends(get_collaborateur_service),
):
    """Permet à un collaborateur de modifier les gares d'une ligne
    Param:
        id_ligne (int) : l'id de la ligne à modifier
        ligne: la nouvelle gare de départ et la nouvelle gare d'arrivée
    Returns:
        LigneModifieeModel : un message de confirmation et l'id de la ligne
    Raises:
        HTTPException: erreur 400 si une gare n'existe pas, si les deux gares sont identiques,
                       si une autre ligne relie déjà ces gares ou si la ligne a des trajets
        HTTPException: erreur 404 si la ligne n'existe pas
    """
    logger.info("Modification d'une ligne")

    try:
        ligne_modifiee = collaborateur_service.modifier_ligne(id_ligne, ligne.gare_depart_id, ligne.gare_arrivee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if ligne_modifiee is None:
        raise HTTPException(status_code=404, detail=f"La ligne #{id_ligne} n'existe pas.")

    return {"message": "Modification de la ligne réussie", "id_ligne": id_ligne}


@router.delete("/lignes/{id_ligne}", response_model=MessageModel, tags=["Collaborateur"])
def supprimer_ligne(id_ligne: int, collaborateur_service=Depends(get_collaborateur_service)):
    """Permet à un collaborateur de supprimer une ligne
    Param:
        id_ligne (int) : l'id de la ligne à supprimer
    Returns:
        MessageModel : un message de confirmation
    Raises:
        HTTPException: erreur 400 si des trajets existent encore sur cette ligne
        HTTPException: erreur 404 si la ligne n'existe pas
    """
    logger.info("Suppression d'une ligne")

    try:
        supprimee = collaborateur_service.supprimer_ligne(id_ligne)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not supprimee:
        raise HTTPException(status_code=404, detail=f"La ligne #{id_ligne} n'existe pas.")

    return {"message": "Suppression de la ligne réussie"}


@router.put("/trajets/{id_trajet}", response_model=TrajetModifieModel, tags=["Collaborateur"])
def modifier_trajet(
    id_trajet: int,
    trajet: TrajetModificationModel,
    collaborateur_service=Depends(get_collaborateur_service),
):
    """Permet à un collaborateur de modifier un trajet
    Param:
        id_trajet (int) : l'id du trajet à modifier
        trajet: l'id de la ligne, l'id du train, l'heure de départ et le tarif de base
    Returns:
        TrajetModifieModel : un message de confirmation, l'id du trajet,
                             et l'heure d'arrivée et le temps de trajet recalculés avec l'API SNCF
    Raises:
        HTTPException: erreur 400 si une donnée est invalide, si la ligne ou le train n'existe pas,
                       si un autre trajet existe déjà sur cette ligne à cette heure
                       ou si l'API SNCF ne trouve aucun itinéraire
        HTTPException: erreur 404 si le trajet n'existe pas
        HTTPException: erreur 502 si l'API SNCF est indisponible
    """
    logger.info("Modification d'un trajet")

    try:
        trajet_modifie = collaborateur_service.modifier_trajet(
            id_trajet,
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
    if trajet_modifie is None:
        raise HTTPException(status_code=404, detail=f"Le trajet #{id_trajet} n'existe pas.")

    return {
        "message": "Modification du trajet réussie",
        "id_trajet": id_trajet,
        "heure_arrivee": trajet_modifie.heure_arrivee,
        "temps_trajet": trajet_modifie.temps_trajet,
    }


@router.delete("/trajets/{id_trajet}", response_model=MessageModel, tags=["Collaborateur"])
def supprimer_trajet(id_trajet: int, collaborateur_service=Depends(get_collaborateur_service)):
    """Permet à un collaborateur de supprimer un trajet
    Param:
        id_trajet (int) : l'id du trajet à supprimer
    Returns:
        MessageModel : un message de confirmation
    Raises:
        HTTPException: erreur 400 si des réservations existent encore sur ce trajet
        HTTPException: erreur 404 si le trajet n'existe pas
    """
    logger.info("Suppression d'un trajet")

    try:
        supprime = collaborateur_service.supprimer_trajet(id_trajet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not supprime:
        raise HTTPException(status_code=404, detail=f"Le trajet #{id_trajet} n'existe pas.")

    return {"message": "Suppression du trajet réussie"}

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import (
    CollaborateurService,
)
from src.Classes.controller.utilisateur_controller import get_gare_service, trouver_gare
from src.schema.collaborateur_schema import (
    LigneCreeeModel,
    LigneModifieeModel,
    MessageModel,
    TrajetCreationModel,
    TrajetCreeModel,
    TrajetModificationModel,
    TrajetModifieModel,
)
from src.schema.gare_schema import GareReponseModel
from src.schema.train_schema import TrainBaseModel, TrainReponseModel
from src.utils.log_utils import get_logger
from src.utils.securite import verif_token

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
def creer_ligne(
    gare_depart: str,
    gare_arrivee: str,
    id_collaborateur: int,
    collaborateur_service=Depends(get_collaborateur_service),
    gare_service=Depends(get_gare_service),
    collab=Depends(verif_token),
):
    """Permet à un collaborateur de créer une ligne
    Param:
        gare_depart (str) : le nom de la gare de départ
        gare_arrivee (str) : le nom de la gare d'arrivée
        id_collaborateur (int) : l'id du collaborateur
    Returns:
        LigneCreeeModel : un message de confirmation et l'id de la ligne créée
    Raises:
        HTTPException: erreur 400 si le collaborateur n'existe pas, si les deux gares sont identiques,
                       si la ligne existe déjà, ou si un nom de gare est vide ou correspond à plusieurs gares
        HTTPException: erreur 404 si aucune gare ne correspond à un nom
    """
    logger.info("Création d'une ligne")
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")

    depart = trouver_gare(gare_depart, gare_service)
    arrivee = trouver_gare(gare_arrivee, gare_service)

    try:
        nouvelle_ligne = collaborateur_service.creer_ligne(
            depart.id_gare,
            arrivee.id_gare,
            id_collaborateur,
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
def creer_trajet(trajet: TrajetCreationModel, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
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
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
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
    gare_depart: str,
    gare_arrivee: str,
    collaborateur_service=Depends(get_collaborateur_service),
    gare_service=Depends(get_gare_service),
    collab=Depends(verif_token)
):
    """Permet à un collaborateur de modifier les gares d'une ligne
    Param:
        id_ligne (int) : l'id de la ligne à modifier
        gare_depart (str) : le nom de la nouvelle gare de départ
        gare_arrivee (str) : le nom de la nouvelle gare d'arrivée
    Returns:
        LigneModifieeModel : un message de confirmation et l'id de la ligne
    Raises:
        HTTPException: erreur 400 si les deux gares sont identiques, si une autre ligne relie déjà
                       ces gares, si la ligne a des trajets, ou si un nom de gare est vide
                       ou correspond à plusieurs gares
        HTTPException: erreur 404 si la ligne n'existe pas ou si aucune gare ne correspond à un nom
    """
    logger.info("Modification d'une ligne")
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")

    depart = trouver_gare(gare_depart, gare_service)
    arrivee = trouver_gare(gare_arrivee, gare_service)

    try:
        ligne_modifiee = collaborateur_service.modifier_ligne(id_ligne, depart.id_gare, arrivee.id_gare)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if ligne_modifiee is None:
        raise HTTPException(status_code=404, detail=f"La ligne #{id_ligne} n'existe pas.")

    return {"message": "Modification de la ligne réussie", "id_ligne": id_ligne}


@router.delete("/lignes/{id_ligne}", response_model=MessageModel, tags=["Collaborateur"])
def supprimer_ligne(id_ligne: int, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
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
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
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
    collab=Depends(verif_token)
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
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
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
def supprimer_trajet(id_trajet: int, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
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
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        supprime = collaborateur_service.supprimer_trajet(id_trajet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not supprime:
        raise HTTPException(status_code=404, detail=f"Le trajet #{id_trajet} n'existe pas.")

    return {"message": "Suppression du trajet réussie"}


@router.post("/gares/importer", response_model=list[GareReponseModel], tags=["Collaborateur"])
def importer_gares(q: str, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
    """Importe dans notre base les gares trouvées sur l'API SNCF
    Param:
        q (str) : texte à rechercher (au moins 2 caractères)
    Returns:
        list[GareReponseModel] : les gares importées
    Raises:
        HTTPException: erreur 400 si le texte est trop court
        HTTPException: erreur 502 si l'API SNCF est indisponible
    """
    logger.info("Import de gares depuis l'API SNCF")
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        return collaborateur_service.importer_gares(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException:
        logger.exception("Erreur lors de l'appel à l'API SNCF")
        raise HTTPException(status_code=502, detail="L'API SNCF est indisponible ou a refusé la requête.")


@router.post(
    "/trains",
    response_model=TrainReponseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Collaborateur"],
)
def creer_train(train: TrainBaseModel, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
    """Permet à un collaborateur de créer un train
    Param:
        train: le type, les places en 1re et en 2de classe et le numéro du train
    Returns:
        TrainReponseModel : le train créé, avec son id_train
    Raises:
        HTTPException: erreur 400 si la capacité est incorrecte ou si le numéro existe déjà
    """
    logger.info("Création d'un train")
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        return collaborateur_service.creer_train(
            train.type_train,
            train.places_premieres,
            train.places_secondes,
            train.num_train,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/trains/{num_train}", response_model=TrainReponseModel, tags=["Collaborateur"])
def modifier_capacite(num_train: int, t: TrainBaseModel, collaborateur_service=Depends(get_collaborateur_service), collab=Depends(verif_token)):
    """Permet à un collaborateur de modifier la capacité d'un train
    Param:
        num_train (int) : le numéro du train à modifier
        t: le train avec ses nouvelles places en 1re et en 2de classe
    Returns:
        TrainReponseModel : le train modifié
    Raises:
        HTTPException: erreur 400 si la capacité est incorrecte
        HTTPException: erreur 404 si le train n'existe pas
        HTTPException: erreur 500 si la modification ne s'exécute pas
    """
    logger.info("Modification de la capacité d'un train")
    if collab.grade != "COLLABORATEUR":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        train = collaborateur_service.modifier_capacite(num_train, t.places_premieres, t.places_secondes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if train is None:
        raise HTTPException(status_code=500, detail="Erreur pendant la modification du train.")

    return train

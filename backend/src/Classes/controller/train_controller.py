from fastapi import APIRouter, Depends, HTTPException
from src.Classes.classes_service.train_service import TrainService
from src.schema.train_schema import TrainBaseModel
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)

def get_train_service():
    """Dependency Injection provider for PlayerService."""
    return TrainService()

@router.get("/{id_train}", response_model=list[TrainBaseModel], tags=["Trains"])
async def trouve_par_id(id_train, train_service=Depends(get_train_service)):
    """Trouve un train à l'aide de son id
    Param:
        id_train (int)
    Returns:
        TrainBaseModel
    Raises:
        HTTPException: erreur 404 si le train n'est pas trouvé
    """
    logger.info("Trouve un train par son id")
    train = train_service.trouver_par_id(id_train)
    if not train:
        raise HTTPException(status_code=404, detail="Train (id={id_train}) non trouvé.")
    return train



@router.post("/", response_model=TrainBaseModel, tags=["Trains"])
async def creer_train(train: TrainBaseModel, train_service=Depends(get_train_service)):
    """Créer un nouveau train.
    Param:
        p (PlayerModel): The player data to create.
        player_service (PlayerService): The service used to interact with player data.
    Returns:
        PlayerReadModel: The newly created player data.
    Raises:
        HTTPException: 400 error if the username is already taken.
        HTTPException: 500 error if the creation process fails.
    """
    logger.info("Créer un train")

    train = train_service.create(train.type_train, train.places_initiales)
    if not train:
        raise HTTPException(status_code=500, detail="Erreur pendant la création du train")

    return train

@router.post("/{id_train}", response_model=TrainBaseModel, tags=["Trains"])
async def modifier_capacite(id_train : int, t : TrainBaseModel, train_service=Depends(get_train_service)):
    """Modifie la capacité d'un train
    Param:
        id_train : int
    Returns:
        TrainBaseModel : le train modifié
    Raises:
        HTTPException: erreur 404 si le train n'existe pas
        HTTPExecption: erreur 500 si la modification ne s'exécute pas
    """
    logger.info("Modification d'un train")

    train = train_service.trouver_par_id(id_train)
    if not train:
        raise HTTPException(status_code=404, detail="Train (id={id_train}) non trouvé.")
    
    train.places_initiales = t.places_initiales

    train = train_service.modifier_capacite(train.places_initiales)
    if not train:
        raise HTTPException(status_code=500, detail="Ereur pendant la modification du train.")

    return train
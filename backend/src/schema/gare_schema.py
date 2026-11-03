from pydantic import BaseModel, ConfigDict


class GareReponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_gare: int | None = None
    nom: str | None = None
    ville: str | None = None
    id_sncf: str | None = None
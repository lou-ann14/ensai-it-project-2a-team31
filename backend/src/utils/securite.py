import hashlib

from fastapi import Header, HTTPException
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO


def hash_password(mdp: str, salt: str = "") -> str:
    """Hash un mot de passe avec l'algorithme SHA-256.
    Param:
        mdp (str): Le mot de passe à hasher
        salt (str, optional): Un string ajouté au mot de passe avant de hasher
            pour se protéger contre les attaques rainbow table.
    Returns:
        str: hash string résultant du hashage
    """
    password_bytes = mdp.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verif_niv_hab(niv_hab: str, x_auth_token=Header(None)) -> UtilisateurDAO:
    """Verifies the authenticity of a player via the provided auth token.

    This function checks if a token is present in the request headers and
    validates it against the database.
    Args:
        x_auth_token (str, optional): The token extracted from the
            'X-Auth-Token' HTTP header. Defaults to None.
    Returns:
        Player object associated with the valid token.
    Raises:
        HTTPException: 401 error if the token is missing.
        HTTPException: 401 error if the token is not found in the database.
    """
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Token manquant.")

    utilisateur = UtilisateurDAO().find_by_token(x_auth_token)
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Token invalide.")
    if utilisateur.grade != niv_hab:
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")

    return utilisateur
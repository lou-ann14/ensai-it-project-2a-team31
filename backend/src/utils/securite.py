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


def verif_token(x_auth_token=Header(None)) -> UtilisateurDAO:
    """Vérifie l'authentification d'un utilisateur via un token donné.

    Cette fonction vérifie si un token est présent dans les arguments d'une fonction
    et valide le token à l'aide de la base de données.
    Param:
        x_auth_token (str, otpionnel): Le token extrait depuis le 'X-AUth-Token' dans le header HTTP. 
            None par défaut.
    Returns:
        L'utilisateur avec le bon token.
    Raises:
        HTTPException: 401 error if the token is missing.
        HTTPException: 401 error if the token is not found in the database.
    """
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Token manquant.")

    utilisateur = UtilisateurDAO().trouver_par_token(x_auth_token)
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Token invalide.")

    return utilisateur
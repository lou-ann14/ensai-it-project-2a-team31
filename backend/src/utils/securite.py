import hashlib

from fastapi import Header, HTTPException
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur


def hash_password(mdp: str, salt: str = "") -> str:
    """Hash un mot de passe avec l'algorithme SHA-256.
    Param:
        mdp (str): Le mot de passe à hasher
        salt (str, optional): Un string ajouté au mot de passe avant de hasher
            pour se protéger contre les attaques rainbow table.
    Return:
        str: hash string résultant du hashage
    """
    password_bytes = mdp.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


# Hiérarchie des habilitations : chaque grade dispose aussi des droits des grades inférieurs
# (un collaborateur peut faire tout ce que fait un client, un administrateur tout ce que fait
# un collaborateur).
NIVEAUX_GRADE = {"CLIENT": 1, "COLLABORATEUR": 2, "ADMIN": 3}


def _a_le_grade(utilisateur, grade_minimum: str) -> bool:
    """Indique si l'utilisateur a au moins le grade demandé.
    Param:
        utilisateur: l'utilisateur connecté (objet ayant un attribut grade)
        grade_minimum (str): "CLIENT", "COLLABORATEUR" ou "ADMIN"
    Return:
        bool: True si son grade est égal ou supérieur au grade demandé
    """
    return NIVEAUX_GRADE.get(utilisateur.grade, 0) >= NIVEAUX_GRADE[grade_minimum]


def verifier_grade(utilisateur, grade_minimum: str) -> None:
    """Refuse l'action si l'utilisateur n'a pas au moins le grade demandé.
    Raises:
        HTTPException: 403 error si le grade est insuffisant.
    """
    if not _a_le_grade(utilisateur, grade_minimum):
        raise HTTPException(
            status_code=403,
            detail=f"Vous n'avez pas le niveau d'habilitation requis ({grade_minimum} ou supérieur).",
        )


def verif_token(x_auth_token=Header(None)) -> Utilisateur:
    """Vérifie l'authentification d'un utilisateur via un token donné.

    Cette fonction vérifie si un token est présent dans les arguments d'une fonction
    et valide le token à l'aide de la base de données.
    Param:
        x_auth_token (str, otpionel): Le token extrait depuis le 'X-AUth-Token' dans le header HTTP. 
            None par défaut.
    Return:
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
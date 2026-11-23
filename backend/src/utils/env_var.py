import logging

import dotenv


def load_environment_variables():
    """Charge les variables d'environnement depuis le fichier .env ."""
    succes = dotenv.load_dotenv(override=True)
    logging.info(f"Charge les variables d'environnement: {'SUCCES' if succes else 'FAIL'}")


def mask_value(clé, valeur):
    """Masque des valeurs sensibles à partir de mots clés.
    Param:
        clé (str): Le nom de la variable d'environnement.
        valeur (str): La véritable valeur de la variable d'environnement.
    Return:
        str: Le string ("*******") si la clé contient un mot clé sensible, 
            autrement la valeur originelle.
    """
    sensitive_keywords = ["PASSWORD", "SECRET", "KEY", "TOKEN"]

    if any(word in clé.upper() for word in sensitive_keywords):
        return "*******"
    return valeur


def display_values(inclure_prefix=None, exclure_prefix=None):
    """
    Ajoute aux logs toute les variables d'environnement en filtrant et masquant les valeurs sensibles.
    Param:
        inclure_prefix (str, optionnel): Seule les clés avec ce préfixe seront loggées, si le préfixe est donné.
        exclure_prefix (str, optionnel): Seules les clés sans ce préfixe seront loggées, si le préfixe est donné.
            prefix will be skipped.
    """
    for key, value in dotenv.dotenv_values().items():
        if inclure_prefix and not key.startswith(inclure_prefix):
            continue
        if exclure_prefix and key.startswith(exclure_prefix):
            continue
        logging.info(f"{key}={mask_value(key, value)}")

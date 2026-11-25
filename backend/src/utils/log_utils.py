import logging
import logging.config
import numbers
from functools import wraps
from pathlib import Path

import yaml
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def initialize_logs(nom: str):
    """
    Initialise le logging d'après un fichier de configuration.

    Param:
    ------
    nom: str
        le nom associé aux logs créés
    """

    # Créer le dossier de logs à la racine du projet si ce dernier n'existe pas déjà
    logs_dir = Path(__file__).resolve().parents[2] / "logs"
    logs_dir.mkdir(exist_ok=True)

    config_file = Path(__file__).resolve().parents[2] / "logging_config.yml"

    with open(config_file, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
        logging.config.dictConfig(config)

        logging.info("-" * 50)
        logging.info(f"Lancement {nom}                           ")
        logging.info("-" * 50)


def get_logger(nom_module: str, taille_max: int = 25):
    """
    Renvoie un logger, avec son nom raccourci selon le chemin du module.
    Si le chemin dépasse une certaine taille, on utilise les initiales en guise de préfixe.

    Param:
    ------
    nom_module: str
        le nom du module
    taille_max: int
        la taille maximale du chemin

    Return:
    ------
    logging.Logger
        le logger du module
    """
    if len(nom_module) <= taille_max:
        return logging.getLogger(nom_module)

    parts = nom_module.split(".")
    short_prefix = [p[0] for p in parts[:-1]]
    short_name = ".".join(short_prefix + [parts[-1]])

    return logging.getLogger(short_name)


class LogIndentation:
    """Pour indenter les logs à chaque nouvelle méthode"""

    current_indentation = 0
    indentation_size = 2

    @classmethod
    def increase_indentation(cls):
        """Augmenter l'indentation"""
        cls.current_indentation += 1

    @classmethod
    def decrease_indentation(cls):
        """Diminuer l'indentation"""
        cls.current_indentation -= 1

    @classmethod
    def get_indentation(cls):
        """
        Obtenir l'indentation actuelle.

        Return:
        ------
        str
            les espaces à mettre devant le message
        """
        return " " * cls.indentation_size * cls.current_indentation


def log(func):
    """
    Décorateur pour ajouter les appels et sorties des méthodes aux logs.

    Param:
    ------
    func: Callable
        la méthode à suivre dans les logs

    Return:
    ------
    Callable
        la méthode décorée
    """

    SENSITIVE_KEYWORDS = {
        "password",
        "passwd",
        "pwd",
        "pass",
        "token",
        "secret",
        "key",
        "mdp"
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Appelle la méthode et écrit dans les logs ses paramètres (mots de passe et tokens masqués) et son résultat.

        Param:
        ------
        args: tuple
            les paramètres de la méthode
        kwargs: dict
            les paramètres nommés de la méthode

        Return:
        ------
        Any
            le résultat de la méthode
        """
        if args and hasattr(args[0], "__class__"):
            logger = get_logger(f"{args[0].__class__.__module__}")
        else:
            logger = logging.getLogger(__name__)

        LogIndentation.increase_indentation()
        indentation = LogIndentation.get_indentation()

        # Récupération des paramètres de la méthode
        method_name = func.__name__
        param_names = func.__code__.co_varnames[1 : func.__code__.co_argcount]
        args_list = []

        for i, arg in enumerate(args[1:]):
            if i >= len(param_names):
                break
            param_name = param_names[i].lower()
            if any(keyword in param_name for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(
                    str(arg) if not isinstance(arg, numbers.Number) else arg
                )

        for k, v in kwargs.items():
            if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(str(v) if not isinstance(v, numbers.Number) else v)

        args_tuple = tuple(args_list)

        # Ajout des entrées aux logs
        logger.info(f"{indentation}{method_name}{args_tuple} - START")
        result = func(*args, **kwargs)
        logger.info(f"{indentation}{method_name}{args_tuple} - END")

        # Raccourci les sorties trop longues pour plus de lisibilité
        if isinstance(result, list):
            result_str = str([str(item) for item in result[:3]])
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, dict):
            result_str = [(str(k), str(v)) for k, v in list(result.items())[:3]]
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, str) and len(result) > 50:
            result_str = result[:50] + f" ... ({len(result)} characters)"
        else:
            result_str = str(result)

        logger.info(f"{indentation}  └─> Output: {result_str}")

        LogIndentation.decrease_indentation()

        return result

    return wrapper


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware qui écrit chaque requête HTTP dans les logs."""
    async def dispatch(self, request: Request, call_next):
        """
        Middleware permettant d'enregistrer les requêtes et les réponses HTTP.
        Il enregistre la méthode, le chemin d'accès, le code d'état et les détails de l'erreur.

        Param:
        ------
        request: Request
            la requête reçue
        call_next: Callable
            la fonction qui traite la requête

        Return:
        ------
        Response
            la réponse à la requête

        Raises:
        ------
        Exception
            si le traitement de la requête échoue (l'erreur est écrite dans les logs puis relancée)
        """

        method = request.method
        path = str(request.url.path)

        logging.info(f"{method} {path} - START")

        try:
            response = await call_next(request)
            logging.info(f"{method} {path} - END [Status: {response.status_code}]")
            return response

        except Exception as e:
            logging.error(f"{method} {path} - FAILED [Status: 500] Error: {e!s}")
            raise e

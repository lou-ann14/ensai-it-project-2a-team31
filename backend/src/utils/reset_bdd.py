import os
from pathlib import Path

import dotenv
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log
from src.utils.singleton import Singleton

logger = get_logger(__name__)

class Reset_bdd(metaclass=Singleton):
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent

    @log
    def demarrer(self):
        init_chemin_bdd = self.base_path / "backend" / "data" / "init_bdd.sql"
        test_bdd_chemin = self.base_path/ "backend" / "data" / "test_bdd.sql"
        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]
        create_schema = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        )
        print("1")
        try:
            with open(init_chemin_bdd, encoding="utf-8") as init_fichier_bdd:
                init_bdd_as_string = init_fichier_bdd.read()
            with open(test_bdd_chemin, encoding="utf-8") as test_bdd_fichier:
                test_bdd_as_string = test_bdd_fichier.read()
        except FileNotFoundError as e:
            logger.error( f"Erreur de chemin : impossible de trouver le fichier {e.filename}")
            raise
        print('2')    
        try:    
            with DBConnexion().connexion.cursor() as cursor:
                print('2.5')
                cursor.execute(create_schema)
                print('3')
                cursor.execute(init_bdd_as_string)
                print('4')
                cursor.execute(test_bdd_as_string)
                print('5')
        except Exception as e:
            logger.info(e)
            raise

        return True

if __name__ == "__main__":
    Reset_bdd().demarrer()
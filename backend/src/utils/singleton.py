class Singleton(type):
    """Classe permettant d'utiliser qu'une seule et unique instance.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Renvoie l'instance de la classe, en la créant au premier appel.

        Param:
        ------
        args: tuple
            les paramètres du constructeur
        kwargs: dict
            les paramètres nommés du constructeur

        Return:
        ------
        object
            l'unique instance de la classe
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

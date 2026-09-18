class Ligne :
    def __init__(self,id_ligne:int ,id_gare_depart:int ,id_gare_arrivee:int):
        self.id_ligne=id_ligne
        self.id_gare_depart=id_gare_depart
        self.id_garre_arrivee=id_gare_arrivee

    def __str__(self):
        return f"la gare de depart de la ligne : #{self.id_ligne} est #{self.id_gare_depart} et la gare d'arrivée est : # {self.id_garre_arrivee}"

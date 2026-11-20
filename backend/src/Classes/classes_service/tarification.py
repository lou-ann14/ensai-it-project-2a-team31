"""Calcul des prix et tarification transparente (fonctionnalité F5).

Le prix payé par le client dépend du tarif de base du trajet et de la classe :
- seconde classe : le tarif de base ;
- première classe : le tarif de base multiplié par COEFFICIENT_PREMIERE_CLASSE.

La tarification transparente décompose ce prix TTC en quatre parts, pour que le client
sache ce qu'il paie. Les proportions ci-dessous sont des hypothèses de notre compagnie :
- TVA : 10 % (taux réduit appliqué au transport de voyageurs en France) ;
- péage réseau : 35 % du prix HT (redevances versées à SNCF Réseau pour utiliser les voies) ;
- coût d'exploitation : 50 % du prix HT (personnel, énergie, entretien des trains) ;
- marge de la compagnie : le reste du prix HT (15 %).
"""

COEFFICIENT_PREMIERE_CLASSE = 1.5  # la première classe coûte 1,5 fois le tarif de base
TAUX_TVA = 0.10
PART_PEAGE_RESEAU = 0.35
PART_COUT_EXPLOITATION = 0.50


def prix(tarif_base: float, classe: int) -> float:
    """
    Prix payé par le client pour une place dans la classe donnée.

    Param:
    ------
    tarif_base: float
        le tarif de base du trajet (prix de la seconde classe)
    classe: int
        1 (première) ou 2 (seconde)

    Return:
    ------
    float
        le prix TTC, arrondi au centime
    """
    if classe == 1:
        return round(tarif_base * COEFFICIENT_PREMIERE_CLASSE, 2)
    return round(tarif_base, 2)


def detail_prix(tarif_base: float, classe: int) -> dict:
    """
    Décompose le prix d'une place en TVA, péage réseau, coût d'exploitation et marge.
    Les calculs sont faits en centimes : la somme des parts est toujours exactement
    égale au prix total (la marge absorbe les arrondis).

    Param:
    ------
    tarif_base: float
        le tarif de base du trajet
    classe: int
        1 (première) ou 2 (seconde)

    Return:
    ------
    dict
        {"prix_total", "cout_exploitation", "peage_reseau", "marge", "tva"} en euros
    """
    total = round(prix(tarif_base, classe) * 100)  # en centimes
    tva = round(total - total / (1 + TAUX_TVA))
    hors_taxes = total - tva
    peage = round(hors_taxes * PART_PEAGE_RESEAU)
    exploitation = round(hors_taxes * PART_COUT_EXPLOITATION)
    marge = hors_taxes - peage - exploitation

    return {
        "prix_total": total / 100,
        "cout_exploitation": exploitation / 100,
        "peage_reseau": peage / 100,
        "marge": marge / 100,
        "tva": tva / 100,
    }

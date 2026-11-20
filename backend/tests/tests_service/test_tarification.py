import pytest
from src.Classes.classes_service import tarification

# Tarification transparente (F5) : fonctions pures, aucune base ni API.


@pytest.mark.parametrize(
    "tarif_base, classe, attendu",
    [(20.0, 2, 20.0), (20.0, 1, 30.0), (33.0, 1, 49.5), (12.34, 2, 12.34), (0.0, 1, 0.0)],
)
def test_prix(tarif_base, classe, attendu):
    """2de = tarif de base, 1re = tarif x 1,5 (arrondi au centime)"""
    assert tarification.prix(tarif_base, classe) == attendu


def test_detail_prix_seconde_classe():
    """20 € TTC : TVA 10 % (1,82 €), puis 35 % péage / 50 % exploitation / reste marge sur le HT"""
    detail = tarification.detail_prix(20.0, 2)

    assert detail == {
        "prix_total": 20.0,
        "cout_exploitation": 9.09,
        "peage_reseau": 6.36,
        "marge": 2.73,
        "tva": 1.82,
    }


def test_detail_prix_premiere_classe():
    """En 1re classe, le total vaut 1,5 fois le tarif de base"""
    assert tarification.detail_prix(20.0, 1)["prix_total"] == 30.0


@pytest.mark.parametrize("tarif_base", [0.01, 1.0, 9.99, 20.0, 33.33, 47.5, 99.99, 123.45, 1000.0])
@pytest.mark.parametrize("classe", [1, 2])
def test_detail_prix_somme_exacte(tarif_base, classe):
    """La somme des parts est toujours exactement égale au prix payé (au centime près)"""
    d = tarification.detail_prix(tarif_base, classe)
    somme = round((d["cout_exploitation"] + d["peage_reseau"] + d["marge"] + d["tva"]) * 100)

    assert somme == round(d["prix_total"] * 100)
    assert d["prix_total"] == tarification.prix(tarif_base, classe)
    assert all(valeur >= 0 for valeur in d.values())


def test_detail_prix_gratuit():
    """Tarif de base à 0 : tous les postes valent 0"""
    assert tarification.detail_prix(0.0, 2) == {
        "prix_total": 0.0, "cout_exploitation": 0.0, "peage_reseau": 0.0, "marge": 0.0, "tva": 0.0,
    }

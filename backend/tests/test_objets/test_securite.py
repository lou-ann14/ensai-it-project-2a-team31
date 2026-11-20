from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from src.utils.securite import a_le_grade, verifier_grade

# Hiérarchie des grades : CLIENT < COLLABORATEUR < ADMIN


@pytest.mark.parametrize(
    "grade, minimum, attendu",
    [
        ("CLIENT", "CLIENT", True),
        ("CLIENT", "COLLABORATEUR", False),
        ("CLIENT", "ADMIN", False),
        ("COLLABORATEUR", "CLIENT", True),
        ("COLLABORATEUR", "COLLABORATEUR", True),
        ("COLLABORATEUR", "ADMIN", False),
        ("ADMIN", "CLIENT", True),
        ("ADMIN", "COLLABORATEUR", True),
        ("ADMIN", "ADMIN", True),
        ("INCONNU", "CLIENT", False),
    ],
)
def test_a_le_grade(grade, minimum, attendu):
    assert a_le_grade(MagicMock(grade=grade), minimum) is attendu


def test_verifier_grade_autorise():
    verifier_grade(MagicMock(grade="ADMIN"), "COLLABORATEUR")  # aucune exception


def test_verifier_grade_refuse_en_403():
    with pytest.raises(HTTPException) as erreur:
        verifier_grade(MagicMock(grade="CLIENT"), "COLLABORATEUR")
    assert erreur.value.status_code == 403
    assert "COLLABORATEUR ou supérieur" in erreur.value.detail

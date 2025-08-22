import pytest
from django.core.exceptions import ValidationError

from papers.validators import doi_validator


@pytest.mark.parametrize(
    "doi",
    [
        "10.1000/xyz123",
        "10.1234/ABC-DEF_123",
        "10.12345/paper(2023)",
        "10.123456789/test:123",
    ],
)
def test_valid_dois(doi):
    doi_validator(doi)


@pytest.mark.parametrize(
    "doi",
    [
        "",
        "invalid",
        "11.1000/xyz123",  # Wrong prefix
        "10.123/xyz123",  # Too short publisher ID
        "10.1234567890/xyz123",  # Too long publisher ID
        "10.1234/xyz#123",  # Invalid character
    ],
)
def test_invalid_dois(doi):
    with pytest.raises(ValidationError):
        doi_validator(doi)


def test_case_insensitive():
    doi_validator("10.1000/XYZ123")
    doi_validator("10.1000/xyz123")

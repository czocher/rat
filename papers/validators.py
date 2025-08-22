import re

from django.core.validators import RegexValidator


doi_validator = RegexValidator(
    regex=r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$",
    message="Enter a valid DOI (e.g., 10.1000/xyz123).",
    flags=re.IGNORECASE,
)

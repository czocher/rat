from django import forms

from papers.utils import normalize_doi
from papers.validators import doi_validator


class DOIFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("validators", [doi_validator])
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        return normalize_doi(value)

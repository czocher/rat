from django import forms
from django.utils.translation import gettext_lazy as _

from papers.models import Tag
from papers.utils import travers_inferred


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

    def clean_inferred_tags(self, *args, **kwargs):
        name = self.cleaned_data.get("name")
        inferred_tags = self.cleaned_data.get("inferred_tags")

        if any(tag.name == name for tag in travers_inferred(inferred_tags)):
            raise forms.ValidationError(
                _("Tag inference cycle detected - tag would infer itself.")
            )

        return inferred_tags

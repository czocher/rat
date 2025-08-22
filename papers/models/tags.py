from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import (
    BaseModel,
    ApprovableMixin,
    ApprovableManagerMixin,
    ApprovableQuerysetMixin,
)


class TagCategory(BaseModel, ApprovableMixin):
    name = models.CharField(_("name"), unique=True)

    class Meta:
        verbose_name = _("tag category")
        verbose_name_plural = _("tag categories")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class TagQuerySet(ApprovableQuerysetMixin):
    pass


class TagManager(ApprovableManagerMixin, models.Manager):
    def get_queryset(self) -> TagQuerySet:
        return TagQuerySet(self.model, using=self._db)


class Tag(BaseModel, ApprovableMixin):
    name = models.CharField(_("name"), unique=True)
    category = models.ForeignKey(
        TagCategory,
        verbose_name=_("category"),
        blank=True,
        null=True,
        related_name="tags",
        on_delete=models.CASCADE,
    )
    inferred_tags = models.ManyToManyField(
        "self",
        verbose_name=_("inferred tags"),
        blank=True,
        symmetrical=False,
    )
    description = models.TextField(_("description"), blank=True)
    objects = TagManager()

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class TagAlias(BaseModel):
    name = models.CharField(
        _("name"), unique=True, help_text=_("Must be unique among tags and aliases")
    )
    tag = models.ForeignKey(
        Tag, verbose_name=_("tag"), related_name="aliases", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("tag alias")
        verbose_name_plural = _("tag aliases")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        if self.name == self.tag.name:
            raise ValidationError(
                {"name": _("An alias cannot be the same as the tag it is aliasing.")}
            )
        if exclude is None or "name" not in exclude:
            if Tag.objects.filter(name=self.name).exists():
                raise ValidationError(
                    {"name": _("A tag with this name already exists.")}
                )

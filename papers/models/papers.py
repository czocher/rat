from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import (
    BaseModel,
    ApprovableMixin,
    ApprovableManagerMixin,
    ApprovableQuerysetMixin,
)
from papers.fields import DOIFormField
from papers.models import Tag
from papers.utils import normalize_doi
from papers.validators import doi_validator


class DOIField(models.CharField):
    default_validators = [doi_validator]
    description = "Stores a normalized DOI (e.g., 10.1000/xyz123) and exposes .doi_url"

    def __init__(self, *args, url_prefix="https://doi.org/", **kwargs):
        self.url_prefix = url_prefix
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        raw_value = getattr(model_instance, self.attname)
        normalized = normalize_doi(raw_value)
        setattr(model_instance, self.attname, normalized)
        return normalized

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)

        # Define the property on the model class dynamically
        def doi_url(instance):
            doi = getattr(instance, name)
            return f"{self.url_prefix}{doi}" if doi else None

        setattr(cls, f"{name}_url", property(doi_url))

    def formfield(self, **kwargs):
        defaults = {"form_class": DOIFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class PaperQuerySet(ApprovableQuerysetMixin):
    def with_tags(self, *tags):
        return self.filter(tags__name__in=tags).distinct()


class PaperManager(ApprovableManagerMixin, models.Manager):
    def get_queryset(self) -> PaperQuerySet:
        return PaperQuerySet(self.model, using=self._db)

    def with_tag(self, tags):
        return self.get_queryset().with_tags(tags)


class Paper(BaseModel, ApprovableMixin):
    title = models.CharField(_("title"))
    doi = DOIField(_("DOI"), blank=True, null=True, unique=True)
    abstract = models.TextField(_("abstract"))
    publication_date = models.DateField(_("publication date"))
    authors = models.ManyToManyField("PaperAuthor", verbose_name=_("authors"))
    tags = models.ManyToManyField(Tag, verbose_name=_("tags"), blank=True)

    objects = PaperManager()

    class Meta:
        verbose_name = _("paper")
        verbose_name_plural = _("papers")
        ordering = ["-publication_date"]
        default_related_name = "papers"
        permissions = [("can_approve", _("Can approve paper"))]
        indexes = [
            models.Index(fields=["doi"]),
            models.Index(fields=["publication_date"]),
        ]

    def __str__(self):
        return self.title


class PaperLink(BaseModel):
    url = models.URLField(_("url"))
    paper = models.ForeignKey(
        Paper, verbose_name=_("paper"), related_name="links", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("paper link")
        verbose_name_plural = _("paper links")
        ordering = ["created_at"]

    def __str__(self):
        return self.url


class PaperCitation(BaseModel):
    citation = models.CharField(_("citation"))
    paper = models.ForeignKey(
        Paper,
        verbose_name=_("paper"),
        related_name="citations",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("paper citation")
        verbose_name_plural = _("paper citations")
        ordering = ["created_at"]

    def __str__(self):
        return self.citation


class PaperFileQuerySet(models.QuerySet):
    def sensitive(self):
        return self.filter(sensitive=True)

    def public(self):
        return self.filter(sensitive=False)


class PaperFileManager(models.Manager):
    def get_queryset(self) -> PaperFileQuerySet:
        return PaperFileQuerySet(self.model, using=self._db)

    def sensitive(self):
        return self.get_queryset().sensitive()

    def public(self):
        return self.get_queryset().public()


class PaperFile(BaseModel):
    file = models.FileField(_("file"))
    paper = models.ForeignKey(
        Paper, verbose_name=_("paper"), related_name="files", on_delete=models.CASCADE
    )
    sensitive = models.BooleanField(_("sensitive"), default=True)
    objects = PaperFileManager()

    class Meta:
        verbose_name = _("paper file")
        verbose_name_plural = _("paper files")
        ordering = ["created_at"]
        permissions = [("can_view_sensitive_files", _("Can view sensitive files"))]

    def __str__(self):
        return self.file.name


class PaperAuthor(BaseModel):
    name = models.CharField(_("name"))

    class Meta:
        verbose_name = _("paper author")
        verbose_name_plural = _("paper authors")
        ordering = ["created_at"]

    def __str__(self):
        return self.name

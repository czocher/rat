from dalf.admin import DALFRelatedOnlyField
from django.contrib import admin
from django.utils.safestring import mark_safe

from papers.admin.utils import (
    HandleMetadataMixin,
    HandleMetadataSaveMixin,
    HandleApprovalMixin,
)
from papers.models import (
    Paper,
    PaperAuthor,
    PaperLink,
    PaperFile,
    PaperCitation,
)
from django.utils.translation import gettext_lazy as _


class PaperLinkInline(HandleMetadataSaveMixin, admin.TabularInline):
    model = PaperLink
    extra = 0
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    fieldsets = ((None, {"fields": ("url",)}),)


class PaperCitationInline(HandleMetadataSaveMixin, admin.TabularInline):
    model = PaperCitation
    extra = 0
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    fieldsets = ((None, {"fields": ("citation",)}),)


class PaperFileInline(HandleMetadataSaveMixin, admin.TabularInline):
    model = PaperFile
    extra = 0
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    fieldsets = ((None, {"fields": ("file", "sensitive")}),)


@admin.register(Paper)
class PaperAdmin(HandleMetadataMixin, HandleApprovalMixin):
    list_display = (
        "title",
        "doi_url",
        "publication_date",
        "approval_status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "approval_status",
        ("authors", DALFRelatedOnlyField),
        ("tags", DALFRelatedOnlyField),
        "publication_date",
        "created_at",
        "updated_at",
        ("created_by", DALFRelatedOnlyField),
        ("updated_by", DALFRelatedOnlyField),
    )
    date_hierarchy = "publication_date"
    search_fields = ("doi",)
    autocomplete_fields = ("authors", "tags")
    inlines = (PaperCitationInline, PaperLinkInline, PaperFileInline)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "abstract",
                    "doi",
                    "publication_date",
                    "authors",
                    "tags",
                )
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    @classmethod
    @admin.display(description=_("doi url"))
    def doi_url(cls, paper):
        return mark_safe(f'<a href="{paper.doi_url}">{paper.doi}</a>')


@admin.register(PaperAuthor)
class PaperAuthorAdmin(HandleMetadataMixin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "created_at",
        "updated_at",
        ("created_by", DALFRelatedOnlyField),
        ("updated_by", DALFRelatedOnlyField),
    )
    search_fields = ("name",)
    date_hierarchy = "created_at"

    fieldsets = ((None, {"fields": ("name",)}),)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

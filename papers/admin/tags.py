from dalf.admin import DALFRelatedOnlyField
from django.contrib import admin

from papers.admin.utils import (
    HandleMetadataMixin,
    HandleMetadataSaveMixin,
    HandleApprovalMixin,
)
from papers.forms import TagForm
from papers.models import (
    TagCategory,
    Tag,
    TagAlias,
)


@admin.register(TagCategory)
class TagCategoryAdmin(HandleMetadataMixin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_filter = ("created_at", "updated_at", "created_by", "updated_by")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    fieldsets = ((None, {"fields": ("name",)}),)
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )


class TagAliasAdminInline(HandleMetadataSaveMixin, admin.TabularInline):
    model = TagAlias
    extra = 0
    autocomplete_fields = ("tag",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    fieldsets = ((None, {"fields": ("name",)}),)


@admin.register(Tag)
class TagAdmin(HandleMetadataMixin, HandleApprovalMixin):
    form = TagForm
    list_display = (
        "name",
        "category",
        "approval_status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "approval_status",
        "category",
        ("inferred_tags", DALFRelatedOnlyField),
        "created_at",
        "updated_at",
        ("created_by", DALFRelatedOnlyField),
        ("updated_by", DALFRelatedOnlyField),
    )
    inlines = (TagAliasAdminInline,)
    autocomplete_fields = ("inferred_tags",)
    search_fields = ("name",)
    date_hierarchy = "created_at"
    fieldsets = ((None, {"fields": ("name", "category", "inferred_tags")}),)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

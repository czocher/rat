from dalf.admin import DALFModelAdmin
from django.contrib import admin

from django.utils.translation import gettext_lazy as _

class HandleApprovalMixin(DALFModelAdmin):
    @admin.action(description=_("Approve selected entries"))
    def approve_action(self, request, queryset):
        queryset.approve_by(request.user)

    @admin.action(description=_("Reject selected entries"))
    def reject_action(self, request, queryset):
        queryset.reject()

    def save_model(self, request, obj, form, change):
        if obj.status == obj.APPROVED:
            obj.approver = request.user
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + (
            (
                _("Approval"),
                {
                    "classes": ("collapse",),
                    "fields": ("status", "approver"),
                },
            ),
        )


class HandleMetadataSaveMixin:
    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class HandleMetadataMixin(HandleMetadataSaveMixin, DALFModelAdmin):
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + (
            (
                _("Metadata"),
                {
                    "classes": ("collapse",),
                    "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                },
            ),
        )

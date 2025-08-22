from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PapersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "papers"
    verbose_name = _("papers")

    def ready(self):
        import papers.signals  # noqa

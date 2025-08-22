from django.utils import timezone
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    favourite_papers = models.ManyToManyField(
        "papers.Paper",
        verbose_name=_("favourite papers"),
        blank=True,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class BaseModel(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("updated by"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True


class ApprovableQuerysetMixin(models.QuerySet):
    def approved(self):
        return self.filter(status=ApprovableMixin.APPROVED)

    def pending(self):
        return self.filter(status=ApprovableMixin.PENDING)

    def approve_by(self, user):
        return self.update(status=ApprovableMixin.APPROVED, approver=user)

    def reject(self):
        return self.delete()


class ApprovableManagerMixin:
    def approved(self):
        return self.approved()

    def pending(self):
        return self.pending()


class ApprovableMixin(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    STATUS_CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
    )
    approval_status = models.CharField(
        _("approval status"),
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("approver"),
        related_name="approved_%(class)s",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("The user who approved this entry."),
    )

    class Meta:
        abstract = True

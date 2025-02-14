from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Letter(BaseModel):
    text = models.TextField(_("Text"))
    is_used = models.BooleanField(_("Is used"), default=False)

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")

    def __str__(self):
        return self.text[:50]


class TelegramUser(BaseModel):
    chat_id = models.CharField(_("Chat ID"), max_length=255, unique=True)
    username = models.CharField(_("Username"), max_length=255, null=True, blank=True)
    first_name = models.CharField(
        _("First Name"), max_length=255, null=True, blank=True
    )
    is_active = models.BooleanField(_("Is Active"), default=True)
    letter_command_count = models.PositiveIntegerField(
        _("Letter Command Count"), default=0
    )

    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")

    def __str__(self):
        return f"{self.username or self.chat_id}"


class LetterHistory(BaseModel):
    telegram_user = models.ForeignKey(
        "TelegramUser",
        on_delete=models.CASCADE,
        related_name="letter_history",
        verbose_name=_("Telegram User"),
    )
    letter = models.TextField(_("Letter"))

    class Meta:
        verbose_name = _("Letter History")
        verbose_name_plural = _("Letter Histories")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.telegram_user} - {self.letter[:50]}"

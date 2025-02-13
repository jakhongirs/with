from django.contrib import admin

from apps.bot.models import Letter, TelegramUser


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("text", "is_used", "created_at")
    list_filter = ("is_used",)
    search_fields = ("text",)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "chat_id",
        "username",
        "first_name",
        "is_active",
        "letter_command_count",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("chat_id", "username", "first_name")

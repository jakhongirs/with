from django.contrib import admin

from apps.bot.models import Letter, LetterHistory, TelegramUser


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


@admin.register(LetterHistory)
class LetterHistoryAdmin(admin.ModelAdmin):
    list_display = ("telegram_user", "letter", "created_at")
    list_filter = ("telegram_user", "created_at")
    search_fields = ("telegram_user__username", "telegram_user__chat_id", "letter")

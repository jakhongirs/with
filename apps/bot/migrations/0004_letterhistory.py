# Generated by Django 5.1.4 on 2025-02-14 10:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0003_telegramuser_letter_command_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="LetterHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("letter", models.TextField(verbose_name="Letter")),
                (
                    "telegram_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="letter_history",
                        to="bot.telegramuser",
                        verbose_name="Telegram User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Letter History",
                "verbose_name_plural": "Letter Histories",
                "ordering": ["-created_at"],
            },
        ),
    ]

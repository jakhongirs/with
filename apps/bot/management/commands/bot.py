import datetime
import logging
import os

import openai
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater

from apps.bot.models import Letter, LetterHistory, TelegramUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Starts the Telegram bot"
    HISTORY_SIZE = 50

    def __init__(self):
        super().__init__()
        self.updater = None
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_letter_history(self, chat_id):
        user = TelegramUser.objects.get(chat_id=chat_id)
        return [
            history.letter for history in user.letter_history.all()[: self.HISTORY_SIZE]
        ]

    def add_to_history(self, chat_id, letter):
        user = TelegramUser.objects.get(chat_id=chat_id)
        LetterHistory.objects.create(telegram_user=user, letter=letter.lower())
        # Keep only last HISTORY_SIZE letters
        old_records = user.letter_history.all()[self.HISTORY_SIZE :]
        if old_records:
            user.letter_history.filter(id__in=[r.id for r in old_records]).delete()

    def get_example_letters(self):
        example_letters = Letter.objects.order_by("?")[:5]
        if not example_letters:
            example_letters = Letter.objects.all().order_by("?")[:5]
        return [letter.text.lower() for letter in example_letters]

    def generate_ai_letter(self, chat_id=None):
        history = self.get_letter_history(chat_id) if chat_id else []
        example_letters = self.get_example_letters()

        examples_prompt = (
            "Here are some example love messages to understand my style. Create a new message with completely "
            "different meaning, emotion, and perspective:\n"
        )
        # Add random examples from database
        for i, letter in enumerate(example_letters, 1):
            examples_prompt += f"{i}. {letter}\n"

        examples_prompt += (
            "\nCreate a message that expresses a NEW feeling or perspective not covered above. "
            "Keep it short, sweet, and genuine. Never use similar words or themes from examples"
        )

        history_prompt = "\nDo not repeat these recent messages:\n"
        history_prompt += (
            "\n".join([f"- {letter}" for letter in history[-5:]]) if history else ""
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are me, writing very short love messages to my beloved. "
                        "Keep messages between 1-4 sentences max. "
                        "Make it personal and sweet, like sending a quick loving thought. "
                        "Never use words from example messages. "
                        "Make each message about a different aspect of love. "
                        "Write naturally like a human, not AI. "
                        "Do not use complex words or poetic language. "
                        "Never end messages with a dot or period. "
                        "Occasionally (20% of the time) use relevant emojis "
                        "where it feels natural, but don't force it. "
                        "Never place emojis at the start of the message.",
                    },
                    {
                        "role": "user",
                        "content": f"{examples_prompt}\n{history_prompt}\n\nWrite a new short love message following my style:",
                    },
                ],
                max_tokens=60,
                temperature=0.9,
                presence_penalty=0.8,
                frequency_penalty=0.9,
            )
            letter = response.choices[0].message.content.strip().lower()

            if chat_id:
                self.add_to_history(chat_id, letter)

            return letter
        except Exception as e:
            logger.error(f"Error generating AI letter: {e}")
            return "i love you more than words can express"

    def send_daily_letter(self, context: CallbackContext):
        users = TelegramUser.objects.filter(is_active=True)
        if not users.exists():
            logger.warning("No active users found")
            return

        letter = Letter.objects.filter(is_used=False).first()
        if letter:
            text = letter.text.lower()
            letter.is_used = True
            letter.save()
        else:
            # Show typing for AI generation
            for user in users:
                context.bot.send_chat_action(chat_id=user.chat_id, action="typing")
            text = self.generate_ai_letter()

        for user in users:
            try:
                context.bot.send_message(chat_id=user.chat_id, text=text)
            except Exception as e:
                logger.error(f"Failed to send letter to {user.chat_id}: {e}")
                user.is_active = False
                user.save()

    def command_letter(self, update: Update, context: CallbackContext):
        chat_id = str(update.effective_chat.id)

        # Update user's command count
        user = TelegramUser.objects.get(chat_id=chat_id)
        user.letter_command_count += 1
        user.save()

        # Show typing while generating
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
        ai_letter = self.generate_ai_letter(chat_id)
        update.message.reply_text(ai_letter)

    def start(self, update: Update, context: CallbackContext):
        chat_id = str(update.effective_chat.id)
        user = update.effective_user

        TelegramUser.objects.get_or_create(
            chat_id=chat_id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "is_active": True,
            },
        )

        update.message.reply_text(
            "hello my love! 💌\n\n"
            "i'll send you my personal letters daily and whenever you want!\n\n"
            "just use /letter to get a special letter from me ♥️"
        )

    def handle(self, *args, **options):
        self.updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
        dp = self.updater.dispatcher

        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("letter", self.command_letter))

        job_queue = self.updater.job_queue
        job_queue.run_daily(
            self.send_daily_letter,
            time=datetime.time(hour=3, minute=0),  # 3:00 UTC = 8:00 Tashkent time
            days=(0, 1, 2, 3, 4, 5, 6),
            context=None,
            name="daily_letter",
        )

        self.updater.start_polling()
        self.stdout.write("bot started")
        self.updater.idle()

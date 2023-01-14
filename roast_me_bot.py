import os
from dotenv import load_dotenv
import logging
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # user = update.effective_user
    await update.message.reply_html(
        rf"Welcome to RoastMeBot, send any photo to receive roasts!🔥😈🔥",
        # reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send any photo to receive roasts! 🔥😈🔥")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text("Photo received")
    file_id = update.message.photo[-1].file_id
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive()
    await update.message.reply_text("Photo downloaded")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    load_dotenv()
    application = Application.builder().token(os.environ.get("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application1.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
    pass

# modified from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py

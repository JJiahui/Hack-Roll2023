import random
import os, requests
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

COMPLIMENT = "COMPLIMENT"
ROAST = "ROAST"
REQUEST_TYPE = "REQUEST_TYPE"
compliment_emojis = list("🤗👍✌😎🎉👏💪😄😊🤩😌🥰😘😍")
roast_emojis = list("🤦‍♂️🤦‍♀️😈💀🐵🤏👎🐒�😑�🔥🤡🤥🤓")


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # user = update.effective_user
    await update.message.reply_html(
        rf"Welcome to RoastMeBot! If you want to get roasted 🔥 or complimented 🤗, you've come to the right place!",
        # reply_markup=ForceReply(selective=True),
    )


# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /help is issued."""
#     await update.message.reply_text("Send any photo to get roasted! 🔥😈🔥")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if REQUEST_TYPE not in context.user_data or context.user_data[REQUEST_TYPE] == None:
        return
    request_type = context.user_data[REQUEST_TYPE]
    context.user_data[REQUEST_TYPE] = None

    await update.message.reply_text("Photo received, generating compliment... " + random.choice(compliment_emojis) if request_type == COMPLIMENT else "Photo received, generating roast... " + random.choice(roast_emojis))
    file_id = update.message.photo[-1].file_id
    photo = await context.bot.get_file(file_id)
    # await photo.download_to_drive()
    # await update.message.reply_text("Photo downloaded")
    prompt = await get_prompt(photo)
    roast = await get_roast(prompt, request_type)
    await update.message.reply_text(roast)

async def get_prompt(photo):
    return "a person with red hair holding a piece of paper, 1 7 - year - old anime goth girl, 1 7 - year - old goth girl, 1 8 yo, emo, female emo art student, 2 0 yo, 20yo, 1 9 year old, emo anime girl, please do your best, tall female emo art student, hyper - goth"

async def get_roast(prompt: str, request_type: str):
    headers = {'Content-Type': "application/json", "Authorization": "Bearer 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"}
    prompt = f"Make a compliment using this prompt: {prompt}" if request_type == COMPLIMENT else f"Make the worst insult using this prompt: {prompt}"
    logger.info(prompt)
    payload = {"model": "text-davinci-003", "prompt": prompt, "temperature": 0.7, "max_tokens": 4000}
    response = requests.post('https://api.openai.com/v1/completions', headers = headers, json=payload)
    logger.info(response.json())
    text = response.json()['choices'][0]['text'].split("\n\n")[1]
    if text.startswith('"') and text.endswith('"'):
        text = text[1: -1]
    return text

async def handle_roast_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[REQUEST_TYPE] = ROAST
    await update.message.reply_text("Please send a photo!")

async def handle_compliment_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[REQUEST_TYPE] = COMPLIMENT
    await update.message.reply_text("Please send a photo!")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    load_dotenv()
    application = Application.builder().token(os.environ.get("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("roast_me", handle_roast_me))
    application.add_handler(CommandHandler("compliment_me", handle_compliment_me))

    # on non command i.e message - echo the message on Telegram
    # application1.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
    pass

# modified from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py

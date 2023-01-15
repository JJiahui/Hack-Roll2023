import os, requests, random, asyncio
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
from telegram import ForceReply, Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import replicate
from PIL import Image

model = replicate.models.get("pharmapsychotic/clip-interrogator")
version = model.versions.get("a4a8bafd6089e1716b06057c42b19378250d008b80fe87caa5cd36d40c1eda90")

async def img2Txt(image_path):
    f = open(image_path, 'rb')
    #model = replicate.models.get("methexis-inc/img2prompt")
    #version = model.versions.get("50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5")
    output = version.predict(image=f)
    return output

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

COMPLIMENT = "COMPLIMENT"
ROAST = "ROAST"
REQUEST_TYPE = "REQUEST_TYPE"
compliment_emojis = list("🤗👍✌😎🎉👏💪😄😊🤩😌🥰😘😍")
roast_emojis = list("🤦‍♂️🤦‍♀️😈💀🐵🤏👎🐒😑🔥🤡🤥🤓")


# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html(
        rf"Welcome to RoastMeBot! If you want to get roasted 🔥 or complimented 🤗, you've come to the right place!",
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if REQUEST_TYPE not in context.user_data or context.user_data[REQUEST_TYPE] == None:
        return
    request_type = context.user_data[REQUEST_TYPE]
    context.user_data[REQUEST_TYPE] = None

    await update.message.reply_text("Photo received, generating compliment... " + random.choice(compliment_emojis) if request_type == COMPLIMENT else "Photo received, generating roast... " + random.choice(roast_emojis))
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=constants.ChatAction.TYPING)
    file_id = update.message.photo[-1].file_id
    photo = await context.bot.get_file(file_id)
    photo_path = await photo.download_to_drive()
    prompt = await get_prompt(photo_path)
    roast = await get_roast(prompt, request_type)
    await update.message.reply_text(roast)

async def get_prompt(photo_path):
    return await img2Txt(photo_path)
   
async def get_roast(prompt: str, request_type: str):
    headers = {'Content-Type': "application/json", "Authorization": f"Bearer {OPENAI_KEY}"}
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

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data != None and REQUEST_TYPE in context.user_data:
        context.user_data[REQUEST_TYPE] = None
    await update.message.reply_text("An error has occurred, please try again!")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    load_dotenv()
    global OPENAI_KEY
    OPENAI_KEY = os.environ.get("OPENAI_KEY")

    application = Application.builder().token(os.environ.get("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roast_me", handle_roast_me))
    application.add_handler(CommandHandler("compliment_me", handle_compliment_me))

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.add_error_handler(handle_error)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
    pass

# modified from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py

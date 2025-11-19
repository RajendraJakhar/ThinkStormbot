import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import requests
import wikipedia
import PyPDF2
from io import BytesIO
from PIL import Image

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key="AIzaSyCe7Ye01anyGrncsNIvBv36qBawLS-hn-w")

# AI Chat Model (FAST + powerful)
text_model = genai.GenerativeModel("models/gemini-2.5-flash")

# Image / Anime Model (ULTRA HD)
image_model = genai.GenerativeModel("models/imagen-4.0-generate")

# ---------------- START MESSAGE ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Welcome to *ThinkStorm Bot* ⚡\n"
        "Your All-In-One AI Assistant — Powered by Rajendra Jakhar 🤖✨\n\n"
        "🧠 /ai <msg> — AI Chat\n"
        "🎨 /img <prompt> — Normal Image\n"
        "🌸 /anime <prompt> — Anime Image\n"
        "📚 /wiki <topic> — Wikipedia\n"
        "🎬 /yt <keywords> — YouTube Search\n"
        "📄 Reply PDF  /pdf — PDF Reader\n"
        "🎭 Reply Photo /sticker — Sticker Maker\n"
        "⛅ /weather <city> — Weather\n"
    )


# ---------------- AI CHAT ----------------
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = " ".join(context.args)

    if not user_msg:
        await update.message.reply_text("Use: /ai your question")
        return

    response = text_model.generate_content(user_msg)
    await update.message.reply_text(response.text)


# ---------------- IMAGE GENERATOR ----------------
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("Use: /img cute dog in rain")
        return

    result = image_model.generate_content([prompt])

    for item in result.parts:
        if hasattr(item, "inline_data"):
            await update.message.reply_photo(item.inline_data.data)


# ---------------- ANIME IMAGE ----------------
async def anime_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("Use: /anime boy studying in rain")
        return

    anime_prompt = f"anime style, vibrant detailed artwork: {prompt}"

    result = image_model.generate_content([anime_prompt])

    for item in result.parts:
        if hasattr(item, "inline_data"):
            await update.message.reply_photo(item.inline_data.data)


# ---------------- WIKIPEDIA ----------------
async def wiki_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Use: /wiki India")
        return

    try:
        summary = wikipedia.summary(query, sentences=3)
        await update.message.reply_text(summary)
    except:
        await update.message.reply_text("Wikipedia me kuch nahi mila.")


# ---------------- YOUTUBE SEARCH (LEGAL) ----------------
async def yt_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Use: /yt motivation")
        return

    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    await update.message.reply_text(f"🔍 YouTube search result:\n{url}\n\n"
                                    "⚠️ Download sirf YouTube App / Premium se legal hai.")


# ---------------- WEATHER ----------------
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args)
    if not city:
        await update.message.reply_text("Use: /weather Mumbai")
        return

    res = requests.get(f"https://wttr.in/{city}?format=3")
    await update.message.reply_text(res.text)


# ---------------- PDF READER ----------------
async def read_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply a PDF file → then use /pdf")
        return

    doc = update.message.reply_to_message.document
    if doc.mime_type != "application/pdf":
        await update.message.reply_text("Ye PDF file nahi hai.")
        return

    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()

    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    text = ""

    pages = min(3, len(reader.pages))

    for i in range(pages):
        page = reader.pages[i]
        text += f"--- Page {i+1} ---\n{page.extract_text()}\n\n"

    await update.message.reply_text(text[:4000])


# ---------------- STICKER MAKER ----------------
async def make_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a photo → then use /sticker")
        return

    msg = update.message.reply_to_message

    if msg.photo:
        file = await msg.photo[-1].get_file()
    else:
        await update.message.reply_text("Sticker sirf image se banega.")
        return

    img_bytes = await file.download_as_bytearray()
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    img.thumbnail((512, 512))

    output = BytesIO()
    img.save(output, format="WEBP")
    output.seek(0)

    await update.message.reply_sticker(output)


# ---------------- BOT RUNNER ----------------
app = ApplicationBuilder().token("8567922471:AAH5KMbjHPhkBQhlw2XJ6kT8lfBPMUWBpIs").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ai", ai_chat))
app.add_handler(CommandHandler("img", generate_image))
app.add_handler(CommandHandler("anime", anime_image))
app.add_handler(CommandHandler("wiki", wiki_search))
app.add_handler(CommandHandler("yt", yt_search))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("pdf", read_pdf))
app.add_handler(CommandHandler("sticker", make_sticker))

# Make normal chats respond as AI
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

app.run_polling()

import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask App Setup for Vercel
app = Flask(name)

# Configuration from Environment Variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
VERCEL_URL = os.environ.get('VERCEL_URL')

# Basic Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# --- BOT LOGIC ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    logger.info("Received /start command")
    await update.message.reply_text("Welcome.")

# --- BOT SETUP ---
async def setup_bot():
    """Initializes the bot application and sets up the start handler."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    return application

# --- FLASK ROUTES (FOR VERCEL) ---
@app.route('/api', methods=['POST'])
async def webhook():
    """This endpoint receives updates from Telegram."""
    try:
        application = await setup_bot()
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        async with application:
            await application.process_update(update)
        logger.info("Webhook processed successfully.")
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """This endpoint is called once to set the webhook with Telegram."""
    if not VERCEL_URL:
        return "Error: VERCEL_URL environment variable is not set.", 500
    
    application = await setup_bot()
    webhook_url = f"https://{VERCEL_URL}/api"
    
    success = await application.bot.set_webhook(url=webhook_url)
    
    if success:
        logger.info(f"Webhook set to {webhook_url}")
        return f"Webhook set successfully to {webhook_url}", 200
    else:
        logger.error("Webhook setup failed.")
        return "Webhook setup failed.", 500

@app.route('/')
def health_check():
    """A simple endpoint to check if the app is running."""
    return "Simple bot is running.", 200

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from DataBase import DatabaseManager  # Import the DatabaseManager class
from config import TOKEN
from handlers import start, help_command, button, text_message_handler

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an instance of the DatabaseManager
db_manager = DatabaseManager()

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT, text_message_handler))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Exception occurred: {e}")
        db_manager.close_db()  # Use the close_db method from the db_manager instance



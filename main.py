from src.sales_bot import SalesBot
from src.sales_http import SalesHTTP
from src.sales_database import SalesDatabase
from dotenv import load_dotenv
from telegram.ext import Updater
import os
import signal
import threading

# Load environment variables from .env file
load_dotenv()

# Create instances of classes
sales_bot = SalesBot(bot_token=os.getenv('TELEGRAM_BOT_TOKEN'))
sales_database = SalesDatabase(server=os.getenv('DB_SERVER'), database=os.getenv('DB_NAME'),
                               username=os.getenv('DB_USERNAME'), password=os.getenv('DB_PASSWORD'))
server_name = os.getenv('HTTP_SERVER_NAME')
sales_http = SalesHTTP(('127.0.0.1', 5000), sales_database)

# Define routes for HTTP service
sales_http.add_route('/sales', sales_database.add_sale_record)
sales_http.add_route('/sales_report', sales_database.get_sales_data)

if __name__ == '__main__':

    # Register signal handler in main thread
    signal.signal(signal.SIGTERM, lambda *args: sales_http.stop())

    # Start Telegram bot
    updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'), use_context=True)
    dp = updater.dispatcher
    print("Adding conversation handler")
    dp.add_handler(sales_bot.conversation_handler)



    # Start HTTP service in a separate thread
    http_thread = threading.Thread(target=sales_http.start)
    http_thread.start()

    # Start polling for updates from Telegram
    updater.start_polling()

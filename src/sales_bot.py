import json
import os

import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, ConversationHandler
import requests
import csv

load_dotenv()

class SalesBot:
    ADD_SALE, GET_SALES_DATA, MAIN_MENU = range(3)

    def __init__(self, bot_token):
        # initialize the bot with the provided token
        self.bot_token = bot_token
        self.bot = telegram.Bot(token=self.bot_token)
        self.updater = Updater(token=self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.MAIN_MENU: [MessageHandler(Filters.text, self.main_menu)],
                self.ADD_SALE: [MessageHandler(Filters.text, self.enter_sales_details)],
                self.GET_SALES_DATA: [MessageHandler(Filters.text, self.get_sales_data)]
            },
            fallbacks=[]
        )
        self.add_handlers()

    def start(self, update, context):
        # send a welcome message to the user and display the main menu
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Привет! Добро пожаловать в 'Sales Bot'. \n")
        text = "Пожалуйста, выберите опцию :"
        keyboard = [['Введите данные о продаже'], ['Получить отчет о продажах за период']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
        return self.MAIN_MENU

    def main_menu(self, update, context):
        user_input = update.message.text
        if user_input == 'Введите данные о продаже':
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Пожалуйста, введите детали продажи в следующем формате:\n<id_article>,<date>,<country_name>,<sold_units>")
            return self.ADD_SALE
        elif user_input == 'Получить отчет о продажах за период':
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Введите даты начала и окончания периода, за который вы хотите просмотреть данные о продажах (YYYY-MM-DD,YYYY-MM-DD):")
            return self.GET_SALES_DATA
        else:
            text = "Неверный Ввод. Пожалуйста, выберите опцию :"
            keyboard = [['Введите данные о продаже'], ['Получить отчет о продажах за период']]
            reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
            return self.MAIN_MENU

    def add_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

    def enter_sales_details(self, update, context):
        try:
            # extract sale record details from message text
            message_text = update.message.text
            id_article, date, country_name, sold_units = message_text.split(',')

            # create sale record as a dictionary
            sale_record = {
                'id_article': id_article,
                'date': date,
                'country_name': country_name,
                'sold_units': int(sold_units)
            }

            # send sale record to HTTP service
            headers = {'Content-type': 'application/json'}
            data = json.dumps(sale_record)
            r = requests.post('http://127.0.0.1:5000/sales', headers=headers, data=data)
            response = r.text
            context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат! Пожалуйста, попробуйте еще раз.")
        return self.MAIN_MENU

    def get_sales_data(self, update, context):
        try:
            # send date range to HTTP service
            data = {'date_range': update.message.text}
            r = requests.post('http://127.0.0.1:5000/sales_report', data=data)
            sales = r.json()['sales']['sales']

            # create a CSV file
            file_name = 'sales_report.csv'
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['id_sales', 'id_article', 'date', 'country', 'units'])
                writer.writerows(sales)

            # send the CSV file to the user
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_name, 'rb'))
            os.remove(file_name)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат! Пожалуйста, попробуйте еще раз.")
            return self.MAIN_MENU

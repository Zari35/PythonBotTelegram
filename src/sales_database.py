import os
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SalesDatabase:
    def __init__(self, driver=os.getenv('DB_DRIVER'), server=os.getenv('DB_SERVER'),
                 database=os.getenv('DB_NAME'), username=os.getenv('DB_USERNAME'),
                 password=os.getenv('DB_PASSWORD')):
        self.driver = driver
        self.server = server
        self.database = database
        self.username = username
        self.password = password

        self.connection = None
        self.cursor = None

        self.connect()

    def connect(self):
        try:
            connection_string = f"DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            print(f'Successfully connected to {self.database}')
        except pyodbc.Error as e:
            print(f'Error connecting to database: {str(e)}')

    def add_sale_record(self, sale_record=None):
        if sale_record is not None:
            id_article = sale_record['id_article']
            date = datetime.strptime(sale_record['date'], '%Y-%m-%d')
            country_name = sale_record['country_name']
            sold_units = sale_record['sold_units']

            try:
                query = "INSERT INTO Sales (id_article, date, country_name, sold_units) VALUES (?, ?, ?, ?)"
                params = (id_article, date, country_name, sold_units)
                self.cursor.execute(query, params)
                self.connection.commit()
                return 'Successfully added sale record'
            except pyodbc.Error as e:
                print(f'Error adding sale record: {str(e)}')
                return 'Error adding sale record'
        else:
            try:
                query = "SELECT id_sales, id_article, date, country_name, sold_units FROM Sales order by id_sales desc "
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                return results
            except pyodbc.Error as e:
                print(f'Error retrieving sale records: {str(e)}')
                return 'Error retrieving sale records'

    def get_sales_data(self, start_date, end_date):
        try:
            query = f"SELECT id_sales, id_article, date, country_name, sold_units FROM Sales WHERE date BETWEEN ? AND ?"
            result = self.cursor.execute(query, start_date, end_date).fetchall()
            return {'sales': [list(row) for row in result]}
        except pyodbc.Error as e:
            print(f'Error getting sales data: {str(e)}')
            return {'error': 'Error getting sales data'}
import os
from datetime import datetime

from flask import Flask, request, send_from_directory, jsonify


class SalesHTTP:
    def __init__(self, server_address, sales_database):
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        self.server_address = server_address
        self.sales_database = sales_database
        #self.server_name = os.getenv('HTTP_SERVER_NAME')
        #self.app.config['SERVER_NAME'] = f"{self.server_address[0]}:{self.server_address[1]}"

        @self.app.errorhandler(404)
        def page_not_found(error):
            return "404 error: page not found", 404

        @self.app.route('/')
        def index():
            return 'Welcome to the Sales Bot!'

        @self.app.route('/sales', methods=['POST'])
        def add_sale():
            print('Received a sale record')
            sale_record = request.get_json()
            self.sales_database.add_sale_record(sale_record=sale_record)
            print(sale_record)
            return 'Sale record added successfully.'

        @self.app.route('/sales', methods=['GET'])
        def sales():
            # Retrieve all sales records from the database
            sales_records = self.sales_database.add_sale_record()

            # Convert the query results to a list of dictionaries
            sales_list = []
            for record in sales_records:
                record_dict = {
                    'id_sale': record[0],
                    'id_article': record[1],
                    'date': record[2].strftime('%Y-%m-%d') if isinstance(record[2], datetime.date.__class__) else record[2],  #datetime.date
                    'country_name': record[3],
                    'sold_units': record[4]
                }
                sales_list.append(record_dict)

            # Return the sales data as JSON
            return jsonify(sales_list)

        @self.app.route('/sales_report', methods=['GET'])
        def get_sales():
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            sales_in_period = self.sales_database.get_sales_data(start_date, end_date)
            return {'sales': sales_in_period}

        @self.app.route('/sales_report', methods=['POST'])
        def p_sales():
            date_range = request.form.get('date_range')
            start_date, end_date = date_range.split(',')
            sales_in_period = self.sales_database.get_sales_data(start_date, end_date)
            return {'sales': sales_in_period}

        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(self.app.root_path, 'static'),
                                       'favicon.ico', mimetype='image/vnd.microsoft.icon')

    def add_route(self, route, view_func, methods=['GET']):
        self.app.add_url_rule(route, view_func=view_func, methods=methods)

    def start(self):
        print("Starting HTTP server...")
        try:
            self.app.run(host=self.server_address[0], port=self.server_address[1], debug=False)
        except Exception as e:
            print(f"Exception occurred while starting HTTP server: {e}")
        else:
            print("HTTP server started!")

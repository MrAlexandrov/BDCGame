import psycopg2
import json

class SQLProvider:
    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = json.load(config_file)

    def get_connection(self):
        return psycopg2.connect(
            dbname=self.config['database'],
            user=self.config['user'],
            password=self.config['password'],
            host=self.config['host'],
            port=self.config['port']
        )

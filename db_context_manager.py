import psycopg2
import json

class DBContextManager:
    def __enter__(self):
        with open('configs/db_config.json') as config_file:
            config = json.load(config_file)
        self.conn = psycopg2.connect(
            dbname=config['database'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

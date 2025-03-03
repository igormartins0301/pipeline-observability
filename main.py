import requests
import os
import logging
from psycopg2 import OperationalError
import psycopg2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class DataHandler:
    def __init__(self):
        self.data = None
        self.connection = None

    def extract_data_from_api(self):
        URL = "https://api.coinbase.com/v2/prices/spot?currency=USD"
        response = requests.get(URL)
        data = response.json()

        return data["data"]

    def connect_to_db(self):
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        
        try:
            self.connection = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            logger.info("Connected to database")
        except OperationalError as e:
            logger.error(f"Error connecting to database: {e}")
            self.connection = None
        

        return self.connection
    

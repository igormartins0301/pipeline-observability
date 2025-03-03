import requests
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import (
    OperationalError,
    TimeoutError,
    IntegrityError,
    InvalidRequestError,
)
from models.raw_model import RawData, Base

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class DataHandler:
    def __init__(self):
        self.data = None
        self.connection = None
        self.session = None

    def extract_data_from_api(self):
        URL = "https://api.coinbase.com/v2/prices/spot?currency=USD"
        response = requests.get(URL)
        data = response.json()

        return data["data"]

    def connect_to_db(self):
        load_dotenv()
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        try:
            engine = create_engine(db_url)
            Base.metadata.create_all(engine)  # Cria todas as tabelas se não existirem

            Session = sessionmaker(bind=engine)
            self.session = Session()

            logger.info("Connected to database successfully")
            return True

        except TimeoutError as e:
            logger.error(f"Connection timed out: {e}")
            return False

        except OperationalError as e:
            logger.error(f"Operational error occurred: {e}")
            return False

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return False

    def insert_data_into_db(self, data):
        if self.session is None:
            self.connect_to_db()

        # Inserir os dados na tabela usando ORM
        raw_data = RawData(
            amount=data["amount"], base=data["base"], currency=data["currency"]
        )
        self.session.add(raw_data)
        self.session.commit()
        logger.info("Data inserted into database")


if __name__ == "__main__":
    data_handler = DataHandler()
    data = data_handler.extract_data_from_api()
    data_handler.insert_data_into_db(data)

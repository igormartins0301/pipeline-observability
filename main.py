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

# OpenTelemetry Imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider


# Tracers
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)

# Metrics
db_connection_failures = meter.create_counter(
    name="db_connection_failures",
    description="Counts database connection failures",
)

api_request_count = meter.create_counter(
    name="api_requests",
    description="Counts API requests to Coinbase",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class DataHandler:
    def __init__(self):
        self.session = None

    def extract_data_from_api(self):
        with tracer.start_as_current_span("API Request - Coinbase"):
            URL = "https://api.coinbase.com/v2/prices/spot?currency=USD"
            response = requests.get(URL)
            api_request_count.add(1)

            if response.status_code != 200:
                logger.error(f"API request failed with status: {response.status_code}")
                return None
            data = response.json()
            logger.info("API data extracted successfully")
            return data["data"]

    def connect_to_db(self):
        load_dotenv()
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        with tracer.start_as_current_span("Database Connection"):
            try:
                engine = create_engine(db_url)
                Base.metadata.create_all(
                    engine
                )  # Cria todas as tabelas se não existirem

                Session = sessionmaker(bind=engine)
                self.session = Session()

                logger.info("Connected to database successfully")
                return True

            except (OperationalError, IntegrityError, InvalidRequestError) as e:
                db_connection_failures.add(1)
                logger.error(f"Database error: {e}")
                return False

            except Exception as e:
                db_connection_failures.add(1)
                logger.error(f"Unexpected error: {e}")
                return False

    def insert_data_into_db(self, data):
        if self.session is None:
            self.connect_to_db()

        with tracer.start_as_current_span("Insert Data"):
            try:
                raw_data = RawData(
                    amount=data["amount"], base=data["base"], currency=data["currency"]
                )
                self.session.add(raw_data)
                self.session.commit()
                logger.info("Data inserted into database")

            except Exception as e:
                logger.error(f"Error inserting data into database: {e}")
                self.session.rollback()

if __name__ == "__main__":
    data_handler = DataHandler()
    data = data_handler.extract_data_from_api()
    if data:
        data_handler.insert_data_into_db(data)

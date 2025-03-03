import requests

URL = "https://api.coinbase.com/v2/prices/spot?currency=USD"

response = requests.get(URL)

print(response.json())

# {'data': {'amount': '88841.325', 'base': 'BTC', 'currency': 'USD'}}

import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

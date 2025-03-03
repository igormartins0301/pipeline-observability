import pytest
from unittest.mock import patch, MagicMock
import requests
import psycopg2
from main import DataHandler


@patch("requests.get")
def test_extract_data_from_api(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {"amount": 5000.0, "base": "USD", "currency": "BTC"}
    }
    mock_get.return_value = mock_response

    data_handler = DataHandler()

    data = data_handler.extract_data_from_api()

    assert data["amount"] == 5000.0
    assert data["currency"] == "BTC"
    assert data["base"] == "USD"
    mock_get.assert_called_once_with(
        "https://api.coinbase.com/v2/prices/spot?currency=USD"
    )


@pytest.fixture
def set_env_vars(monkeypatch):
    monkeypatch.setenv('DB_NAME', 'crypto_db')
    monkeypatch.setenv('DB_USER', 'postgres')
    monkeypatch.setenv('DB_PASSWORD', 'example')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')

@patch('psycopg2.connect')
def test_connect_to_db(mock_connect, set_env_vars):
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    data_handler = DataHandler()
    
    connection = data_handler.connect_to_db()

    mock_connect.assert_called_once_with(
        dbname='crypto_db',
        user='postgres',
        password='example',
        host='localhost',
        port='5432'
    )

    assert connection == mock_connection

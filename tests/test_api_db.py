import pytest
from unittest.mock import MagicMock, patch
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from main import DataHandler
from models.raw_model import RawData

@pytest.fixture
def data_handler():
    """Fixture to create a DataHandler instance."""
    return DataHandler()

@pytest.fixture
def mock_get(monkeypatch):
    """Fixture to mock requests.get."""
    mock_get = MagicMock()
    monkeypatch.setattr("requests.get", mock_get)
    return mock_get

@pytest.fixture
def mock_db_session():
    """Fixture to mock SQLAlchemy session."""
    return UnifiedAlchemyMagicMock()

def test_extract_data_from_api(mock_get, data_handler):
    """Test API extraction method without real API calls."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {"amount": "100.0", "base": "BTC", "currency": "USD"}
    }
    mock_get.return_value = mock_response

    data = data_handler.extract_data_from_api()
    
    assert data["amount"] == "100.0"
    assert data["base"] == "BTC"
    assert data["currency"] == "USD"

@patch.object(DataHandler, "connect_to_db", return_value=True)
def test_insert_data_into_db(mock_connect, data_handler, mock_db_session):
    """Test inserting data into DB without real database."""
    mock_data = {"amount": "100.0", "base": "BTC", "currency": "USD"}

    data_handler.session = mock_db_session  

    data_handler.insert_data_into_db(mock_data)

    assert mock_db_session.query(RawData).count() == 1

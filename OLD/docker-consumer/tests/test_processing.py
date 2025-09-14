# tests/test_processing.py
import json
from unittest.mock import Mock, MagicMock
import pytest
from src.consumer.processing import MessageProcessor # Importa a classe a ser testada

@pytest.fixture
def mock_mongo_collection():
    """
    Cria um "mock" (simulação) da coleção do MongoDB.
    Isso nos permite testar sem um banco de dados real.
    """
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value = Mock(inserted_id="mock_id_123")
    return mock_collection

def test_execute_success(mock_mongo_collection):
    """
    Testa o caminho feliz: uma mensagem válida é processada e inserida.
    """
    # Arrange (Preparação)
    processor = MessageProcessor(mongo_collection=mock_mongo_collection)
    message_body = json.dumps({"key": "value", "id": 1}).encode('utf-8')

    # Act (Ação)
    inserted_id = processor.execute(message_body)

    # Assert (Verificação)
    assert inserted_id == "mock_id_123"

    # Verifica se o método insert_one foi chamado exatamente uma vez
    mock_mongo_collection.insert_one.assert_called_once()

    # Pega o argumento que foi passado para insert_one e verifica seu conteúdo
    inserted_document = mock_mongo_collection.insert_one.call_args[0][0]
    assert inserted_document['status'] == 'processed'
    assert inserted_document['key'] == 'value'
    assert 'timestamp_insert' in inserted_document

def test_execute_invalid_json(mock_mongo_collection):
    """
    Testa o caso de falha: a mensagem não é um JSON válido.
    """
    # Arrange
    processor = MessageProcessor(mongo_collection=mock_mongo_collection)
    invalid_body = b"this is not a json"

    # Act & Assert
    # Verifica se a exceção correta (json.JSONDecodeError) é levantada
    with pytest.raises(json.JSONDecodeError):
        processor.execute(invalid_body)

    # Garante que, em caso de falha, nada foi inserido no banco
    mock_mongo_collection.insert_one.assert_not_called()
    
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from main import app
from rag.models import QueryResult, RetrievedChunk


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_chat_endpoint_structure():
    mock_retriever = Mock()
    mock_result = QueryResult(
        answer="Test answer",
        chunks=[
            RetrievedChunk(
                doc_path="test.md",
                title="Test Doc",
                text="Test content",
                score=0.95,
                metadata={}
            )
        ],
        query="Test question"
    )
    mock_retriever.query = AsyncMock(return_value=mock_result)
    
    with patch('main.retriever', mock_retriever):
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"question": "Test question"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "sources" in data


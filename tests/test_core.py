import pytest
from app.core.search import HybridSearch
from unittest.mock import patch, MagicMock

@pytest.fixture
def search():
    return HybridSearch()

def test_get_embedding(search):
    with patch('app.core.search.OpenAI') as mock_openai:
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        embedding = search._get_embedding("test query")
        assert len(embedding) == 3
        assert embedding == [0.1, 0.2, 0.3]

def test_extract_exact_features(search):
    # Test laptop features
    features = search._extract_exact_features("gaming laptop with good battery", "laptops")
    assert "gaming" in features
    assert "battery" in features
    
    # Test smartphone features
    features = search._extract_exact_features("phone with 5g and great camera", "smartphones")
    assert "5g" in features
    assert "camera" in features

def test_search_with_filters(search):
    with patch('app.core.search.Pinecone') as mock_pinecone:
        mock_index = MagicMock()
        mock_pinecone.return_value.Index.return_value = mock_index
        
        # Mock query response
        mock_match = MagicMock()
        mock_match.id = "test-1"
        mock_match.score = 0.9
        mock_match.metadata = {
            "name": "Test Product",
            "description": "Test Description",
            "features": ["feature1", "feature2"],
            "price": 100.0,
            "category": "laptops"
        }
        mock_index.query.return_value.matches = [mock_match]
        
        results = search.search(
            query="test query",
            category="laptops",
            min_price=50,
            max_price=200,
            top_k=1
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "test-1"
        assert results[0]["score"] == 0.9

def test_recommend_similar(search):
    with patch('app.core.search.Pinecone') as mock_pinecone:
        mock_index = MagicMock()
        mock_pinecone.return_value.Index.return_value = mock_index
        
        # Mock fetch response
        mock_vector = MagicMock()
        mock_vector.values = [0.1, 0.2, 0.3]
        mock_index.fetch.return_value.vectors = {"test-1": mock_vector}
        
        # Mock query response
        mock_match = MagicMock()
        mock_match.id = "test-2"
        mock_match.score = 0.8
        mock_match.metadata = {
            "name": "Similar Product",
            "description": "Similar Description",
            "features": ["feature1", "feature2"],
            "price": 150.0,
            "category": "laptops"
        }
        mock_index.query.return_value.matches = [mock_match]
        
        results = search.recommend_similar(
            product_id="test-1",
            category="laptops",
            top_k=1
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "test-2"
        assert results[0]["score"] == 0.8

def test_error_handling(search):
    with patch('app.core.search.Pinecone') as mock_pinecone:
        mock_index = MagicMock()
        mock_pinecone.return_value.Index.return_value = mock_index
        
        # Test non-existent product
        mock_index.fetch.return_value.vectors = {}
        results = search.recommend_similar("nonexistent-id", "laptops")
        assert len(results) == 0
        
        # Test invalid category
        with pytest.raises(ValueError):
            search.search("test query", category="invalid_category") 
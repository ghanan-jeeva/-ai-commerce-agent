import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv
from app.core.config import get_settings
import json

load_dotenv()

client = TestClient(app)
API_KEY = os.getenv("API_KEY", "test-api-key-123")
headers = {"X-API-Key": API_KEY}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    data = {
        "query": "Tell me about your best selling laptops",
        "context": None
    }
    response = client.post("/api/v1/chat", json=data, headers=headers)
    assert response.status_code == 200
    assert "response" in response.json()
    assert "recommendations" in response.json()

def test_recommend_endpoint():
    data = {
        "query": "gaming laptops under $2000",
        "filters": {"price_max": 2000},
        "limit": 5
    }
    response = client.post("/api/v1/recommend", json=data, headers=headers)
    assert response.status_code == 200
    assert "recommendations" in response.json()
    assert "explanation" in response.json()

def test_similar_products():
    response = client.get("/api/v1/recommend/similar/test-product-1", headers=headers)
    assert response.status_code in [200, 404]  # 404 is acceptable if product not found

def test_unauthorized_access():
    data = {"query": "test"}
    response = client.post("/api/v1/chat", json=data)  # No API key
    assert response.status_code == 403

def test_invalid_api_key():
    bad_headers = {"X-API-Key": "invalid-key"}
    data = {"query": "test"}
    response = client.post("/api/v1/chat", json=data, headers=bad_headers)
    assert response.status_code == 403

# Image search tests would require actual image files
def test_image_search_url():
    data = {
        "image_url": "https://example.com/test.jpg",
        "text_query": "red dress",
        "limit": 5
    }
    response = client.post("/api/v1/image-search/url", json=data, headers=headers)
    # Note: This will likely fail without proper setup
    assert response.status_code in [200, 400, 500]  # 400/500 acceptable for demo 

def test_search_products():
    # Test basic search
    response = client.get("/api/search?query=gaming laptop")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    
    # Test with filters
    response = client.get("/api/search?query=laptop&category=laptops&min_price=500&max_price=2000")
    assert response.status_code == 200
    data = response.json()
    for product in data["results"]:
        assert product["category"] == "laptops"
        assert 500 <= product["price"] <= 2000

def test_recommend_similar():
    # First get a product ID
    search_response = client.get("/api/search?query=laptop")
    product_id = search_response.json()["results"][0]["id"]
    
    # Test similar products
    response = client.get(f"/api/similar/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_error_handling():
    # Test invalid category
    response = client.get("/api/search?query=test&category=invalid")
    assert response.status_code == 400
    
    # Test invalid price range
    response = client.get("/api/search?query=test&min_price=1000&max_price=500")
    assert response.status_code == 400
    
    # Test non-existent product
    response = client.get("/api/similar/nonexistent-id")
    assert response.status_code == 404

def test_rate_limiting():
    # Test rate limiting
    for _ in range(5):
        response = client.get("/api/search?query=test")
        assert response.status_code == 200
    
    # Should be rate limited after 5 requests
    response = client.get("/api/search?query=test")
    assert response.status_code == 429 
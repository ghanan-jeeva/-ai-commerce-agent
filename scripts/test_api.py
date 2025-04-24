import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-Key": API_KEY}

def test_chat():
    """Test the chat endpoint"""
    url = f"{BASE_URL}/api/v1/chat"
    data = {
        "query": "What gaming laptops do you have under $2000?",
        "context": None
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print("\nChat Response:")
    print(json.dumps(response.json(), indent=2))

def test_recommendations():
    """Test the recommendations endpoint"""
    url = f"{BASE_URL}/api/v1/recommend"
    data = {
        "query": "high performance laptops",
        "filters": {"price_max": 2000},
        "limit": 3
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print("\nRecommendations Response:")
    print(json.dumps(response.json(), indent=2))

def test_similar_products():
    """Test the similar products endpoint"""
    url = f"{BASE_URL}/api/v1/recommend/similar/laptop-1"
    
    response = requests.get(url, headers=HEADERS)
    print("\nSimilar Products Response:")
    print(json.dumps(response.json(), indent=2))

def main():
    print("Testing API endpoints...")
    
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"\nHealth Check: {response.json()}")
    
    # Test main endpoints
    test_chat()
    test_recommendations()
    test_similar_products()

if __name__ == "__main__":
    main() 
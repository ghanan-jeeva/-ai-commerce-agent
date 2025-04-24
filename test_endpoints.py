import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-123"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_search():
    """Test the search endpoint"""
    url = f"{BASE_URL}/api/search"
    data = {
        "query": "gaming laptop with good battery life",
        "category": "laptops",
        "min_price": 1000,
        "max_price": 3000,
        "top_k": 3
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print("\nSearch Response:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    return response

def test_similar():
    """Test the similar products endpoint"""
    # First get a product ID through search
    search_response = test_search()
    
    if search_response.status_code == 200 and search_response.json():
        product_id = search_response.json()[0]["id"]
        url = f"{BASE_URL}/api/similar/{product_id}"
        params = {
            "category": "laptops",
            "top_k": 3
        }
        
        response = requests.get(url, params=params, headers=HEADERS)
        print("\nSimilar Products Response:")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("\nHealth Check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_health()
    test_search()
    test_similar() 
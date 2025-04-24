import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_search(query, category=None, min_price=None, max_price=None, top_k=3):
    params = {
        "query": query,
        "top_k": top_k
    }
    if category:
        params["category"] = category
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
        
    response = requests.get(f"{BASE_URL}/api/v1/search", params=params)
    print(f"\nSearch Test for '{query}'")
    print(f"Parameters: category={category}, price range=${min_price or 0}-${max_price or 'any'}")
    print(f"Status: {response.status_code}")
    
    results = response.json()
    if not results:
        print("No results found.")
    else:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            product = result["metadata"]
            print(f"\n{i}. {product['name']} - ${product['price']}")
            print(f"   Score: {result['score']:.2f}")
            print(f"   Description: {product['description']}")
            print(f"   Features: {', '.join(product['features'])}")
    print("\n" + "-"*80)

if __name__ == "__main__":
    test_health()
    
    # Test realistic customer queries
    print("\nTesting realistic customer queries...")
    
    # Laptop queries
    test_search("I need a powerful laptop for gaming with good graphics card")
    test_search("looking for a budget friendly laptop for college students", max_price=1000)
    test_search("business laptop with long battery life and fingerprint reader")
    
    # Smartphone queries
    test_search("best camera phone for photography", category="smartphones")
    test_search("affordable 5G phone with good battery life", category="smartphones", max_price=600)
    test_search("large screen phone with high refresh rate", category="smartphones")
    
    # Tablet queries
    test_search("tablet good for digital art and drawing", category="tablets")
    test_search("lightweight tablet for reading and note taking", category="tablets")
    test_search("premium tablet with keyboard for work", category="tablets", min_price=700)
    
    # Audio queries
    test_search("noise cancelling headphones for travel", category="audio")
    test_search("wireless earbuds for running and workouts", category="audio")
    test_search("premium headphones for audiophiles", category="audio", min_price=300) 
from app.core.search import HybridSearch
import json

def test_search():
    search = HybridSearch()
    
    # Test cases
    test_queries = [
        # Basic functionality tests
        {
            "query": "gaming laptop with good battery life",
            "category": "laptops",
            "description": "Basic semantic + feature matching for laptops"
        },
        {
            "query": "smartphone with great camera and 5g",
            "category": "smartphones",
            "description": "Basic semantic + feature matching for smartphones"
        },
        # Edge cases
        {
            "query": "cheap laptop under 500",
            "category": "laptops",
            "min_price": 0,
            "max_price": 500,
            "description": "Price range filtering"
        },
        {
            "query": "premium smartphone",
            "category": "smartphones",
            "min_price": 1000,
            "description": "Minimum price filtering"
        },
        {
            "query": "tablet",
            "category": "tablets",
            "description": "Very broad query"
        },
        {
            "query": "headphones with very specific features that might not exist",
            "category": "audio",
            "description": "Query with unlikely features"
        },
        {
            "query": "laptop for professional video editing and gaming",
            "category": "laptops",
            "description": "Multiple use cases"
        },
        {
            "query": "smartphone with 8k video and 120hz display",
            "category": "smartphones",
            "description": "Specific technical requirements"
        }
    ]
    
    # Run tests
    for test in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing: {test['description']}")
        print(f"Query: {test['query']}")
        print(f"Category: {test['category']}")
        if 'min_price' in test:
            print(f"Min Price: ${test['min_price']}")
        if 'max_price' in test:
            print(f"Max Price: ${test['max_price']}")
        
        try:
            results = search.search(
                query=test['query'],
                category=test['category'],
                min_price=test.get('min_price'),
                max_price=test.get('max_price'),
                top_k=3
            )
            
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Score: {result['score']:.4f}")
                print(f"Name: {result['metadata']['name']}")
                print(f"Description: {result['metadata']['description']}")
                print(f"Features: {', '.join(result['metadata']['features'])}")
                print(f"Price: ${result['metadata']['price']}")
        except Exception as e:
            print(f"Error during search: {str(e)}")
            continue

def test_similar_products():
    search = HybridSearch()
    
    # Test similar product recommendations
    test_cases = [
        {
            "product_id": "laptop-1",
            "category": "laptops",
            "description": "Similar laptops"
        },
        {
            "product_id": "phone-1",
            "category": "smartphones",
            "description": "Similar smartphones"
        },
        {
            "product_id": "nonexistent-id",
            "category": "laptops",
            "description": "Non-existent product ID"
        }
    ]
    
    print("\nTesting Similar Product Recommendations")
    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {test['description']}")
        print(f"Product ID: {test['product_id']}")
        print(f"Category: {test['category']}")
        
        try:
            results = search.recommend_similar(
                product_id=test['product_id'],
                category=test['category'],
                top_k=3
            )
            
            print(f"\nFound {len(results)} similar products:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Score: {result['score']:.4f}")
                print(f"Name: {result['metadata']['name']}")
                print(f"Description: {result['metadata']['description']}")
                print(f"Features: {', '.join(result['metadata']['features'])}")
                print(f"Price: ${result['metadata']['price']}")
        except Exception as e:
            print(f"Error during similar product search: {str(e)}")
            continue

if __name__ == "__main__":
    print("Running Basic Search Tests")
    test_search()
    
    print("\nRunning Similar Product Tests")
    test_similar_products() 
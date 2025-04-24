import pytest
import time
from app.core.search import HybridSearch
from app.core.config import get_settings

@pytest.fixture
def search():
    return HybridSearch()

def test_search_response_time(search):
    """Test that search response time is within acceptable limits"""
    start_time = time.time()
    results = search.search("gaming laptop", top_k=10)
    end_time = time.time()
    
    # Response time should be under 1 second
    assert end_time - start_time < 1.0
    assert len(results) <= 10

def test_concurrent_searches(search):
    """Test performance with multiple concurrent searches"""
    queries = [
        "gaming laptop",
        "smartphone with good camera",
        "wireless headphones",
        "tablet for drawing"
    ]
    
    start_time = time.time()
    results = []
    for query in queries:
        results.append(search.search(query, top_k=5))
    end_time = time.time()
    
    # All searches should complete within 2 seconds
    assert end_time - start_time < 2.0
    assert all(len(r) <= 5 for r in results)

def test_large_result_set(search):
    """Test performance with large result sets"""
    start_time = time.time()
    results = search.search("laptop", top_k=50)
    end_time = time.time()
    
    # Should handle large result sets efficiently
    assert end_time - start_time < 1.5
    assert len(results) <= 50

def test_filtered_search_performance(search):
    """Test performance of filtered searches"""
    start_time = time.time()
    results = search.search(
        "laptop",
        category="laptops",
        min_price=500,
        max_price=2000,
        top_k=20
    )
    end_time = time.time()
    
    # Filtered searches should be efficient
    assert end_time - start_time < 1.0
    assert len(results) <= 20
    assert all(500 <= r["price"] <= 2000 for r in results)

def test_similar_products_performance(search):
    """Test performance of similar products recommendation"""
    # First get a product ID
    results = search.search("laptop", top_k=1)
    product_id = results[0]["id"]
    
    start_time = time.time()
    similar = search.recommend_similar(product_id, top_k=10)
    end_time = time.time()
    
    # Similar products should be found quickly
    assert end_time - start_time < 1.0
    assert len(similar) <= 10 
import pinecone
import openai
from dotenv import load_dotenv
import os
import json
import pytest

# Load environment variables
load_dotenv()

def test_similar_products():
    """Test finding similar products based on description"""
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "commerce-agent"))
    
    # Initialize OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Test query 1: Find similar laptops
    query_text = "I need a powerful laptop for work with good RAM and storage"
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_vector = response.data[0].embedding
    
    results = index.query(
        vector=query_vector,
        top_k=2,
        include_metadata=True,
        namespace="products",
        filter={"category": {"$eq": "laptops"}}
    )
    
    # Verify we got laptop results
    assert len(results.matches) > 0
    assert all(match.metadata["category"] == "laptops" for match in results.matches)
    print("\nLaptop search results:")
    for match in results.matches:
        print(f"- {match.metadata['name']}: {match.metadata['description']}")
    
    # Test query 2: Find budget phones
    query_text = "Looking for an affordable smartphone with good camera"
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_vector = response.data[0].embedding
    
    results = index.query(
        vector=query_vector,
        top_k=1,
        include_metadata=True,
        namespace="products",
        filter={"category": {"$eq": "phones"}}
    )
    
    # Verify we got phone results
    assert len(results.matches) > 0
    assert results.matches[0].metadata["category"] == "phones"
    assert float(results.matches[0].metadata["price"]) < 500.0  # Should be a budget phone
    print("\nPhone search results:")
    for match in results.matches:
        print(f"- {match.metadata['name']}: {match.metadata['description']}")

def test_feature_based_search():
    """Test finding products based on specific features"""
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "commerce-agent"))
    
    # Search for products with specific features
    query_text = "Find devices with water resistance and long battery life"
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_vector = response.data[0].embedding
    
    results = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        namespace="products"
    )
    
    # Print results for debugging
    print("\nFeature-based search results:")
    for match in results.matches:
        print(f"\nProduct: {match.metadata['name']}")
        print(f"Features: {match.metadata['features']}")
    
    # Verify we got some results
    assert len(results.matches) > 0

def test_price_range_filter():
    """Test filtering products by price range"""
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "commerce-agent"))
    
    # Search for premium products
    query_text = "Show me premium devices with advanced features"
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_vector = response.data[0].embedding
    
    results = index.query(
        vector=query_vector,
        top_k=2,
        include_metadata=True,
        namespace="products",
        filter={"price": {"$gte": 1000.0}}  # Premium products
    )
    
    # Print results for debugging
    print("\nPrice range filter results:")
    for match in results.matches:
        print(f"- {match.metadata['name']}: ${match.metadata['price']}")
    
    # Verify we got premium products
    assert len(results.matches) > 0
    assert all(float(match.metadata["price"]) >= 1000.0 for match in results.matches)

def test_category_filter():
    """Test filtering products by category"""
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "commerce-agent"))
    
    # Search for accessories
    query_text = "Show me tech accessories"
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_vector = response.data[0].embedding
    
    results = index.query(
        vector=query_vector,
        top_k=2,
        include_metadata=True,
        namespace="products",
        filter={"category": {"$eq": "accessories"}}
    )
    
    # Print results for debugging
    print("\nCategory filter results:")
    for match in results.matches:
        print(f"- {match.metadata['name']}: {match.metadata['category']}")
    
    # Verify we got accessories
    assert len(results.matches) > 0
    assert all(match.metadata["category"] == "accessories" for match in results.matches)

if __name__ == "__main__":
    # Run tests
    test_similar_products()
    test_feature_based_search()
    test_price_range_filter()
    test_category_filter()
    print("\nAll tests passed!") 
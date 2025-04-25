# AI Commerce Agent

A hybrid search system for e-commerce products that combines semantic search with exact feature matching, fuzzy matching, and AI-powered product recommendations.

## Features

- **Hybrid Search**: Combines semantic search, exact feature matching, and fuzzy matching
- **AI-Powered Recommendations**: Get similar products based on product features
- **Category Filtering**: Search within specific product categories
- **Price Range Filtering**: Find products within your budget
- **Agent Q&A**: Get personalized product recommendations through natural language
- **Image Search**: Find similar products using image URLs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX_NAME=commerce-agent
API_KEY=your_api_key
```

3. Initialize database and start server:
```bash
python scripts/init_db.py
uvicorn app.main:app --reload
```

## API Endpoints

### Search Products
```http
POST /api/search
{
    "query": "gaming laptop with good battery life",
    "category": "laptops",
    "min_price": 1000,
    "max_price": 3000,
    "top_k": 3
}
```

### Agent Q&A
```http
POST /api/agent/qa
{
    "query": "I need a laptop for gaming and video editing. What would you recommend?",
    "conversation_history": []
}
```

### Image Search
```http
POST /api/search/image
{
    "image_url": "https://example.com/product_image.jpg"
}
```

### Similar Products
```http
GET /api/similar/{product_id}?category=laptops&top_k=3
```

### Health Check
```http
GET /health
```

## Testing

Run unit tests:
```bash
python -m pytest tests/test_api.py -v
```

For API testing, import `postman_collection.json` into Postman. The collection includes examples for:
- Basic product search
- Budget product search
- Premium product search
- Agent Q&A
- Image search
- Similar products search

## Product Categories

The system supports the following product categories:
- Laptops
- Smartphones
- Tablets
- Audio devices

## Note
Uses Pinecone free tier in AWS us-east-1 region. Create your index there first.

## License
MIT 
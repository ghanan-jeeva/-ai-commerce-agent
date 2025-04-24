# AI Commerce Agent

A hybrid search system for e-commerce products that combines semantic search with exact feature matching.

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

### Similar Products
```http
GET /api/similar/{product_id}?category=laptops&top_k=3
```

### Health Check
```http
GET /health
```

## Testing

Run tests:
```bash
python -m pytest tests/test_api.py -v
```

For API testing, import `AI_Commerce_Agent.postman_collection.json` into Postman.

## Note
Uses Pinecone free tier in AWS us-east-1 region. Create your index there first.

## License
MIT 
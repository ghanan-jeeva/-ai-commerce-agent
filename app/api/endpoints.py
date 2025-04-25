from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel, validator
from app.core.search import HybridSearch
from app.core.config import get_settings
import openai
import base64
from PIL import Image
import io

router = APIRouter()
search = HybridSearch()
settings = get_settings()

# Valid product categories
VALID_CATEGORIES = ["laptops", "smartphones", "tablets", "audio"]

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    top_k: Optional[int] = 5

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            v_lower = v.lower()
            if v_lower not in [c.lower() for c in VALID_CATEGORIES]:
                raise ValueError(f"Invalid category: {v}. Valid categories are: {', '.join(VALID_CATEGORIES)}")
            return v_lower
        return v

    @validator('min_price', 'max_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError("max_price must be greater than min_price")
        return v

class AgentRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None

class AgentResponse(BaseModel):
    response: str
    suggested_products: Optional[List[dict]] = None
    follow_up_questions: Optional[List[str]] = None

class ProductResponse(BaseModel):
    id: str
    score: float
    metadata: dict

class ImageSearchRequest(BaseModel):
    image: str  # Base64 encoded image
    category: Optional[str] = None
    top_k: Optional[int] = 3

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            v_lower = v.lower()
            if v_lower not in [c.lower() for c in VALID_CATEGORIES]:
                raise ValueError(f"Invalid category: {v}. Valid categories are: {', '.join(VALID_CATEGORIES)}")
            return v_lower
        return v

@router.post("/agent/qa", response_model=AgentResponse)
async def agent_qa(request: AgentRequest):
    """
    Handle conversational queries about products using GPT
    """
    try:
        # Get relevant products based on the query
        products = search.search(
            query=request.query,
            top_k=5
        )
        
        # Format products for context
        product_context = "\n".join([
            f"Product: {p['metadata']['name']}\n"
            f"Description: {p['metadata']['description']}\n"
            f"Price: ${p['metadata']['price']}\n"
            f"Features: {', '.join(p['metadata']['features'])}\n"
            for p in products
        ])
        
        # Format conversation history
        history = ""
        if request.conversation_history:
            history = "\n".join([
                f"User: {msg['user']}\nAssistant: {msg['assistant']}"
                for msg in request.conversation_history
            ])
        
        # Create system message
        system_message = f"""You are a helpful shopping assistant. Use the following product information to answer questions:
        
        {product_context}
        
        Previous conversation:
        {history}
        
        Guidelines:
        1. Be helpful and friendly
        2. Recommend products when relevant
        3. Ask follow-up questions to better understand user needs
        4. Provide specific details about products
        5. Suggest alternatives if requested products aren't available
        """
        
        # Get response from GPT using new API format
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.query}
            ],
            temperature=0.7
        )
        
        # Extract response and generate follow-up questions
        assistant_response = response.choices[0].message.content
        
        # Generate follow-up questions using new API format
        follow_up = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate 2-3 relevant follow-up questions based on the conversation."},
                {"role": "user", "content": f"User query: {request.query}\nAssistant response: {assistant_response}"}
            ],
            temperature=0.7
        )
        
        follow_up_questions = follow_up.choices[0].message.content.split("\n")
        
        return AgentResponse(
            response=assistant_response,
            suggested_products=products[:3] if products else None,
            follow_up_questions=follow_up_questions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[ProductResponse])
async def search_products(request: SearchRequest):
    """
    Search for products using hybrid search (semantic + exact matching)
    """
    try:
        # Validate category if provided
        if request.category and request.category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {request.category}. Valid categories are: {', '.join(VALID_CATEGORIES)}"
            )

        # Validate price range
        if request.min_price is not None and request.max_price is not None:
            if request.min_price > request.max_price:
                raise HTTPException(
                    status_code=400,
                    detail="min_price cannot be greater than max_price"
                )
            
        results = search.search(
            query=request.query,
            category=request.category,
            min_price=request.min_price,
            max_price=request.max_price,
            top_k=request.top_k or 5
        )
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No products found matching the criteria"
            )
            
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{product_id}", response_model=List[ProductResponse])
async def recommend_similar(
    product_id: str,
    category: Optional[str] = None,
    top_k: int = Query(default=3, ge=1, le=10)
):
    """
    Get similar product recommendations
    """
    try:
        # Validate category if provided
        if category and category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}. Valid categories are: {', '.join(VALID_CATEGORIES)}"
            )
            
        # First check if the product exists
        product = search.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {product_id}"
            )
            
        results = search.recommend_similar(
            product_id=product_id,
            category=category,
            top_k=top_k
        )
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No similar products found for {product_id}"
            )
            
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/image", response_model=List[ProductResponse])
async def image_search(request: ImageSearchRequest):
    """
    Search for products using an image
    """
    try:
        # Handle base64 padding
        padding = len(request.image) % 4
        if padding:
            request.image += '=' * (4 - padding)
            
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image)
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        
        # Get image description using GPT-4 Vision
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this product image in detail, focusing on its features, style, and potential use cases. Be specific about colors, materials, and any distinguishing characteristics."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{request.image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        # Extract image description
        image_description = response.choices[0].message.content
        
        # Use description to search for similar products
        results = search.search(
            query=image_description,
            category=request.category,
            top_k=request.top_k or 3
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
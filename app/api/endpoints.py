from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, validator
from app.core.search import HybridSearch
from app.core.config import get_settings

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

class ProductResponse(BaseModel):
    id: str
    score: float
    metadata: dict

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
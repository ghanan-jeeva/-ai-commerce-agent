from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.ai_service import ai_service
from ..core.security import verify_api_key

router = APIRouter()

class RecommendationRequest(BaseModel):
    query: str
    filters: Optional[Dict] = None
    limit: Optional[int] = 5

class RecommendationResponse(BaseModel):
    recommendations: List[Dict]
    explanation: Optional[str] = None

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    api_key: str = Depends(verify_api_key)
) -> RecommendationResponse:
    """
    Get product recommendations based on text query.
    
    This endpoint uses semantic search to find relevant products
    and returns them with an optional explanation.
    """
    try:
        # Get recommendations
        recommendations = await ai_service.get_product_recommendations(
            query=request.query,
            n=request.limit
        )
        
        # Get explanation for recommendations
        explanation = await ai_service.get_response(
            query=f"Explain why these products are recommended for the query: {request.query}",
            context={"recommendations": recommendations}
        )
        
        return RecommendationResponse(
            recommendations=recommendations,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

@router.get("/similar/{product_id}", response_model=RecommendationResponse)
async def get_similar_products(
    product_id: str,
    limit: int = Query(default=5, le=20),
    api_key: str = Depends(verify_api_key)
) -> RecommendationResponse:
    """
    Get similar products based on a product ID.
    
    This endpoint finds products similar to the given product
    using semantic similarity search.
    """
    try:
        # Get product details first
        product_details = await ai_service.get_product_recommendations(
            query=f"product_id:{product_id}",
            n=1
        )
        
        if not product_details:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )
        
        # Get similar products
        similar_products = await ai_service.get_product_recommendations(
            query=str(product_details[0]),  # Use product details as query
            n=limit
        )
        
        # Filter out the original product
        similar_products = [p for p in similar_products if p.get("id") != product_id]
        
        return RecommendationResponse(
            recommendations=similar_products[:limit],
            explanation=f"Products similar to {product_details[0].get('name', product_id)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting similar products: {str(e)}"
        ) 
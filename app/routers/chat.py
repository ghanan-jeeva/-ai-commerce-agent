from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from ..services.ai_service import ai_service
from ..core.security import verify_api_key

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    recommendations: Optional[List[Dict]] = None

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
) -> ChatResponse:
    """
    Handle chat interactions with the AI agent.
    
    This endpoint processes natural language queries and returns responses
    with optional product recommendations.
    """
    try:
        # Get AI response
        response = await ai_service.get_response(
            query=request.query,
            context=request.context
        )
        
        # Get relevant product recommendations
        recommendations = await ai_service.get_product_recommendations(
            query=request.query,
            n=3  # Limit to top 3 recommendations
        )
        
        return ChatResponse(
            response=response,
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        ) 
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Dict, Optional
from PIL import Image
import io
from ..services.ai_service import ai_service
from ..core.security import verify_api_key

router = APIRouter()

class ImageSearchResponse(BaseModel):
    matches: List[Dict]
    explanation: Optional[str] = None

@router.post("/upload", response_model=ImageSearchResponse)
async def search_by_image(
    image: UploadFile = File(...),
    text_query: Optional[str] = Form(None),
    limit: int = Form(default=5),
    api_key: str = Depends(verify_api_key)
) -> ImageSearchResponse:
    """
    Search for products using an uploaded image.
    
    Optionally combine with text query for hybrid search.
    """
    try:
        # Read and validate image
        contents = await image.read()
        try:
            img = Image.open(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format"
            )
        
        if text_query:
            # Perform hybrid search
            matches = await ai_service.hybrid_search(
                text_query=text_query,
                image=img,
                n=limit
            )
            
            explanation = await ai_service.get_response(
                query=f"Explain why these products match the image and text query: {text_query}",
                context={"matches": matches}
            )
        else:
            # Perform image-only search
            matches = await ai_service.search_by_image(
                image=img,
                n=limit
            )
            
            explanation = await ai_service.get_response(
                query="Explain why these products match the uploaded image",
                context={"matches": matches}
            )
        
        return ImageSearchResponse(
            matches=matches,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image search: {str(e)}"
        )

@router.post("/url", response_model=ImageSearchResponse)
async def search_by_image_url(
    image_url: str,
    text_query: Optional[str] = None,
    limit: int = 5,
    api_key: str = Depends(verify_api_key)
) -> ImageSearchResponse:
    """
    Search for products using an image URL.
    
    Optionally combine with text query for hybrid search.
    """
    try:
        # Download and validate image
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to fetch image from URL"
                )
            
            try:
                img = Image.open(io.BytesIO(response.content))
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image format"
                )
        
        if text_query:
            # Perform hybrid search
            matches = await ai_service.hybrid_search(
                text_query=text_query,
                image=img,
                n=limit
            )
            
            explanation = await ai_service.get_response(
                query=f"Explain why these products match the image and text query: {text_query}",
                context={"matches": matches}
            )
        else:
            # Perform image-only search
            matches = await ai_service.search_by_image(
                image=img,
                n=limit
            )
            
            explanation = await ai_service.get_response(
                query="Explain why these products match the image",
                context={"matches": matches}
            )
        
        return ImageSearchResponse(
            matches=matches,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image search: {str(e)}"
        ) 
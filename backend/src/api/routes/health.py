from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Estado del servicio
    """
    return {
        "status": "healthy",
        "service": "DocuMind API",
        "version": "1.0.0"
    }

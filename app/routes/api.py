from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from app.models.schemas import (
    QueryRequest, QueryResponse, AudioRequest, ThresholdRequest, 
    StatsResponse, HealthResponse
)
from app.models.enums import MatchingMethod
from app.services.audio_matcher import AudioMatcher

router = APIRouter()

matcher = None

def get_matcher():
    if not matcher:
        raise HTTPException(status_code=500, detail="System not initialized")
    return matcher

@router.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest, matcher: AudioMatcher = Depends(get_matcher)):
    """
    Process a query and return the most appropriate audio
    """
    if not matcher:
        raise HTTPException(status_code=500, detail="Sistema no inicializado")

    try:
        result = matcher.find_best_match(request.text, method=request.method)
        return QueryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        system_initialized=matcher is not None
    )

@router.get("/stats", response_model=StatsResponse)
async def get_stats(matcher: AudioMatcher = Depends(get_matcher)):
    stats = matcher.get_stats()
    return StatsResponse(**stats)

@router.post("/admin/add-audio")
async def add_audio(request: AudioRequest, matcher: AudioMatcher = Depends(get_matcher)):
    
    success = matcher.add_audio(request.audio_file, request.descriptions)
    if success:
        return {"message": f"Audio {request.audio_file} added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Error adding audio")

@router.post("/admin/update-threshold")
async def update_threshold(request: ThresholdRequest, matcher: AudioMatcher = Depends(get_matcher)):
    """
    Update the similarity threshold
    """
    success = matcher.update_threshold(request.threshold)
    if success:
        return {"message": f"Threshold updated to {request.threshold}"}
    else:
        raise HTTPException(status_code=400, detail="Invalid threshold (must be between 0.0 and 1.0)")

def initialize_matcher(audio_base_path: str = "audio_base.json"):
    global matcher
    if not matcher:
        matcher = AudioMatcher(audio_base_path)
    return matcher
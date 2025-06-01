from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any, Union
from .enums import MatchingMethod, ResponseStatus, MatchingMethodType, ConfidenceScore, AudioFileName

class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Query text to match against audio descriptions")
    method: MatchingMethodType = Field(default="hybrid", description="Matching method to use")
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()

class DetailedScores(BaseModel):
    """Schema for detailed scoring information"""
    individual_scores: Optional[List[float]] = None
    descriptions: Optional[List[str]] = None
    max_score: Optional[float] = None

class HybridScores(BaseModel):
    """Schema for hybrid method scoring information"""
    individual_scores: Optional[Dict[str, float]] = None
    combined_scores: Optional[Dict[str, float]] = None
    weights: Optional[Dict[str, float]] = None

class ComparisonInfo(BaseModel):
    """Schema for method comparison information"""
    combined_score: Optional[float] = None
    individual_score: Optional[float] = None

class QueryResponse(BaseModel):
    response: Union[AudioFileName, str]
    confidence: ConfidenceScore
    method: MatchingMethodType
    message: str
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    
    best_candidate: Optional[AudioFileName] = None
    all_scores: Optional[Dict[str, float]] = None
    detailed_scores: Optional[Union[Dict[str, DetailedScores], HybridScores]] = None
    method_used: Optional[str] = None
    compared_with: Optional[ComparisonInfo] = None
    error: Optional[str] = None
    
    @validator('confidence')
    def confidence_must_be_valid(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class AudioRequest(BaseModel):
    audio_file: AudioFileName = Field(..., description="Audio file name")
    descriptions: List[str] = Field(..., min_items=1, description="List of descriptions for the audio")
    
    @validator('descriptions')
    def descriptions_must_not_be_empty(cls, v):
        if not v or all(not desc.strip() for desc in v):
            raise ValueError('At least one non-empty description is required')
        return [desc.strip() for desc in v if desc.strip()]

class ThresholdRequest(BaseModel):
    threshold: ConfidenceScore = Field(..., ge=0.0, le=1.0, description="Similarity threshold between 0.0 and 1.0")

class StatsResponse(BaseModel):
    """Schema for system statistics"""
    total_audios: int
    model: str
    current_threshold: ConfidenceScore
    available_audios: List[AudioFileName]

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    system_initialized: bool
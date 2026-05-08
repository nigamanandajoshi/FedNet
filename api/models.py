"""API data models."""

from pydantic import BaseModel
from typing import List, Optional, Dict


class CBCData(BaseModel):
    """CBC data model."""
    hb: float
    rbc: float
    mcv: float
    mch: float
    mchc: float
    rdw: float
    wbc: float
    platelets: float


class PredictionResponse(BaseModel):
    """Prediction response model."""
    condition: str
    confidence: float
    probabilities: Dict[str, float]


class HospitalRegistration(BaseModel):
    """Hospital registration model."""
    hospital_id: str
    organization: str
    data_size: int
    data_quality: Optional[float] = 1.0


class FLRoundInfo(BaseModel):
    """Federated learning round information."""
    round_number: int
    num_clients: int
    global_metrics: Dict[str, float]
    timestamp: str

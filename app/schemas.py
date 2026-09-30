from typing import List
from pydantic import BaseModel, Field


class SmilesRequest(BaseModel):
    smiles: str = Field(...)


class SmilesListRequest(BaseModel):
    smiles_list: List[str] = Field(...)


class PredictionResponse(BaseModel):
    smiles: str
    prediction: float
    model_version: str


class HistoryEntry(BaseModel):
    timestamp: str
    smiles: str
    prediction: float


class HistoryResponse(BaseModel):
    success: bool
    historique: List[HistoryEntry]


class Mol2DResponse(BaseModel):
    smiles: str
    image_base64: str


class PropertiesResponse(BaseModel):
    count: int
    properties: List[dict]


class Molecule3DResponse(BaseModel):
    smiles: str
    html_url: str

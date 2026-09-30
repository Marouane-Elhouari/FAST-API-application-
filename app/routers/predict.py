from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_api_key
from ..model_utils import MODEL_VERSION, predict_smiles
from ..schemas import PredictionResponse, SmilesRequest
from .history import log_prediction

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictionResponse, dependencies=[Depends(require_api_key)])
def predict(payload: SmilesRequest):
    try:
        prediction = predict_smiles(payload.smiles)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {exc}") from exc

    log_prediction(payload.smiles, prediction)

    return PredictionResponse(
        smiles=payload.smiles,
        prediction=prediction,
        model_version=MODEL_VERSION,
    )

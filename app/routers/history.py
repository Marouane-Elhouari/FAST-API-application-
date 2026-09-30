import io
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from ..auth import require_api_key
from ..schemas import HistoryResponse

router = APIRouter(prefix="/api", tags=["history"])

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "history.csv"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_history_df() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame(columns=["timestamp", "smiles", "prediction"])
    return pd.read_csv(LOG_FILE)


def log_prediction(smiles: str, prediction: float) -> None:
    row = pd.DataFrame([{
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "smiles": smiles,
        "prediction": prediction,
    }])
    header = not LOG_FILE.exists()
    row.to_csv(LOG_FILE, mode="a", header=header, index=False)


@router.get("/history", response_model=HistoryResponse, dependencies=[Depends(require_api_key)])
def api_history():
    df = _read_history_df()
    return {"success": True, "historique": df.to_dict(orient="records")}


@router.get("/export-csv", dependencies=[Depends(require_api_key)])
def api_export_csv():
    if not LOG_FILE.exists():
        raise HTTPException(status_code=404, detail="Aucun historique disponible.")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"historique_optima_{ts}.csv"
    return FileResponse(
        LOG_FILE,
        media_type="text/csv",
        filename=filename,
    )


@router.get("/export-xlsx", dependencies=[Depends(require_api_key)])
def api_export_xlsx():
    if not LOG_FILE.exists():
        raise HTTPException(status_code=404, detail="Aucun historique disponible.")

    df = _read_history_df()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="historique")
    buffer.seek(0)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"historique_optima_{ts}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

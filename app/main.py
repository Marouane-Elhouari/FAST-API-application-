from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import API_KEY
from .model_utils import load_model
from .routers import chemistry, history, predict

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(
    title="GNN Molecular Property Prediction API",
    description="Backend REST API for AttentiveFP-based property prediction, "
                "2D/3D molecule visualization, and descriptor computation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(predict.router)
app.include_router(history.router)
app.include_router(chemistry.router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "gnn-prediction-api"}


@app.get("/", tags=["frontend"])
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"api_key": API_KEY},
    )


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, tracts, risk_scores, predict

app = FastAPI(
    title="GeoPulse API",
    description="Real-Time Urban Risk Intelligence Platform — Chicago",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://geopulse.vercel.app",  # update with your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(tracts.router, prefix="/tracts", tags=["Tracts"])
app.include_router(risk_scores.router, prefix="/risk-scores", tags=["Risk Scores"])
app.include_router(predict.router, prefix="/predict", tags=["Predict"])
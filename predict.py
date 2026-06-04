from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.services import geo_service, model_service
from app.schemas.risk import PredictRequest, PredictResponse

router = APIRouter()


@router.post("/", response_model=PredictResponse, summary="Predict risk for a lat/lon")
def predict_risk(body: PredictRequest, db: Session = Depends(get_db)):
    """
    Given a lat/lon, find the nearest census tract, load its features,
    and run model inference to return a risk score with SHAP explanations.
    """
    # 1. Find nearest tract
    tract_id = geo_service.find_nearest_tract(db, body.lat, body.lon)
    if not tract_id:
        raise HTTPException(status_code=404, detail="No census tracts found near that location")

    # 2. Load features for that tract
    sql = text("""
        SELECT * FROM risk_features WHERE tract_id = :tract_id
    """)
    row = db.execute(sql, {"tract_id": tract_id}).mappings().first()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No feature data for tract {tract_id}. Run the feature pipeline first."
        )

    # 3. Run model inference
    result = model_service.predict(dict(row))

    return PredictResponse(
        lat=body.lat,
        lon=body.lon,
        nearest_tract=tract_id,
        **result,
    )


@router.get("/nearby", summary="Risk scores for tracts near a lat/lon")
def get_nearby_risk(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db),
):
    """Return all tracts within radius_km of a point with their risk scores."""
    return geo_service.get_nearby_tracts(db, lat, lon, radius_km)
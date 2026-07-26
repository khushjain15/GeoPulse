from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import geo_service

router = APIRouter()


@router.get("/", summary="All tract risk scores as GeoJSON")
def get_all_risk_scores(db: Session = Depends(get_db)):
    """
    Return all census tracts with their ML risk scores as a GeoJSON FeatureCollection.
    Used by the frontend map to color tracts by risk level.
    """
    return geo_service.get_all_risk_scores_geojson(db)


@router.get("/{tract_id}", summary="Risk score for a single tract")
def get_risk_score(tract_id: str, db: Session = Depends(get_db)):
    """Return risk score + SHAP top factors for a single census tract."""
    result = geo_service.get_risk_score_by_id(db, tract_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No risk score for tract '{tract_id}'")
    return result
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import geo_service

router = APIRouter()


@router.get("/", summary="All census tracts as GeoJSON")
def get_all_tracts(db: Session = Depends(get_db)):
    """Return all Chicago census tracts as a GeoJSON FeatureCollection."""
    return geo_service.get_all_tracts_geojson(db)


@router.get("/{tract_id}", summary="Single tract with features and score")
def get_tract(tract_id: str, db: Session = Depends(get_db)):
    """Return a single tract with all risk features and score."""
    result = geo_service.get_tract_by_id(db, tract_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Tract '{tract_id}' not found")
    return result
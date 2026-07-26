"""Pydantic schemas for GeoJSON tract responses."""
from typing import Any, Optional
from pydantic import BaseModel


class TractProperties(BaseModel):
    tract_id: str
    name: Optional[str]
    county: Optional[str]
    state: Optional[str]
    population: Optional[int]
    median_income: Optional[float]
    area_km2: Optional[float]


class TractFeature(BaseModel):
    type: str = "Feature"
    properties: TractProperties
    geometry: Any  # raw GeoJSON geometry dict


class TractFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[TractFeature]
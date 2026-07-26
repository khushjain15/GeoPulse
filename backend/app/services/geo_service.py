"""Spatial query helpers using raw PostGIS SQL for performance."""
import json
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_all_tracts_geojson(db: Session) -> dict:
    """Return all tracts as a GeoJSON FeatureCollection."""
    sql = text("""
        SELECT
            t.tract_id,
            t.name,
            t.county,
            t.state,
            t.population,
            t.median_income,
            t.area_km2,
            ST_AsGeoJSON(t.geometry)::json AS geometry
        FROM tracts t
        ORDER BY t.tract_id
    """)
    rows = db.execute(sql).mappings().all()
    features = [
        {
            "type": "Feature",
            "properties": {
                "tract_id": r["tract_id"],
                "name": r["name"],
                "county": r["county"],
                "state": r["state"],
                "population": r["population"],
                "median_income": r["median_income"],
                "area_km2": r["area_km2"],
            },
            "geometry": r["geometry"],
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


def get_tract_by_id(db: Session, tract_id: str) -> dict | None:
    """Return a single tract with its risk features and score."""
    sql = text("""
        SELECT
            t.tract_id, t.name, t.county, t.state,
            t.population, t.median_income, t.area_km2,
            r.risk_score, r.risk_category, r.confidence,
            r.top_factor_1, r.top_factor_2, r.top_factor_3,
            f.population_density, f.flood_zone_overlap,
            f.distance_to_hospital, f.distance_to_shelter,
            f.road_density, f.impervious_surface_pct,
            f.tree_cover_pct, f.elevation_mean, f.building_density,
            ST_AsGeoJSON(t.geometry)::json AS geometry
        FROM tracts t
        LEFT JOIN risk_scores r  ON t.tract_id = r.tract_id
        LEFT JOIN risk_features f ON t.tract_id = f.tract_id
        WHERE t.tract_id = :tract_id
    """)
    row = db.execute(sql, {"tract_id": tract_id}).mappings().first()
    if not row:
        return None
    return {
        "type": "Feature",
        "properties": dict(row),
        "geometry": row["geometry"],
    }


def get_all_risk_scores_geojson(db: Session) -> dict:
    """Return all tracts with risk scores as a GeoJSON FeatureCollection."""
    sql = text("""
        SELECT
            t.tract_id, t.name, t.county, t.population,
            t.median_income, t.area_km2,
            r.risk_score, r.risk_category, r.confidence,
            r.top_factor_1, r.top_factor_2, r.top_factor_3,
            f.flood_zone_overlap, f.distance_to_hospital,
            f.population_density,
            ST_AsGeoJSON(t.geometry)::json AS geometry
        FROM tracts t
        LEFT JOIN risk_scores r  ON t.tract_id = r.tract_id
        LEFT JOIN risk_features f ON t.tract_id = f.tract_id
        ORDER BY r.risk_score DESC NULLS LAST
    """)
    rows = db.execute(sql).mappings().all()
    features = [
        {
            "type": "Feature",
            "properties": {k: v for k, v in r.items() if k != "geometry"},
            "geometry": r["geometry"],
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


def get_risk_score_by_id(db: Session, tract_id: str) -> dict | None:
    """Return risk score + features for a single tract."""
    sql = text("""
        SELECT
            r.tract_id, r.risk_score, r.risk_category,
            r.confidence, r.top_factor_1, r.top_factor_2, r.top_factor_3,
            r.updated_at,
            f.population_density, f.flood_zone_overlap,
            f.distance_to_hospital, f.distance_to_shelter,
            f.road_density, f.impervious_surface_pct,
            f.tree_cover_pct, f.elevation_mean, f.building_density
        FROM risk_scores r
        LEFT JOIN risk_features f ON r.tract_id = f.tract_id
        WHERE r.tract_id = :tract_id
    """)
    row = db.execute(sql, {"tract_id": tract_id}).mappings().first()
    return dict(row) if row else None


def find_nearest_tract(db: Session, lat: float, lon: float) -> str | None:
    """Return the tract_id of the tract whose centroid is nearest to lat/lon."""
    sql = text("""
        SELECT tract_id
        FROM tracts
        ORDER BY ST_Distance(
            ST_Centroid(geometry)::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
        )
        LIMIT 1
    """)
    row = db.execute(sql, {"lat": lat, "lon": lon}).first()
    return row[0] if row else None


def get_nearby_tracts(db: Session, lat: float, lon: float, radius_km: float = 5.0) -> dict:
    """Return tracts within radius_km of a point."""
    sql = text("""
        SELECT
            t.tract_id, t.name, t.county,
            r.risk_score, r.risk_category,
            ROUND(ST_Distance(
                ST_Centroid(t.geometry)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) / 1000, 2) AS distance_km,
            ST_AsGeoJSON(t.geometry)::json AS geometry
        FROM tracts t
        LEFT JOIN risk_scores r ON t.tract_id = r.tract_id
        WHERE ST_DWithin(
            t.geometry::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            :radius_m
        )
        ORDER BY distance_km
    """)
    rows = db.execute(sql, {"lat": lat, "lon": lon, "radius_m": radius_km * 1000}).mappings().all()
    features = [
        {
            "type": "Feature",
            "properties": {k: v for k, v in r.items() if k != "geometry"},
            "geometry": r["geometry"],
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}
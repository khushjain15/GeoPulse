"""
Phase 2 — Ingest OpenStreetMap data for Chicago into PostGIS.

Data fetched via OSMnx:
    - Hospitals (amenity=hospital)
    - Emergency shelters (amenity=shelter)
    - Road network (drive graph)

Writes to PostGIS tables: hospitals, shelters, roads

Usage:
    python pipelines/ingest_osm.py

Required env vars:
    DATABASE_URL
"""

import os
import geopandas as gpd
import osmnx as ox
from shapely.geometry import LineString
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PLACE = "Chicago, Illinois, USA"


def fetch_hospitals() -> gpd.GeoDataFrame:
    """Download hospital point locations via OSMnx."""
    print("Fetching hospitals from OSM...")
    tags = {"amenity": "hospital"}
    gdf = ox.features_from_place(PLACE, tags=tags)
    gdf = gdf[["geometry", "name", "osmid"]].copy() if "name" in gdf.columns else gdf[["geometry", "osmid"]].copy()

    # Convert polygons to centroids, keep only points
    gdf["geometry"] = gdf.geometry.centroid
    gdf = gdf.set_geometry("geometry").to_crs("EPSG:4326")
    gdf = gdf.rename(columns={"osmid": "osm_id"})
    gdf["name"] = gdf.get("name", "")
    print(f"  Found {len(gdf)} hospitals")
    return gdf[["name", "osm_id", "geometry"]]


def fetch_shelters() -> gpd.GeoDataFrame:
    """Download emergency shelter locations via OSMnx."""
    print("Fetching shelters from OSM...")
    tags = {"amenity": ["shelter", "social_facility"]}
    try:
        gdf = ox.features_from_place(PLACE, tags=tags)
        gdf["geometry"] = gdf.geometry.centroid
        gdf = gdf.set_geometry("geometry").to_crs("EPSG:4326")
        gdf = gdf.rename(columns={"osmid": "osm_id"})
        gdf["name"] = gdf.get("name", "")
        gdf = gdf[["name", "osm_id", "geometry"]]
        print(f"  Found {len(gdf)} shelters")
        return gdf
    except Exception as e:
        print(f"  Warning: shelter fetch returned: {e}. Using empty GeoDataFrame.")
        return gpd.GeoDataFrame(columns=["name", "osm_id", "geometry"], crs="EPSG:4326")


def fetch_road_network() -> gpd.GeoDataFrame:
    """Download Chicago drive network and return edges as GeoDataFrame."""
    print("Fetching road network from OSM (this may take a minute)...")
    G = ox.graph_from_place(PLACE, network_type="drive", simplify=True)
    _, edges = ox.graph_to_gdfs(G)
    edges = edges.reset_index()
    edges = edges.to_crs("EPSG:4326")

    # Compute length in meters
    edges_proj = edges.to_crs("EPSG:26916")
    edges["length_m"] = edges_proj.geometry.length

    edges["highway"] = edges["highway"].apply(
        lambda x: x[0] if isinstance(x, list) else x
    )
    edges["name"] = edges.get("name", "").apply(
        lambda x: x[0] if isinstance(x, list) else x
    )
    edges = edges[["osmid", "highway", "name", "length_m", "geometry"]].rename(
        columns={"osmid": "osm_id"}
    )
    print(f"  Found {len(edges)} road segments")
    return edges


def load_to_postgis(gdf: gpd.GeoDataFrame, table: str) -> None:
    engine = create_engine(DATABASE_URL)
    gdf.to_postgis(table, engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_geometry ON {table} USING GIST (geometry)"))
        conn.commit()
    print(f"  Wrote {len(gdf)} rows to {table}")


def main():
    hospitals = fetch_hospitals()
    shelters = fetch_shelters()
    roads = fetch_road_network()

    load_to_postgis(hospitals, "hospitals")
    load_to_postgis(shelters, "shelters")
    load_to_postgis(roads, "roads")

    print("OSM ingestion complete.")


if __name__ == "__main__":
    main()
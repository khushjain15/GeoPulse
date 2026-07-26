"""
Phase 2 — Ingest Census tract boundaries + ACS demographics into PostGIS.

Downloads:
    - Cook County, IL TIGER/Line census tract shapefile (2022)
    - ACS 5-Year: population, median income, housing units

Writes to PostGIS table: tracts

Usage:
    python pipelines/ingest_census.py

Required env vars:
    CENSUS_API_KEY
    DATABASE_URL
"""

import os
import io
import zipfile
import tempfile
import requests
import geopandas as gpd
import pandas as pd
from census import Census
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# Cook County, IL
STATE_FIPS = "17"
COUNTY_FIPS = "031"
YEAR = 2022

# TIGER/Line shapefile URL for Illinois census tracts
TIGER_URL = (
    f"https://www2.census.gov/geo/tiger/TIGER{YEAR}/TRACT/"
    f"tl_{YEAR}_{STATE_FIPS}_tract.zip"
)


def fetch_tract_boundaries() -> gpd.GeoDataFrame:
    """Download Illinois TIGER/Line tract shapefile, filter to Cook County."""
    print("Downloading TIGER/Line tract shapefile...")
    resp = requests.get(TIGER_URL, timeout=120)
    resp.raise_for_status()

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "tracts.zip")
        with open(zip_path, "wb") as f:
            f.write(resp.content)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmpdir)

        shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
        gdf = gpd.read_file(os.path.join(tmpdir, shp_files[0]))

    # Filter to Cook County only
    gdf = gdf[gdf["COUNTYFP"] == COUNTY_FIPS].copy()
    gdf = gdf.to_crs("EPSG:4326")

    # Compute area in km²
    gdf_proj = gdf.to_crs("EPSG:26916")  # UTM zone 16N for Chicago
    gdf["area_km2"] = gdf_proj.geometry.area / 1e6

    print(f"  Found {len(gdf)} tracts in Cook County")
    return gdf


def fetch_demographics() -> pd.DataFrame:
    """Pull ACS 5-Year population + median income per tract."""
    print("Fetching ACS 5-Year demographics...")
    c = Census(CENSUS_API_KEY)

    # B01003_001E = total population
    # B19013_001E = median household income
    data = c.acs5.state_county_tract(
        fields=("NAME", "B01003_001E", "B19013_001E"),
        state_fips=STATE_FIPS,
        county_fips=COUNTY_FIPS,
        tract="*",
        year=YEAR,
    )

    df = pd.DataFrame(data)
    df["tract_id"] = df["state"] + df["county"] + df["tract"]
    df = df.rename(columns={
        "B01003_001E": "population",
        "B19013_001E": "median_income",
    })
    df["population"] = pd.to_numeric(df["population"], errors="coerce").astype("Int64")
    df["median_income"] = pd.to_numeric(df["median_income"], errors="coerce")
    df["median_income"] = df["median_income"].where(df["median_income"] > 0)

    print(f"  Fetched demographics for {len(df)} tracts")
    return df[["tract_id", "population", "median_income"]]


def load_to_postgis(gdf: gpd.GeoDataFrame) -> None:
    """Write the merged GeoDataFrame to PostGIS tracts table."""
    print("Writing to PostGIS tracts table...")
    engine = create_engine(DATABASE_URL)

    # Drop and recreate via geopandas (handles geometry column automatically)
    gdf_out = gdf[["tract_id", "name", "county", "state", "population", "median_income", "area_km2", "geometry"]]
    gdf_out.to_postgis(
        "tracts",
        engine,
        if_exists="replace",
        index=False,
        dtype={"geometry": "GEOMETRY"},
    )

    # Re-create GIST index (to_postgis doesn't add it)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tracts_geometry ON tracts USING GIST (geometry)"))
        conn.commit()

    print(f"  Wrote {len(gdf_out)} tracts to PostGIS")


def main():
    gdf = fetch_tract_boundaries()
    demographics = fetch_demographics()

    # Build tract_id from GEOID column
    gdf["tract_id"] = gdf["GEOID"]
    gdf["name"] = gdf["NAMELSAD"]
    gdf["county"] = "Cook"
    gdf["state"] = "Illinois"

    # Join demographics
    gdf = gdf.merge(demographics, on="tract_id", how="left")

    load_to_postgis(gdf)
    print("Census ingestion complete.")


if __name__ == "__main__":
    main()
-- ============================================================
-- GeoPulse Database Initialization
-- Run automatically by postgis/postgis Docker image on first start
-- ============================================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ============================================================
-- TABLE: tracts
-- Census tract boundaries + demographic attributes
-- ============================================================
CREATE TABLE IF NOT EXISTS tracts (
    tract_id        VARCHAR(20) PRIMARY KEY,
    name            VARCHAR(100),
    county          VARCHAR(100),
    state           VARCHAR(50),
    population      INTEGER,
    median_income   FLOAT,
    area_km2        FLOAT,
    geometry        GEOMETRY(MULTIPOLYGON, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tracts_geometry
    ON tracts USING GIST (geometry);

CREATE INDEX IF NOT EXISTS idx_tracts_county
    ON tracts (county);

-- ============================================================
-- TABLE: flood_zones
-- FEMA National Flood Hazard Layer polygons
-- ============================================================
CREATE TABLE IF NOT EXISTS flood_zones (
    id          SERIAL PRIMARY KEY,
    fld_zone    VARCHAR(20),        -- e.g. AE, X, AO
    zone_subty  VARCHAR(50),
    sfha_tf     BOOLEAN,            -- Special Flood Hazard Area
    geometry    GEOMETRY(MULTIPOLYGON, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_flood_zones_geometry
    ON flood_zones USING GIST (geometry);

-- ============================================================
-- TABLE: hospitals
-- OSM hospital point locations
-- ============================================================
CREATE TABLE IF NOT EXISTS hospitals (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200),
    osm_id      BIGINT,
    geometry    GEOMETRY(POINT, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hospitals_geometry
    ON hospitals USING GIST (geometry);

-- ============================================================
-- TABLE: shelters
-- OSM emergency shelter point locations
-- ============================================================
CREATE TABLE IF NOT EXISTS shelters (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200),
    osm_id      BIGINT,
    geometry    GEOMETRY(POINT, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_shelters_geometry
    ON shelters USING GIST (geometry);

-- ============================================================
-- TABLE: roads
-- OSM road network (simplified linestrings per tract)
-- ============================================================
CREATE TABLE IF NOT EXISTS roads (
    id          SERIAL PRIMARY KEY,
    osm_id      BIGINT,
    highway     VARCHAR(50),
    name        VARCHAR(200),
    length_m    FLOAT,
    geometry    GEOMETRY(LINESTRING, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_roads_geometry
    ON roads USING GIST (geometry);

-- ============================================================
-- TABLE: risk_features
-- Engineered ML features per census tract
-- ============================================================
CREATE TABLE IF NOT EXISTS risk_features (
    tract_id                VARCHAR(20) PRIMARY KEY
        REFERENCES tracts(tract_id) ON DELETE CASCADE,
    population_density      FLOAT,      -- people / km²
    median_income           FLOAT,      -- USD
    flood_zone_overlap      FLOAT,      -- 0.0 – 1.0 fraction of tract area
    distance_to_hospital    FLOAT,      -- km
    distance_to_shelter     FLOAT,      -- km
    road_density            FLOAT,      -- road km / tract km²
    impervious_surface_pct  FLOAT,      -- 0.0 – 100.0
    tree_cover_pct          FLOAT,      -- 0.0 – 100.0
    elevation_mean          FLOAT,      -- meters
    building_density        FLOAT,      -- building footprint fraction
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: risk_scores
-- ML model prediction outputs per census tract
-- ============================================================
CREATE TABLE IF NOT EXISTS risk_scores (
    tract_id        VARCHAR(20) PRIMARY KEY
        REFERENCES tracts(tract_id) ON DELETE CASCADE,
    risk_score      FLOAT NOT NULL,         -- 0 – 100
    risk_category   VARCHAR(20) NOT NULL,   -- Low / Medium / High / Critical
    confidence      FLOAT,                  -- 0.0 – 1.0
    top_factor_1    VARCHAR(100),
    top_factor_2    VARCHAR(100),
    top_factor_3    VARCHAR(100),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_scores_category
    ON risk_scores (risk_category);

CREATE INDEX IF NOT EXISTS idx_risk_scores_score
    ON risk_scores (risk_score DESC);

-- ============================================================
-- VIEWS
-- ============================================================

-- Handy view: tracts + scores + features joined
CREATE OR REPLACE VIEW tract_risk_view AS
SELECT
    t.tract_id,
    t.name,
    t.county,
    t.state,
    t.population,
    t.median_income,
    t.area_km2,
    r.risk_score,
    r.risk_category,
    r.confidence,
    r.top_factor_1,
    r.top_factor_2,
    r.top_factor_3,
    r.updated_at,
    f.population_density,
    f.flood_zone_overlap,
    f.distance_to_hospital,
    f.distance_to_shelter,
    f.road_density,
    f.impervious_surface_pct,
    f.tree_cover_pct,
    f.elevation_mean,
    f.building_density,
    t.geometry
FROM tracts t
LEFT JOIN risk_scores r  ON t.tract_id = r.tract_id
LEFT JOIN risk_features f ON t.tract_id = f.tract_id;
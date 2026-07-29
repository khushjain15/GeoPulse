# 🌍 GeoPulse Intelligence

> **An end-to-end geospatial intelligence platform that transforms raw spatial data into actionable urban risk insights using machine learning, GIS, and cloud-native data engineering.**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![PostGIS](https://img.shields.io/badge/PostGIS-Spatial_Database-336791)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

GeoPulse Intelligence is a production-inspired full-stack geospatial intelligence platform that combines **GIS, machine learning, cloud-native data engineering, and interactive mapping** to generate explainable urban and environmental risk insights.

Rather than being a simple mapping application, GeoPulse demonstrates how modern organizations transform large-scale geospatial datasets into actionable intelligence using scalable software engineering practices.

The project models the architecture of real-world systems used in:

- Smart Cities
- Emergency Management
- Climate Risk Analysis
- Urban Planning
- Infrastructure Development
- Disaster Response
- Environmental Monitoring
- Insurance Risk Assessment

---

# Why GeoPulse?

Every city generates enormous volumes of geospatial data:

- Population demographics
- Flood zones
- Transportation networks
- Hospitals
- Emergency shelters
- Critical infrastructure
- Census information
- Environmental datasets

Most of this information exists across independent systems.

GeoPulse brings these datasets together into a single intelligence platform capable of:

- Predicting environmental risk
- Explaining machine learning decisions
- Visualizing geographic information
- Serving predictions through scalable REST APIs

---

# What GeoPulse Can Do

Given any latitude and longitude, GeoPulse can:

- Predict environmental risk
- Explain why the prediction was made using SHAP
- Locate nearby critical infrastructure
- Display interactive GIS visualizations
- Compare neighbouring census tracts
- Serve predictions through REST APIs
- Process multiple public geospatial datasets
- Demonstrate production-inspired geospatial software architecture

---

# Features

## Geospatial Data Engineering

- Import Census TIGER datasets
- Import OpenStreetMap road networks
- Import FEMA flood zones
- Automated ETL pipelines
- Spatial indexing using PostGIS
- Geographic feature engineering

---

## Machine Learning

- XGBoost prediction models
- SHAP explainability
- Risk score generation
- Feature importance analysis
- Reproducible training pipeline

---

## Backend API

- FastAPI
- RESTful API design
- SQLAlchemy ORM
- Pydantic validation
- Modular architecture
- Dependency injection

---

## Interactive GIS Dashboard

- React
- TypeScript
- Mapbox GL JS
- Interactive choropleth maps
- Dynamic filtering
- Real-time visualization

---

## Database

- PostgreSQL
- PostGIS
- Spatial SQL
- Geometry indexing
- Efficient nearest-neighbour searches

---

## DevOps

- Docker
- Docker Compose
- Environment configuration
- Modular project architecture
- GitHub Actions (planned)

---

# Technology Stack

| Category | Technologies |
|------------|--------------|
| Backend | Python, FastAPI |
| Database | PostgreSQL, PostGIS |
| Machine Learning | XGBoost, Scikit-Learn, SHAP |
| GIS | GeoPandas, OSMnx, Rasterio, Shapely |
| Frontend | React, TypeScript, Mapbox GL JS |
| Data Engineering | Pandas, NumPy |
| Infrastructure | Docker, Docker Compose |
| Version Control | Git, GitHub |

---

# System Architecture

```text
                    Public Geospatial Data
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
 Census TIGER          OpenStreetMap            FEMA
      │                      │                      │
      └──────────────────────┼──────────────────────┘
                             │
                    Data Ingestion Pipelines
                             │
                  Feature Engineering & ETL
                             │
                     PostgreSQL + PostGIS
                             │
                  Machine Learning Pipeline
                             │
                    FastAPI REST Backend
                             │
                   React + Mapbox Frontend
                             │
              Interactive Geospatial Dashboard
```

---

# Project Structure

```text
GeoPulse/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── predict.py
│   │   │   ├── risk_scores.py
│   │   │   └── tracts.py
│   │   │
│   │   ├── db/
│   │   │   └── session.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── main.py
│   └── Dockerfile
│
├── database/
│
├── frontend/
│   ├── api/
│   ├── charts/
│   ├── components/
│   ├── maps/
│   ├── pages/
│   └── types/
│
├── pipelines/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── models/
├── notebooks/
├── docs/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

---

# Example API

## Predict Risk

```http
POST /predict
```

Example Request

```json
{
  "latitude": 43.0731,
  "longitude": -89.4012
}
```

Example Response

```json
{
  "risk_score": 0.82,
  "risk_level": "High",
  "top_factors": [
    "Population Density",
    "Flood Risk",
    "Distance to Hospital"
  ]
}
```

---

## Health Check

```http
GET /health
```

Example Response

```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "version": "1.0.0"
}
```

---

# Getting Started

## Clone the Repository

```bash
git clone https://github.com/khushjain15/GeoPulse.git

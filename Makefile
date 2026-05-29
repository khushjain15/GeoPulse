.PHONY: up down logs shell-db shell-backend ingest-census ingest-osm ingest-fema features train

# ── Docker ────────────────────────────────────────────────────────
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

shell-db:
	docker exec -it geopulse_db psql -U geopulse -d geopulse

shell-backend:
	docker exec -it geopulse_backend bash

# ── Data pipelines ────────────────────────────────────────────────
ingest-census:
	docker exec geopulse_backend python /app/../pipelines/ingest_census.py

ingest-osm:
	docker exec geopulse_backend python /app/../pipelines/ingest_osm.py

ingest-fema:
	docker exec geopulse_backend python /app/../pipelines/ingest_fema.py

features:
	docker exec geopulse_backend python /app/../pipelines/build_features.py

train:
	docker exec geopulse_backend python /app/../pipelines/train_model.py

# ── Shortcuts ─────────────────────────────────────────────────────
# Run all Phase 2+3+4 in order
pipeline: ingest-census ingest-osm ingest-fema features train

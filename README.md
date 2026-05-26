# Predictive Vehicle Service Recommendation API

ML-powered FastAPI service that predicts the next vehicle service date and odometer milestone, returning whichever trigger (time or km) comes first.

## Status — all phases complete

| Phase | Description | Status |
|---|---|---|
| 0 | Refined `ideas.md` — locked decisions, response contract, glossary | Done |
| 1 | FastAPI skeleton + deterministic rules predictor | Done |
| 2 | Synthetic dataset (3,000 rows) + EDA notebook | Done |
| 3 | v1 model: DecisionTree, 2 features, mean MAE 56.9 | Done |
| 4 | ML model wired into `/predict` with `?mode=model\|rules` toggle | Done |
| 5 | Per-vehicle service history + personalised prediction + `next_service_km` | Done |
| 6 | v2 model: RandomForest, 6 features, mean MAE 46.1 (beats v1) | Done |
| 7 | pytest (20/20), Dockerfile, structured logging | Done |

## Setup

```powershell
.\myenv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive Swagger UI.

## Tests

```powershell
pytest tests/ -v
```

## Regenerate training data + retrain

```powershell
python -m training.synthesize          # -> data/processed/service_history.csv
python -m training.train               # -> models/service_predictor.pkl (v1)
python -m training.train_v2            # -> models/service_predictor_v2.pkl (v2)
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root |
| `GET` | `/health` | Health check — shows `model_v1_loaded` and `model_v2_loaded` |
| `POST` | `/predict?mode=model\|rules` | Stateless prediction. Include optional v2 fields to use the expanded model. |
| `POST` | `/vehicles/{id}/service` | Record a service event + optional vehicle metadata |
| `GET` | `/vehicles/{id}/history` | Service history + empirical km/month |
| `POST` | `/vehicles/{id}/predict` | Personalised prediction from current odometer |

## Model selection logic

```
POST /predict called
├── mode=rules → deterministic rule baseline
├── v2 fields provided (make, year, fuel_type, last_service_type) + model_v2 loaded
│   └── RandomForestRegressor (6 features) — source: "model_v2"
├── model_v1 loaded
│   └── DecisionTreeRegressor (2 features) — source: "model_v1"
└── fallback → deterministic rule baseline — source: "rules"
```

## Example: stateless v2 prediction

```powershell
curl -X POST http://127.0.0.1:8000/predict `
  -H "Content-Type: application/json" `
  -d '{
    "months_driven": 5,
    "total_kms_driven": 7200,
    "make": "Toyota",
    "vehicle_model": "Corolla",
    "year": 2020,
    "fuel_type": "petrol",
    "last_service_type": "oil_change"
  }'
```

## Example: per-vehicle personalised flow

```powershell
# 1. Record first service with vehicle metadata
curl -X POST http://127.0.0.1:8000/vehicles/V001/service `
  -H "Content-Type: application/json" `
  -d '{
    "service_date": "2025-11-01",
    "odometer_km": 45000,
    "service_type": "oil_change",
    "vehicle_metadata": {"make": "Toyota", "vehicle_model": "Corolla", "year": 2020, "fuel_type": "petrol"}
  }'

# 2. Record most recent service
curl -X POST http://127.0.0.1:8000/vehicles/V001/service `
  -H "Content-Type: application/json" `
  -d '{"service_date": "2026-05-01", "odometer_km": 54800, "service_type": "full_service"}'

# 3. Predict (uses stored metadata → model_v2 automatically)
curl -X POST http://127.0.0.1:8000/vehicles/V001/predict `
  -H "Content-Type: application/json" `
  -d '{"current_odometer_km": 55900}'
```

## Project layout

```
app/
  main.py                    FastAPI app + lifespan (loads v1 + v2 at startup)
  routers/
    predict.py               POST /predict
    vehicles.py              Vehicle history + personalised predict
  schemas/
    service.py               Pydantic models (stateless)
    vehicle.py               Pydantic models (vehicle endpoints)
  services/
    rules.py                 Deterministic baseline (always available)
    predictor.py             v2 → v1 → rules dispatcher
storage/
  history.py                 JSON-backed per-vehicle store
training/
  synthesize.py              Synthetic dataset generator (3,000 rows, 6 features)
  train.py                   v1 training (DecisionTree, 2 features)
  train_v2.py                v2 training (RandomForest, 6 features)
models/
  service_predictor.pkl      v1 model
  service_predictor_v2.pkl   v2 model
  metrics.json               v1 evaluation
  metrics_v2.json            v2 evaluation
data/
  processed/service_history.csv
  README.md                  Dataset notes + Kaggle candidates
notebooks/
  01_eda.ipynb               EDA: distributions, correlations, scatter plots
tests/
  test_rules.py              Unit tests for deterministic predictor
  test_api.py                Integration tests for all endpoints (20/20)
Dockerfile
.dockerignore
_archive/                    Original patient-records demo (reference)
```

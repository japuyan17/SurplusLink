# SurplusLink

Hunger isn't a food shortage problem, it's a logistics problem. SurplusLink matches surplus food from dining halls, restaurants, and events with nearby pantries in real time.

Built for the GM#11 hackathon, targeting **UN SDG 2: Zero Hunger**.

## Features
- **Post surplus** in seconds: food, quantity, pickup deadline, dietary tags
- **Optimal matching** of listings to pantries (Hungarian algorithm) scored on distance, urgency, dietary fit, and capacity
- **Surplus forecasting** (gradient boosting) so pantries can plan ahead
- **Impact dashboard**: meals saved, lbs diverted, CO2e avoided
- **Notifications** to matched pantries (logged; swap in SNS/Twilio)

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # API on :8000 (docs at /docs)
streamlit run streamlit_app.py         # UI on :8501
pytest
```

## API
| Method | Route | Purpose |
|---|---|---|
| GET | `/sites` | Donor sites |
| GET | `/pantries` | Pantries |
| POST | `/listings` | Post surplus |
| GET | `/listings` | All listings |
| POST | `/match` | Run matching on open listings |
| GET | `/notifications` | Notifications sent |
| GET | `/forecast` | Predicted surplus (lbs) |
| GET | `/impact` | Impact totals |

## Structure
```
app/
  main.py       FastAPI routes
  models.py     Pydantic models
  store.py      In-memory store (swap for Postgres)
  matching.py   Scoring + Hungarian assignment
  forecast.py   Surplus forecasting model
  seed.py       Sample Berkeley data (verify before demoing)
streamlit_app.py
tests/
```

## Assumptions
- 1.2 lbs of food = 1 meal (Feeding America convention)
- 1.1 kg CO2e avoided per lb diverted (approximate; cite your source in the submission)
- Forecast model trains on synthetic data; replace with real dining/event data when available

## Roadmap
- Postgres + auth for donors and pantries
- SMS/email alerts via AWS SNS
- Volunteer pickup route optimization
- Deploy on AWS (EC2 or Lambda + S3)

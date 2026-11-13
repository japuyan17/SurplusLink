# SurplusLink

Hunger isn't a food shortage problem, it's a logistics problem. SurplusLink matches surplus food from dining halls, restaurants, and events with nearby pantries in real time.

Built for the GM#11 hackathon, targeting **UN SDG 2: Zero Hunger**.

## Features
- **Accounts**: sign up as a donor or a neighbor looking for food; passwords are hashed and sessions use signed, expiring tokens
- **Donor dashboard** (`/donate`): how-to-donate guide, post surplus, run matching, track your listings
- **Pickup dashboard** (`/pickup`): live list of available food with where to pick it up, a map, and directions
- **Find food & shelter** (`/find-help`): map and cards for local food banks and shelters
- **Give back** (`/give-back`): volunteer and donation opportunities nearby
- **Optimal matching** of listings to pantries (Hungarian algorithm) scored on distance, urgency, dietary fit, and capacity
- **Surplus forecasting** (gradient boosting) so pantries can plan ahead
- **Impact dashboard** on the home page: meals saved, lbs diverted, CO2e avoided

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # API on :8000 (docs at /docs)
streamlit run streamlit_app.py         # UI on :8501
pytest
```
Run the API and the UI in two separate terminals. Set `API_URL` if the API isn't at `http://127.0.0.1:8000`, and `SECRET_KEY` to sign tokens in production.

## Pages
| URL | Who | Purpose |
|---|---|---|
| `/` | everyone | Impact, how it works, forecast |
| `/find-help` | everyone | Food banks and shelters map |
| `/give-back` | everyone | Volunteer and donation opportunities |
| `/login` | logged out | Log in or sign up |
| `/donate` | donors | Donor dashboard |
| `/pickup` | neighbors | Pickup dashboard |

## API
| Method | Route | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | | Create account, returns token |
| POST | `/auth/login` | | Log in, returns token |
| GET | `/auth/me` | any | Current user |
| GET | `/sites`, `/pantries` | | Donor sites and pantries |
| GET | `/resources?kind=` | | Food banks, shelters, volunteer and donation places |
| POST | `/listings` | donor | Post surplus |
| GET | `/listings` | | All listings |
| GET | `/listings/mine` | donor | Your listings |
| GET | `/pickups` | any | Active food with pickup locations |
| POST | `/match` | any | Run matching on open listings |
| GET | `/notifications` | | Notifications sent |
| GET | `/forecast` | | Predicted surplus (lbs) |
| GET | `/impact` | | Impact totals |

## Structure
```
app/
  main.py       FastAPI routes
  auth.py       Password hashing, signed tokens, role checks
  models.py     Pydantic models
  store.py      In-memory store (swap for Postgres)
  matching.py   Scoring + Hungarian assignment
  forecast.py   Surplus forecasting model
  resources.py  Local food banks, shelters, volunteer/donation places
  seed.py       Sample Berkeley data (verify before demoing)
streamlit_app.py  Navigation and page routing
ui.py             API client and shared UI helpers
views/            One file per page
tests/
```

## Assumptions
- 1.2 lbs of food = 1 meal (Feeding America convention)
- 1.1 kg CO2e avoided per lb diverted (approximate; cite your source in the submission)
- Forecast model trains on synthetic data; replace with real dining/event data when available
- Accounts, listings, and notifications live in memory and reset when the API restarts
- Resource coordinates are approximate; hours and addresses change, so verify before demoing

## Roadmap
- Postgres + persistent accounts
- SMS/email alerts via AWS SNS
- Volunteer pickup route optimization
- Deploy on AWS (EC2 or Lambda + S3)

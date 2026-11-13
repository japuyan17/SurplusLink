import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
TAGS = ["vegetarian", "vegan", "halal", "gluten-free", "produce", "baked goods", "prepared meals"]


def get(path: str, **params):
    r = requests.get(f"{API}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def post(path: str, payload: dict | None = None):
    r = requests.post(f"{API}{path}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


st.set_page_config(page_title="SurplusLink", page_icon="🍽️", layout="wide")
st.title("🍽️ SurplusLink")
st.caption("Hunger isn't a food shortage problem, it's a logistics problem.")

try:
    sites, pantries = get("/sites"), get("/pantries")
except requests.RequestException:
    st.error(f"Can't reach the API at {API}. Start it with: uvicorn app.main:app --reload")
    st.stop()

post_tab, match_tab, map_tab, forecast_tab, impact_tab = st.tabs(
    ["Post surplus", "Match & notify", "Map", "Forecast", "Impact"]
)

with post_tab:
    with st.form("post"):
        site = st.selectbox("Donor site", sites, format_func=lambda s: s["name"])
        food = st.text_input("Food", "Pasta and roasted vegetables")
        qty = st.number_input("Quantity (lbs)", min_value=1.0, value=40.0, step=5.0)
        hours = st.slider("Pickup deadline (hours from now)", 1, 12, 3)
        tags = st.multiselect("Tags", TAGS)
        if st.form_submit_button("Post surplus", type="primary"):
            deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
            post("/listings", {
                "site_id": site["id"], "food": food, "quantity_lbs": qty,
                "pickup_deadline": deadline.isoformat(), "dietary_tags": tags,
            })
            st.success("Listing posted")

with match_tab:
    if st.button("Run matching", type="primary"):
        res = post("/match")
        st.success(f"Matched {len(res['matched'])} listing(s); {res['still_open']} still open")
    pantry_names = {p["id"]: p["name"] for p in pantries}
    site_names = {s["id"]: s["name"] for s in sites}
    listings = get("/listings")
    if listings:
        df = pd.DataFrame(listings)
        df["site"] = df["site_id"].map(site_names)
        df["pantry"] = df["pantry_id"].map(pantry_names)
        st.dataframe(df[["id", "site", "food", "quantity_lbs", "status", "pantry", "score"]], hide_index=True)
    st.subheader("Notifications")
    for n in reversed(get("/notifications")):
        st.write(f"📣 **{pantry_names.get(n['pantry_id'], n['pantry_id'])}**: {n['message']}")

with map_tab:
    pts = [{"lat": s["lat"], "lon": s["lon"], "color": "#e4572e", "size": 40} for s in sites]
    pts += [{"lat": p["lat"], "lon": p["lon"], "color": "#2e86ab", "size": 60} for p in pantries]
    st.map(pd.DataFrame(pts), color="color", size="size")
    st.caption("Red: donor sites. Blue: pantries.")

with forecast_tab:
    days = st.slider("Days ahead", 1, 14, 7)
    fc = pd.DataFrame(get("/forecast", days=days))
    st.line_chart(fc.pivot(index="date", columns="site", values="predicted_lbs"))
    st.caption("Predicted surplus (lbs) from a gradient boosting model trained on synthetic data.")

with impact_tab:
    imp = get("/impact")
    c1, c2, c3 = st.columns(3)
    c1.metric("Meals saved", f"{imp['meals_saved']:,.0f}")
    c2.metric("Lbs diverted", f"{imp['lbs_diverted']:,.0f}")
    c3.metric("CO2e avoided (kg)", f"{imp['co2e_kg_avoided']:,.0f}")

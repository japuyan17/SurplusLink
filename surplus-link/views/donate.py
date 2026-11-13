from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

import ui

u = ui.require_login("donor")
st.title("🍱 Donor dashboard")
st.caption(f"Welcome, {u['name']}")

with st.expander("How to donate surplus food", expanded=True):
    st.markdown(
        "1. **Package it safely.** Keep hot food hot (above 135°F) and cold food cold (below 41°F). "
        "Label the contents and any allergens.\n"
        "2. **Post a listing** below: what it is, how many pounds, and when it must be picked up by.\n"
        "3. **Run matching.** We pick the best pantry by distance, urgency, dietary fit, and capacity.\n"
        "4. **Hand it off.** The matched pantry is notified. Have the food ready by your pickup deadline.\n\n"
        "In the US, the Bill Emerson Good Samaritan Food Donation Act generally protects good-faith food donors from liability."
    )

sites = ui.fetch("/sites")
default_site = next((i for i, s in enumerate(sites) if s["id"] == u.get("site_id")), 0)

st.subheader("Post surplus")
with st.form("post"):
    site = st.selectbox("Pickup location", sites, index=default_site, format_func=lambda s: s["name"])
    food = st.text_input("Food", "Pasta and roasted vegetables")
    qty = st.number_input("Quantity (lbs)", min_value=1.0, value=40.0, step=5.0)
    hours = st.slider("Pickup deadline (hours from now)", 1, 12, 3)
    tags = st.multiselect("Tags", ui.TAGS)
    submitted = st.form_submit_button("Post surplus", type="primary")
if submitted:
    deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
    ok, data = ui.request("POST", "/listings", json={
        "site_id": site["id"], "food": food, "quantity_lbs": qty,
        "pickup_deadline": deadline.isoformat(), "dietary_tags": tags,
    })
    st.success("Listing posted") if ok else st.error(data)

st.subheader("Your listings")
if st.button("Run matching"):
    ok, res = ui.request("POST", "/match")
    if ok:
        st.success(f"Matched {len(res['matched'])} listing(s); {res['still_open']} still open")
    else:
        st.error(res)

mine = ui.fetch("/listings/mine")
if mine:
    pantry_names = {p["id"]: p["name"] for p in ui.fetch("/pantries")}
    df = pd.DataFrame(mine)
    df["pickup by"] = ui.local_time(df["pickup_deadline"])
    df["pantry"] = df["pantry_id"].map(pantry_names)
    st.dataframe(df[["id", "food", "quantity_lbs", "pickup by", "status", "pantry"]], hide_index=True)
else:
    st.info("No listings yet. Post your first surplus above.")

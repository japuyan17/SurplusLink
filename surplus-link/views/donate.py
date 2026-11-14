from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

import theme
import ui

u = ui.require_login("donor")
theme.page_header("Donor dashboard", f"Welcome, {u['name']}. Thank you for sharing what you have.", "icon_post")

mine = ui.fetch("/listings/mine")
posted = sum(l["quantity_lbs"] for l in mine)
matched = sum(l["quantity_lbs"] for l in mine if l["status"] == "matched")
theme.stats([
    (str(len(mine)), "Listings posted", "#F28C38"),
    (f"{posted:,.0f}", "Pounds offered", "#2E86AB"),
    (f"{matched / 1.2:,.0f}", "Meals matched", "#2F7D5B"),
])

theme.section("How to donate surplus food")
theme.feature_cards([
    ("icon_post", "1. Package it safely",
     "Keep hot food hot (above 135°F) and cold food cold (below 41°F). Label what it is and any allergens.", "#F28C38"),
    ("icon_post", "2. Post a listing", "Tell us what it is, how many pounds, and when it must be picked up by.", "#E4572E"),
    ("icon_match", "3. Run matching", "We pick the best pantry by distance, urgency, dietary fit, and capacity.", "#2F7D5B"),
    ("icon_pickup", "4. Hand it off", "The matched pantry is notified. Have the food ready by your pickup deadline.", "#2E86AB"),
], min_width=200)
theme.render(
    '<div class="sl-quote">In the US, the Bill Emerson Good Samaritan Food Donation Act generally protects '
    "good-faith food donors from liability, except in cases of gross negligence or intentional misconduct.</div>"
)

theme.section("Post surplus food")
sites = ui.fetch("/sites")
default_site = next((i for i, s in enumerate(sites) if s["id"] == u.get("site_id")), 0)
with st.form("post"):
    site = st.selectbox("Pickup location", sites, index=default_site, format_func=lambda s: s["name"])
    food = st.text_input("Food", "Pasta and roasted vegetables")
    c1, c2 = st.columns(2)
    qty = c1.number_input("Quantity (lbs)", min_value=1.0, value=40.0, step=5.0)
    hours = c2.slider("Pickup deadline (hours from now)", 1, 12, 3)
    tags = st.multiselect("Tags", ui.TAGS)
    submitted = st.form_submit_button("Post surplus", type="primary")
if submitted:
    deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
    ok, data = ui.request("POST", "/listings", json={
        "site_id": site["id"], "food": food, "quantity_lbs": qty,
        "pickup_deadline": deadline.isoformat(), "dietary_tags": tags,
    })
    if ok:
        st.success("Listing posted. Run matching to send it to a pantry.")
        st.rerun()
    st.error(data)

theme.section("Your listings")
if st.button("Run matching", type="primary"):
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
    theme.empty_state("No listings yet", "Post your first surplus above and it will show up here.", "icon_post")

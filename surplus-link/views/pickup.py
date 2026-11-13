import pandas as pd
import streamlit as st

import ui

ui.require_login("recipient")
st.title("🛒 Pickup dashboard")
st.caption("Fresh surplus food available now, and where to get it.")

items = ui.fetch("/pickups")
if not items:
    st.info("No surplus food is listed right now. Check back soon, or find a food bank near you.")
    st.page_link("views/find_help.py", label="Find food banks and shelters", icon="📍")
else:
    ui.show_map([
        {"lat": i["pantry_lat"] or i["site_lat"], "lon": i["pantry_lon"] or i["site_lon"], "color": "#2e86ab"}
        for i in items
    ])
    for it in items:
        deadline = ui.local_time(pd.Series([it["pickup_deadline"]])).iloc[0]
        lat, lon = it["pantry_lat"] or it["site_lat"], it["pantry_lon"] or it["site_lon"]
        with st.container(border=True):
            st.markdown(f"**{it['food']}** · {it['quantity_lbs']:.0f} lbs")
            if it["dietary_tags"]:
                st.caption(", ".join(it["dietary_tags"]))
            st.write(f"🍽️ Prepared at: {it['site']}")
            st.write(f"📍 Pick up at: {it['pantry'] or 'Being matched to a pantry...'}")
            st.write(f"⏰ Available until: {deadline}")
            st.link_button("Get directions", ui.directions_url(lat, lon))

st.subheader("Recent pantry notifications")
notes = ui.fetch("/notifications")
pantry_names = {p["id"]: p["name"] for p in ui.fetch("/pantries")}
for n in reversed(notes[-5:]):
    st.write(f"📣 **{pantry_names.get(n['pantry_id'], n['pantry_id'])}**: {n['message']}")
if not notes:
    st.caption("Nothing yet.")

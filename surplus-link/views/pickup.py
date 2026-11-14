import pandas as pd
import streamlit as st

import mapview
import theme
import ui

ui.require_login("recipient")
theme.page_header("Pickup dashboard", "Fresh surplus food available now, and how to get to it.", "icon_pickup")

items = ui.fetch("/pickups")
if not items:
    theme.empty_state(
        "No surplus food listed right now",
        "New donations show up here as soon as they're posted. Check back soon, or find a food bank near you.",
        "icon_pickup",
    )
    st.page_link("views/find_help.py", label="Find food banks and shelters", icon=":material/location_on:")
    st.stop()

points, cards = [], []
for it in items:
    until = ui.local_time(pd.Series([it["pickup_deadline"]])).iloc[0]
    detail = f"{it['food']} · {it['quantity_lbs']:.0f} lbs · available until {until}"
    points.append(ui.point(f"d{it['id']}", it["site"], "donor", it["site_lat"], it["site_lon"],
                           it["site_address"], it["site_address"], "Where the food is being shared", detail))
    where = [f'<p><b>Prepared at:</b> {theme.e(it["site"])}</p>']
    donor_links = theme.maps_links(it["site"], it["site_lat"], it["site_lon"], it["site_address"])
    buttons = f'<div class="sl-meta" style="width:100%;margin:0">Directions to the donor</div>{donor_links}'
    if it["pantry"]:
        points.append(ui.point(f"p{it['id']}", it["pantry"], "pantry", it["pantry_lat"], it["pantry_lon"],
                               it["pantry_address"], it["pantry_address"], "Matched pickup pantry", detail))
        where.append(f'<p><b>Pick up at:</b> {theme.e(it["pantry"])}</p>')
        pantry_links = theme.maps_links(it["pantry"], it["pantry_lat"], it["pantry_lon"], it["pantry_address"])
        buttons = (
            '<div class="sl-meta" style="width:100%;margin:0">Directions to the pickup pantry</div>' + pantry_links
            + '<div class="sl-meta" style="width:100%;margin:.4rem 0 0">Directions to the donor</div>' + donor_links
        )
    else:
        where.append("<p><b>Pick up at:</b> still being matched to a pantry</p>")
    tags = "".join(
        f'<span class="sl-pill" style="background:#D3EEDD;color:#1F5C45;margin-right:4px">{theme.e(t)}</span>'
        for t in it["dietary_tags"]
    )
    cards.append(
        '<div class="sl-card"><div class="sl-strip" style="background:#F28C38"></div>'
        f'<span class="sl-pill" style="background:#FDE3BD;color:#B8560F">{it["quantity_lbs"]:.0f} lbs</span> {tags}'
        f'<h3>{theme.e(it["food"])}</h3>{"".join(where)}'
        f'<div class="sl-meta">Available until {until}</div><div class="sl-btns">{buttons}</div></div>'
    )

theme.section("Available now", "Tap a button to open directions in Apple Maps or Google Maps.")
theme.render(f'<div class="sl-grid" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">{"".join(cards)}</div>')

theme.section("See it on the map", "Search an address or use your location to see what's closest.")
mapview.explorer(points, title="Food near you")

notes = ui.fetch("/notifications")
if notes:
    pantry_names = {p["id"]: p["name"] for p in ui.fetch("/pantries")}
    with st.expander("Recent pantry alerts"):
        for n in reversed(notes[-5:]):
            st.write(f"**{pantry_names.get(n['pantry_id'], n['pantry_id'])}**: {n['message']}")

import pandas as pd
import streamlit as st

import theme
import ui

u = ui.user()

with st.container(key="hero"):
    left, right = st.columns([1.1, 1], vertical_alignment="center", gap="large")
    with left:
        theme.render(
            '<span class="sl-eyebrow">UN Goal 2 · Zero Hunger</span>'
            '<h1 class="sl-hero-title">Good food shouldn\'t go to waste while neighbors go hungry.</h1>'
            '<p class="sl-lead">SurplusLink connects dining halls, restaurants, and events that have extra food '
            "with the pantries and neighbors who can use it, before it spoils.</p>"
        )
        c1, c2 = st.columns([1, 1.2])
        with c1, st.container(key="cta1"):
            if u:
                dash, label = ("views/donate.py", "Donor dashboard") if u["role"] == "donor" else ("views/pickup.py", "Find food to pick up")
                st.page_link(dash, label=label, icon=":material/arrow_forward:")
            else:
                st.page_link("views/login.py", label="Get started", icon=":material/arrow_forward:")
        with c2, st.container(key="cta2"):
            st.page_link("views/find_help.py", label="Find food near me", icon=":material/location_on:")
    with right:
        theme.render(f'<img class="sl-art" src="{theme.img_uri("hero")}" alt="A basket of fresh food in a friendly neighborhood">')

theme.section("Our impact so far", "Every pound matched is a pound that feeds someone instead of filling a landfill.")
imp = ui.fetch("/impact")
theme.stats([
    (f"{imp['meals_saved']:,.0f}", "Meals saved", "#2F7D5B"),
    (f"{imp['lbs_diverted']:,.0f}", "Pounds kept out of the trash", "#E4572E"),
    (f"{imp['co2e_kg_avoided']:,.0f}", "kg of CO2e avoided", "#2E86AB"),
    (f"{imp['listings_matched']:,}", "Donations matched", "#8E5EA2"),
])

theme.section("How it works", "Three simple steps from surplus to supper.")
theme.feature_cards([
    ("icon_post", "Donors post", "Share what's left over in under a minute: what it is, how much, and when it needs to go.", "#F28C38"),
    ("icon_match", "We match", "Each listing goes to the best pantry, weighing distance, time left, dietary fit, and room to store it.", "#2F7D5B"),
    ("icon_pickup", "Neighbors pick up", "People see exactly where and when to collect fresh food, with directions in Apple or Google Maps.", "#2E86AB"),
])

theme.band(
    "Hunger is a logistics problem",
    "There is enough food. It's just often in the wrong place at the wrong time. SurplusLink closes that gap "
    "with fast matching, so surplus reaches people while it's still fresh.",
)

theme.section("What we expect to be left over", "A forecast of surplus pounds at each donor site, so pantries can plan ahead.")
days = st.slider("Days ahead", 1, 14, 7)
fc = pd.DataFrame(ui.fetch("/forecast", days=days))
wide = fc.pivot(index="date", columns="site", values="predicted_lbs")
st.line_chart(wide, color=["#2F7D5B", "#E4572E", "#2E86AB", "#8E5EA2", "#F6B93B", "#F28C38"][: wide.shape[1]])
st.caption("Predictions come from a gradient boosting model trained on synthetic data for this demo.")

import streamlit as st

import ui

st.title("📍 Find food & shelter")
st.caption("Food banks, pantries, and shelters in and around Berkeley. Hours change, so call ahead.")
st.info("Need help right now? Dial 211 to reach local food, housing, and emergency services.")

kinds = st.multiselect(
    "Show", ["food_bank", "shelter"], default=["food_bank", "shelter"], format_func=ui.KIND_LABEL.get
)
items = [r for r in ui.fetch("/resources") if r["kind"] in kinds]
ui.resource_map(items)
ui.resource_cards(items)

import streamlit as st

import ui

st.title("🤝 Give back")
st.caption("Other ways to volunteer your time or donate to fight hunger and homelessness nearby.")

kinds = st.multiselect(
    "Show", ["volunteer", "donation"], default=["volunteer", "donation"], format_func=ui.KIND_LABEL.get
)
items = [r for r in ui.fetch("/resources") if r["kind"] in kinds]
ui.resource_map(items)
ui.resource_cards(items)

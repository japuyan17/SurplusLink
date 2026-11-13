import pandas as pd
import streamlit as st

import ui

st.title("🍽️ SurplusLink")
st.subheader("Hunger isn't a food shortage problem, it's a logistics problem.")
st.write(
    "SurplusLink connects dining halls, restaurants, and events that have extra food "
    "with the pantries and neighbors who need it, in real time."
)

u = ui.user()
if u:
    if u["role"] == "donor":
        st.page_link("views/donate.py", label="Go to your donor dashboard", icon="🍱")
    else:
        st.page_link("views/pickup.py", label="Find food to pick up", icon="🛒")
else:
    st.page_link("views/login.py", label="Log in or sign up to donate or pick up food", icon="🔑")

imp = ui.fetch("/impact")
c1, c2, c3 = st.columns(3)
c1.metric("Meals saved", f"{imp['meals_saved']:,.0f}")
c2.metric("Lbs diverted", f"{imp['lbs_diverted']:,.0f}")
c3.metric("CO2e avoided (kg)", f"{imp['co2e_kg_avoided']:,.0f}")

st.subheader("How it works")
a, b, c = st.columns(3)
a.markdown("**1. Donors post**  \nShare what's left over in under a minute.")
b.markdown("**2. We match**  \nListings go to the best pantry by distance, urgency, dietary fit, and capacity.")
c.markdown("**3. Neighbors pick up**  \nPeople see where and when to collect fresh food.")

st.subheader("Predicted surplus")
days = st.slider("Days ahead", 1, 14, 7)
fc = pd.DataFrame(ui.fetch("/forecast", days=days))
st.line_chart(fc.pivot(index="date", columns="site", values="predicted_lbs"))
st.caption("Pounds of surplus per site, from a gradient boosting model trained on synthetic data.")

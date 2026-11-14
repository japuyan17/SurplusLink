from pathlib import Path

import streamlit as st

import theme
import ui

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(page_title="SurplusLink", page_icon=str(ASSETS / "logo_icon.svg"), layout="wide")
st.logo(str(ASSETS / "logo.svg"), icon_image=str(ASSETS / "logo_icon.svg"), size="large")
theme.inject()

home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
about = st.Page("views/about.py", title="About", icon=":material/info:", url_path="about")
find_help = st.Page("views/find_help.py", title="Find food & shelter", icon=":material/location_on:", url_path="find-help")
give_back = st.Page("views/community.py", title="Give back", icon=":material/volunteer_activism:", url_path="give-back")
login = st.Page("views/login.py", title="Log in / Sign up", icon=":material/login:", url_path="login")
donate = st.Page("views/donate.py", title="Donor dashboard", icon=":material/restaurant:", url_path="donate")
pickup = st.Page("views/pickup.py", title="Pickup dashboard", icon=":material/shopping_basket:", url_path="pickup")

u = ui.user()
pages = [home, about, find_help, give_back]
pages.insert(1, (donate if u["role"] == "donor" else pickup) if u else login)

with st.sidebar:
    if u:
        theme.render(
            f'<div class="sl-userbox"><b>{theme.e(u["name"])}</b><br>'
            f'{"Food donor" if u["role"] == "donor" else "Neighbor"}</div>'
        )
        st.button("Log out", on_click=ui.logout, use_container_width=True)

try:
    st.navigation(pages).run()
finally:
    theme.footer()

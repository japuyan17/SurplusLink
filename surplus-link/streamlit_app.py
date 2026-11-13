import streamlit as st

import ui

st.set_page_config(page_title="SurplusLink", page_icon="🍽️", layout="wide")

home = st.Page("views/home.py", title="Home", icon="🏠", default=True)
find_help = st.Page("views/find_help.py", title="Find food & shelter", icon="📍", url_path="find-help")
give_back = st.Page("views/community.py", title="Give back", icon="🤝", url_path="give-back")
login = st.Page("views/login.py", title="Log in / Sign up", icon="🔑", url_path="login")
donate = st.Page("views/donate.py", title="Donor dashboard", icon="🍱", url_path="donate")
pickup = st.Page("views/pickup.py", title="Pickup dashboard", icon="🛒", url_path="pickup")

u = ui.user()
pages = [home, find_help, give_back]
if not u:
    pages.append(login)
else:
    pages.insert(1, donate if u["role"] == "donor" else pickup)

with st.sidebar:
    if u:
        st.markdown(f"**{u['name']}**  \n:gray[{u['role'].title()}]")
        st.button("Log out", on_click=ui.logout)

st.navigation(pages).run()

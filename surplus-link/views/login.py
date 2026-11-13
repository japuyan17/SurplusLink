import streamlit as st

import ui

st.title("🔑 Log in")
login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

with login_tab:
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in", type="primary")
    if submitted:
        ok, data = ui.request("POST", "/auth/login", json={"email": email, "password": password})
        if ok:
            ui.login(data)
            st.rerun()
        st.error(data)

with signup_tab:
    role_label = st.radio(
        "I am a...",
        ["Donor (dining hall, restaurant, or event with surplus food)", "Neighbor looking for food"],
    )
    role = "donor" if role_label.startswith("Donor") else "recipient"
    sites = ui.fetch("/sites")
    with st.form("signup"):
        name = st.text_input("Name")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password (8+ characters)", type="password", key="signup_password")
        site = None
        if role == "donor":
            site = st.selectbox("Your location", sites, format_func=lambda s: s["name"])
        created = st.form_submit_button("Create account", type="primary")
    if created:
        ok, data = ui.request("POST", "/auth/register", json={
            "name": name, "email": new_email, "password": new_password,
            "role": role, "site_id": site["id"] if site else None,
        })
        if ok:
            ui.login(data)
            st.rerun()
        st.error(data)

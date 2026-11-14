import streamlit as st

import theme
import ui

theme.page_header("Welcome", "Create a free account to donate surplus food or find food near you.", "icon_heart")

art, forms = st.columns([1, 1.2], gap="large", vertical_alignment="center")
with art:
    theme.render(f'<img class="sl-art" src="{theme.img_uri("hero")}" alt="A basket of fresh food in a friendly neighborhood">')
    theme.render('<div class="sl-quote">Share what you have. Find what you need. It takes about a minute.</div>')

with forms:
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

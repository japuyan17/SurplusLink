import os

import pandas as pd
import requests
import streamlit as st

import theme

API = os.getenv("API_URL", "http://127.0.0.1:8000")
LOCAL_TZ = "America/Los_Angeles"
TAGS = ["vegetarian", "vegan", "halal", "gluten-free", "produce", "baked goods", "prepared meals"]


def user() -> dict | None:
    return st.session_state.get("user")


def login(data: dict) -> None:
    st.session_state["token"], st.session_state["user"] = data["token"], data["user"]


def logout() -> None:
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)


def request(method: str, path: str, **kwargs) -> tuple[bool, object]:
    """Returns (ok, data). When not ok, data is an error message."""
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    try:
        r = requests.request(method, f"{API}{path}", headers=headers, timeout=10, **kwargs)
    except requests.RequestException:
        return False, f"Can't reach the API at {API}. Start it with: uvicorn app.main:app --reload"
    if r.status_code == 401 and st.session_state.get("token"):
        logout()
        return False, "Your session expired. Please log in again."
    if r.ok:
        return True, r.json()
    try:
        detail = r.json().get("detail", r.text)
    except ValueError:
        detail = r.text
    if isinstance(detail, list):
        detail = "; ".join(d.get("msg", "invalid input") for d in detail)
    return False, detail


def fetch(path: str, **params):
    ok, data = request("GET", path, params=params)
    if not ok:
        st.error(data)
        st.stop()
    return data


def require_login(role: str | None = None) -> dict:
    u = user()
    if not u:
        theme.empty_state("Please log in", "Log in or create a free account to see this page.", "icon_heart")
        st.page_link("views/login.py", label="Log in or sign up", icon=":material/login:")
        st.stop()
    if role and u["role"] != role:
        theme.empty_state("This page is for " + role + "s", "Switch accounts to see this dashboard.", "icon_heart")
        st.stop()
    return u


def local_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True).dt.tz_convert(LOCAL_TZ).dt.strftime("%a %I:%M %p")


def point(id, name, kind, lat, lon, address="", nav_query="", description="", extra="", contact="", url="") -> dict:
    label, strong, soft = theme.kind_style(kind)
    return {
        "id": id, "name": name, "kind": kind, "kind_label": label, "color": strong, "soft": soft,
        "lat": lat, "lon": lon, "address": address, "nav_query": nav_query,
        "description": description, "extra": extra, "contact": contact, "url": url,
    }


def resource_points(items: list[dict]) -> list[dict]:
    """Only places with a real street address go on the map."""
    return [
        point(f"r{r['id']}", r["name"], r["kind"], r["lat"], r["lon"], r["address"], r["nav_address"],
              r["description"], r["how_to_help"], r["contact"], r["url"])
        for r in items if r["nav_address"]
    ]

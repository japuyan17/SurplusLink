import os

import pandas as pd
import requests
import streamlit as st

API = os.getenv("API_URL", "http://127.0.0.1:8000")
LOCAL_TZ = "America/Los_Angeles"
TAGS = ["vegetarian", "vegan", "halal", "gluten-free", "produce", "baked goods", "prepared meals"]
KIND_LABEL = {"food_bank": "Food bank", "shelter": "Shelter", "volunteer": "Volunteer", "donation": "Donate"}
KIND_COLOR = {"food_bank": "#2e86ab", "shelter": "#8e5ea2", "volunteer": "#3cb371", "donation": "#e4572e"}


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
        st.info("Please log in to see this page.")
        st.stop()
    if role and u["role"] != role:
        st.warning(f"This page is for {role}s.")
        st.stop()
    return u


def local_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True).dt.tz_convert(LOCAL_TZ).dt.strftime("%a %I:%M %p")


def directions_url(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"


def show_map(points: list[dict]) -> None:
    """points: dicts with lat, lon, color (hex)."""
    if points:
        st.map(pd.DataFrame(points).assign(size=60), color="color", size="size")


def resource_map(items: list[dict]) -> None:
    show_map([{"lat": r["lat"], "lon": r["lon"], "color": KIND_COLOR[r["kind"]]} for r in items])
    st.caption("  ".join(f":gray[●] {KIND_LABEL[k]}" for k in sorted({r["kind"] for r in items})))


def resource_cards(items: list[dict]) -> None:
    for r in items:
        with st.container(border=True):
            st.markdown(f"**{r['name']}** · {KIND_LABEL[r['kind']]}")
            st.write(r["description"])
            if r["how_to_help"]:
                st.markdown(f"**How to help:** {r['how_to_help']}")
            st.caption(" · ".join(x for x in (r["address"], r["contact"]) if x))
            c1, c2, _ = st.columns([1, 1, 4])
            c1.link_button("Directions", directions_url(r["lat"], r["lon"]))
            if r["url"]:
                c2.link_button("More info", r["url"])

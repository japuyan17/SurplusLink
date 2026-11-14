import base64
from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st

ASSETS = Path(__file__).parent / "assets"

# kind -> (label, strong color, soft color)
KINDS = {
    "food_bank": ("Food bank", "#2E86AB", "#D2EAF7"),
    "shelter": ("Shelter", "#8E5EA2", "#EBDCF3"),
    "volunteer": ("Volunteer", "#2F7D5B", "#D3EEDD"),
    "donation": ("Donate", "#E4572E", "#FBDCD2"),
    "donor": ("Food donor", "#F28C38", "#FDE3BD"),
    "pantry": ("Pickup pantry", "#2E86AB", "#D2EAF7"),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito:wght@400;600;700;800&display=swap');

:root {
  --green:#1F5C45; --leaf:#2F7D5B; --mint:#D3EEDD; --sun:#F6B93B; --cream:#FFF8EC;
  --sand:#F3E9D2; --tomato:#E4572E; --sky:#2E86AB; --plum:#8E5EA2; --ink:#2B3A33;
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp div[data-baseweb] {
  font-family: 'Nunito', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp h1, .stApp h2, .stApp h3, .sl-display {
  font-family: 'Fraunces', Georgia, 'Times New Roman', serif !important;
  color: var(--green); letter-spacing: -0.01em;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }

/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1F5C45 0%, #2F7D5B 100%); }
[data-testid="stSidebar"] * { color: var(--cream); }
[data-testid="stSidebarNavLink"] {
  border-radius: 16px; padding: 0.7rem 1rem; margin-bottom: 0.2rem;
}
[data-testid="stSidebarNavLink"] span, [data-testid="stSidebarNavLink"] p {
  font-size: 1.3rem !important; font-weight: 700 !important; line-height: 1.3;
}
[data-testid="stSidebarNavLink"]:hover { background: rgba(255,248,236,.14); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: var(--sun); }
[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] p { color: var(--green) !important; }
[data-testid="stSidebar"] .sl-userbox {
  background: rgba(255,248,236,.14); border-radius: 18px; padding: 0.9rem 1rem; margin: 0.5rem 0 0.8rem;
}
[data-testid="stSidebar"] .sl-userbox b { font-size: 1.15rem; }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  background: var(--cream); border: 0; border-radius: 999px; font-weight: 800;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] * { color: var(--green) !important; }

/* buttons */
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"],
[data-testid="stBaseLinkButton-secondary"], [data-testid="stBaseLinkButton-primary"],
[data-testid="stPageLink-NavLink"] {
  border-radius: 999px !important; font-weight: 800; padding: 0.55rem 1.4rem;
}
[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button {
  background: var(--tomato); border-color: var(--tomato); color: #fff;
  box-shadow: 0 6px 16px rgba(228,87,46,.28);
}
[data-testid="stBaseButton-primary"]:hover { background: #cf4620; border-color: #cf4620; color: #fff; }

/* forms and inputs */
[data-testid="stForm"] {
  background: #fff; border: 0; border-radius: 24px; padding: 1.6rem;
  box-shadow: 0 10px 30px rgba(31,92,69,.10);
}
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] { border-radius: 14px !important; }
[data-testid="stTabs"] [role="tab"] { font-weight: 800; font-size: 1.05rem; }
[data-testid="stDataFrame"] { border-radius: 18px; overflow: hidden; box-shadow: 0 6px 20px rgba(31,92,69,.08); }
[data-testid="stExpander"] { background: #fff; border: 0 !important; border-radius: 20px; box-shadow: 0 6px 20px rgba(31,92,69,.08); }
[data-testid="stExpander"] summary { font-weight: 800; }

/* hero */
.st-key-hero {
  background: linear-gradient(135deg, #BFE6F5 0%, #FFF1D6 55%, #FDE3BD 100%);
  border-radius: 36px; padding: 2.4rem 2.6rem; overflow: hidden;
}
.sl-eyebrow {
  display: inline-block; background: var(--green); color: var(--cream); border-radius: 999px;
  padding: 0.3rem 0.9rem; font-weight: 800; font-size: 0.85rem; letter-spacing: .04em; text-transform: uppercase;
}
.sl-hero-title { font-size: clamp(2.2rem, 4.4vw, 3.6rem); line-height: 1.08; margin: 1rem 0 0.8rem; }
.sl-lead { font-size: 1.2rem; line-height: 1.55; max-width: 34rem; }
.sl-art { width: 100%; display: block; border-radius: 28px; }

/* page header */
.sl-pagehead {
  display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;
  background: linear-gradient(120deg, #1F5C45, #2F7D5B); color: var(--cream);
  border-radius: 28px; padding: 1.8rem 2.2rem; margin-bottom: 1.6rem;
}
.sl-pagehead h1 { color: var(--cream) !important; margin: 0 0 .3rem; font-size: 2.3rem; padding: 0; }
.sl-pagehead p { margin: 0; font-size: 1.1rem; opacity: .92; max-width: 38rem; }
.sl-pagehead img { width: 84px; height: 84px; flex: none; }

/* sections */
.sl-section { margin: 3rem 0 1.2rem; }
.sl-section h2 { font-size: 2rem; margin: 0 0 .3rem; padding: 0; }
.sl-section p { font-size: 1.1rem; margin: 0; max-width: 40rem; }

/* cards */
.sl-grid { display: grid; gap: 1.2rem; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.sl-card {
  background: #fff; border-radius: 24px; padding: 1.4rem 1.5rem; position: relative; overflow: hidden;
  box-shadow: 0 10px 30px rgba(31,92,69,.10);
}
.sl-card h3 { font-size: 1.3rem; margin: .6rem 0 .4rem; padding: 0; }
.sl-card p { margin: 0 0 .6rem; line-height: 1.5; }
.sl-card img.sl-icon { width: 64px; height: 64px; }
.sl-card .sl-strip { position: absolute; inset: 0 0 auto 0; height: 8px; }
.sl-stat { border-radius: 24px; padding: 1.3rem 1.5rem; color: #fff; }
.sl-stat b { display: block; font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; line-height: 1.1; }
.sl-stat span { font-size: 1rem; font-weight: 700; opacity: .95; }
.sl-pill {
  display: inline-block; border-radius: 999px; padding: .2rem .75rem; font-size: .82rem; font-weight: 800;
}
.sl-meta { color: #5d6b64; font-size: .95rem; margin: .2rem 0 .8rem; }
.sl-btns { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .6rem; }
a.sl-btn {
  display: inline-block; padding: .5rem 1rem; border-radius: 999px; font-weight: 800; font-size: .92rem;
  text-decoration: none !important; background: var(--green); color: var(--cream) !important;
}
a.sl-btn.alt { background: var(--sand); color: var(--green) !important; }
a.sl-btn.hot { background: var(--tomato); color: #fff !important; }
a.sl-btn:hover { filter: brightness(1.08); }

/* bands */
.sl-band {
  background: var(--green); color: var(--cream); border-radius: 32px; padding: 2.2rem 2.6rem; margin: 3rem 0 1rem;
}
.sl-band h2 { color: var(--cream) !important; margin: 0 0 .5rem; font-size: 2rem; padding: 0; }
.sl-band p { font-size: 1.1rem; line-height: 1.6; max-width: 46rem; margin: 0; }
.sl-quote {
  background: #fff; border-left: 8px solid var(--sun); border-radius: 18px; padding: 1.1rem 1.4rem;
  font-size: 1.15rem; margin: 1rem 0;
}
.sl-footer {
  background: var(--green); color: var(--cream); border-radius: 32px; padding: 2rem 2.4rem; margin-top: 4rem;
  display: flex; flex-wrap: wrap; gap: 2rem; justify-content: space-between; align-items: center;
}
.sl-footer p { margin: .2rem 0; opacity: .9; }
.sl-footer .sl-display { color: var(--cream) !important; font-size: 1.6rem; font-weight: 700; }
.sl-footer a { color: var(--sun) !important; font-weight: 800; }
.sl-empty {
  text-align: center; background: #fff; border-radius: 28px; padding: 2.5rem 1.5rem;
  box-shadow: 0 10px 30px rgba(31,92,69,.10);
}
.sl-empty img { width: 96px; height: 96px; }

/* sidebar labels wrap instead of truncating */
[data-testid="stSidebarNavLink"] * {
  white-space: normal !important; overflow: visible !important; text-overflow: clip !important;
}
[data-testid="stSidebar"] button p { font-size: 1.05rem; font-weight: 800; }

/* hero call-to-action buttons */
.st-key-cta1 [data-testid="stPageLink-NavLink"], .st-key-cta2 [data-testid="stPageLink-NavLink"] {
  justify-content: center; padding: 0.75rem 1rem; box-shadow: 0 8px 20px rgba(31,92,69,.18);
}
.st-key-cta1 [data-testid="stPageLink-NavLink"] *, .st-key-cta2 [data-testid="stPageLink-NavLink"] * { white-space: nowrap !important; }
.st-key-cta1 [data-testid="stPageLink-NavLink"] { background: var(--tomato); }
.st-key-cta2 [data-testid="stPageLink-NavLink"] { background: #fff; }
.st-key-cta1 [data-testid="stPageLink-NavLink"] *, .st-key-cta2 [data-testid="stPageLink-NavLink"] * {
  font-size: 1.1rem !important; font-weight: 800 !important;
}
.st-key-cta1 [data-testid="stPageLink-NavLink"] * { color: #fff !important; }
.st-key-cta2 [data-testid="stPageLink-NavLink"] * { color: var(--green) !important; }
.st-key-cta1 [data-testid="stPageLink-NavLink"]:hover { background: #cf4620; }

@media (max-width: 760px) {
  .st-key-hero { padding: 1.4rem; }
  .sl-pagehead { flex-direction: column; align-items: flex-start; padding: 1.4rem; }
  .sl-band, .sl-footer { padding: 1.5rem; }
}
"""


def inject() -> None:
    st.html(f"<style>{CSS}</style>")


def img_uri(name: str) -> str:
    data = base64.b64encode((ASSETS / f"{name}.svg").read_bytes()).decode()
    return f"data:image/svg+xml;base64,{data}"


def e(text) -> str:
    return escape(str(text), quote=True)


def kind_style(kind: str) -> tuple[str, str, str]:
    return KINDS.get(kind, ("Place", "#2F7D5B", "#D3EEDD"))


def render(markup: str) -> None:
    st.html(markup)


def page_header(title: str, subtitle: str, icon: str = "icon_heart") -> None:
    render(
        f'<div class="sl-pagehead"><div><h1>{e(title)}</h1><p>{e(subtitle)}</p></div>'
        f'<img src="{img_uri(icon)}" alt=""></div>'
    )


def section(title: str, blurb: str = "") -> None:
    p = f"<p>{e(blurb)}</p>" if blurb else ""
    render(f'<div class="sl-section"><h2>{e(title)}</h2>{p}</div>')


def stats(items: list[tuple[str, str, str]]) -> None:
    """items: (value, label, color)"""
    cells = "".join(
        f'<div class="sl-stat" style="background:{c}"><b>{e(v)}</b><span>{e(l)}</span></div>' for v, l, c in items
    )
    render(f'<div class="sl-grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">{cells}</div>')


def feature_cards(items: list[tuple[str, str, str, str]], min_width: int = 260) -> None:
    """items: (icon, title, text, strip color)"""
    cells = "".join(
        f'<div class="sl-card"><div class="sl-strip" style="background:{c}"></div>'
        f'<img class="sl-icon" src="{img_uri(i)}" alt=""><h3>{e(t)}</h3><p>{e(x)}</p></div>'
        for i, t, x, c in items
    )
    render(f'<div class="sl-grid" style="grid-template-columns:repeat(auto-fit,minmax({min_width}px,1fr))">{cells}</div>')


def band(title: str, text: str) -> None:
    render(f'<div class="sl-band"><h2>{e(title)}</h2><p>{e(text)}</p></div>')


def empty_state(title: str, text: str, icon: str = "icon_heart") -> None:
    render(f'<div class="sl-empty"><img src="{img_uri(icon)}" alt=""><h3>{e(title)}</h3><p>{e(text)}</p></div>')


def footer() -> None:
    render(
        '<div class="sl-footer"><div><div class="sl-display">SurplusLink</div>'
        "<p>Good food belongs on a plate, not in a bin.</p>"
        "<p>Built for the GM#11 hackathon · UN Sustainable Development Goal 2: Zero Hunger</p></div>"
        '<div><p>Need food or shelter right now?</p><p>Dial <a href="tel:211">211</a> for local help, any time.</p></div></div>'
    )


def maps_links(name: str, lat: float, lon: float, address: str = "") -> str:
    """Apple Maps and Google Maps buttons. Uses the street address when known: it is more accurate than coordinates."""
    dest = quote(address) if address else f"{lat},{lon}"
    apple = f"https://maps.apple.com/?daddr={dest}&q={quote(name)}"
    google = f"https://www.google.com/maps/dir/?api=1&destination={dest}"
    return (
        f'<a class="sl-btn" href="{apple}" target="_blank" rel="noopener">Apple Maps</a>'
        f'<a class="sl-btn" href="{google}" target="_blank" rel="noopener">Google Maps</a>'
    )


def resource_cards(items: list[dict]) -> None:
    cells = []
    for r in items:
        label, strong, soft = kind_style(r["kind"])
        nav = maps_links(r["name"], r["lat"], r["lon"], r["nav_address"]) if r["nav_address"] else ""
        more = f'<a class="sl-btn alt" href="{e(r["url"])}" target="_blank" rel="noopener">More info</a>' if r["url"] else ""
        meta = " · ".join(e(x) for x in (r["address"], r["contact"]) if x)
        how = f"<p><b>How to help:</b> {e(r['how_to_help'])}</p>" if r["how_to_help"] else ""
        cells.append(
            f'<div class="sl-card"><div class="sl-strip" style="background:{strong}"></div>'
            f'<span class="sl-pill" style="background:{soft};color:{strong}">{label}</span>'
            f'<h3>{e(r["name"])}</h3><p>{e(r["description"])}</p>{how}'
            f'<div class="sl-meta">{meta}</div><div class="sl-btns">{nav}{more}</div></div>'
        )
    render(f'<div class="sl-grid" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">{"".join(cells)}</div>')

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

# Ensure the local package is importable regardless of current working directory
sys.path.insert(0, os.path.dirname(__file__))

from shopimpact import core


st.set_page_config(page_title="ShopImpact", layout="wide")

# --- Safe secrets fallback -------------------------------------------------
# Some Streamlit apps access `st.secrets` and Streamlit raises
# StreamlitSecretNotFoundError when no secrets.toml exists. Provide a
# resilient accessor so the app and other scripts won't crash in that case.
try:
    _STREAMLIT_SECRETS = st.secrets
except Exception:
    class _EmptySecrets(dict):
        def get(self, key, default=None):
            return default

    _STREAMLIT_SECRETS = _EmptySecrets()


def get_secret(key, default=None):
    """Return a secret value or `default` if secrets aren't available."""
    try:
        return _STREAMLIT_SECRETS.get(key, default)
    except Exception:
        return default

# Example usage: API_BASE = get_secret("api_base", "http://localhost:8000/api")
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# API integration (safe defaults)
API_BASE = get_secret("api_base", "http://localhost:8000/api")

import urllib.request as _urlreq
import urllib.error as _urlerr
import json as _json


def api_get(path: str, timeout: int = 2):
    """Make a safe GET to the API and return parsed JSON or None on failure."""
    base = API_BASE.rstrip("/")
    url = f"{base}/{path.lstrip('/') }"
    try:
        with _urlreq.urlopen(url, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return _json.load(resp)
    except _urlerr.URLError as e:
        # Connection refused, timeout, DNS error, etc.
        return None
    except Exception:
        return None


def check_api_and_notify():
    """Check API /status and show a small status indicator in UI without failing the app."""
    status = api_get("status")
    if status is None:
        st.warning("Backend API not reachable at {} — some features may be disabled.".format(API_BASE))
        return False
    else:
        st.success("Backend API reachable — status: {}".format(status))
        return True


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def ensure_session():
    if "purchases" not in st.session_state:
        st.session_state.purchases = load_data()


def add_purchase(entry):
    st.session_state.purchases.append(entry)
    save_data(st.session_state.purchases)


def draw_leaf_badge(saved_co2: float = 0.0):
    # simple turtle-style badge using matplotlib
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # draw a stylized leaf
    leaf = patches.Ellipse((5, 5.5), 6, 3.5, angle=25, facecolor="#2E8B57", edgecolor="#145A32", linewidth=3)
    stem = patches.FancyBboxPatch((4.7, 3.2), 0.6, 2.2, boxstyle="round,pad=0.2", facecolor="#6B8E23", edgecolor="#3A5F0B")
    ax.add_patch(leaf)
    ax.add_patch(stem)

    txt = f"Saved\n{saved_co2:.2f} kgCO2"
    ax.text(5, 1.6, txt, ha="center", va="center", fontsize=10, weight="bold", color="#2F4F4F")

    return fig


ensure_session()

st.title("🌱 ShopImpact — Make Shopping Greener")
st.markdown("""
An inviting companion that estimates CO₂ for purchases and nudges greener choices.
Earthy palette, big fonts, and playful badges make sustainability joyful.
""")

with st.sidebar:
    st.header("Log a planned purchase")
    categories = sorted(list(core.DEFAULT_MULTIPLIERS.keys())) + ["Other"]
    category = st.selectbox("Category", categories)
    brand = st.text_input("Brand (optional)")
    price = st.number_input("Price (USD)", min_value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    note = st.text_area("Note (optional)")
    add = st.button("Add purchase")

    st.markdown("---")
    st.caption("Data persisted locally in `data.json` for this demo.")

if add:
    multiplier = core.get_multiplier_for_category(category)
    entry = core.record_to_entry(category=category, brand=brand or "", price=price, quantity=quantity, note=note)
    add_purchase(entry)
    st.sidebar.success(f"Logged {category} — {entry['co2']:.2f} kgCO₂")

df = pd.DataFrame(st.session_state.purchases)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live monthly impact")
    if df.empty:
        st.info("No purchases yet — log one on the left to see your impact.")
    else:
        # parse timestamps
        df["ts"] = pd.to_datetime(df["ts"])
        df["month"] = df["ts"].dt.to_period("M").astype(str)

        # monthly totals
        monthly = df.groupby("month")["co2"].sum().sort_index()
        st.metric("This month total (kg CO₂)", f"{monthly.iloc[-1]:.2f}")

        # matplotlib bar chart
        fig, ax = plt.subplots(figsize=(8, 3))
        monthly.plot(kind="bar", color="#8FBF8F", ax=ax)
        ax.set_ylabel("kg CO₂")
        ax.set_title("Monthly CO₂ by purchases")
        st.pyplot(fig)

        st.subheader("Recent purchases")
        st.dataframe(df.sort_values(by="ts", ascending=False).head(10)[["ts", "category", "brand", "price", "quantity", "co2"]])

with col2:
    st.subheader("Suggestions & Badges")
    selected_cat = category if category != "Other" else (df.iloc[-1]["category"] if not df.empty else "Groceries")
    alts = core.suggest_alternatives(selected_cat)
    if alts:
        st.markdown(f"### Greener options for {selected_cat}")
        for alt in alts:
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**{alt['product']}** — {alt['brand']}")
                st.caption(f"Estimated {alt['mult']:.2f} kgCO₂ per USD")
            with cols[1]:
                if st.button(f"Choose {alt['product']}", key=f"alt_{alt['product']}"):
                    # log a mock purchase where user chooses greener alternative
                    price_example = 10.0
                    qty = 1
                    mult = alt["mult"]
                    co2_old = core.get_multiplier_for_category(selected_cat) * price_example * qty
                    co2_new = mult * price_example * qty
                    saved = max(0.0, co2_old - co2_new)
                    entry = core.record_to_entry(category=selected_cat, brand=alt["brand"], price=price_example, quantity=qty, note=f"Chosen alternative: {alt['product']}")
                    # override multiplier/co2 to reflect alternative (for demo clarity)
                    entry["multiplier"] = float(mult)
                    entry["co2"] = float(co2_new)
                    add_purchase(entry)
                    st.success(f"Nice! Saved {saved:.2f} kgCO₂ vs typical option.")
                    # draw badge
                    fig_badge = draw_leaf_badge(saved)
                    st.pyplot(fig_badge)
    else:
        st.info("No curated alternatives for this category yet — try other categories.")

st.markdown("---")
st.caption("ShopImpact demo — multipliers are illustrative, not scientific. Built with Streamlit.")

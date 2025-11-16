import streamlit as st
from ..config import CARD_BACKGROUND, TEXT_COLOR, MUTED_TEXT_COLOR, SECONDARY_COLOR, DANGER_COLOR, ACCENT_COLOR


def kpi_card(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="
            background-color:{CARD_BACKGROUND};
            padding:1rem 1.2rem;
            border-radius:0.8rem;
            border:1px solid #263238;
            ">
            <div style="font-size:0.8rem;color:{MUTED_TEXT_COLOR};text-transform:uppercase;">{title}</div>
            <div style="font-size:1.6rem;font-weight:600;color:{TEXT_COLOR};margin-top:0.2rem;">{value}</div>
            <div style="font-size:0.8rem;color:{MUTED_TEXT_COLOR};margin-top:0.2rem;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def participant_progress(current: int, max_participants: int):
    ratio = current / max_participants if max_participants > 0 else 0
    percent = int(ratio * 100)

    st.write(f"**Aforo:** {current} / {max_participants} participantes ({percent}%)")
    st.progress(ratio)


def status_badge(status: str):
    status = status.lower()
    color = "#546E7A"
    if status in ("open", "scheduled"):
        color = SECONDARY_COLOR
    elif status in ("expired", "failed"):
        color = DANGER_COLOR
    elif status in ("adjudicated", "complete"):
        color = ACCENT_COLOR

    st.markdown(
        f"""
        <span style="
            background-color:{color};
            padding:0.25rem 0.6rem;
            border-radius:999px;
            font-size:0.7rem;
            color:#000000;
            text-transform:uppercase;
            ">
            {status}
        </span>
        """,
        unsafe_allow_html=True,
    )

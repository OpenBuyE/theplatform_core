import streamlit as st
from ..config import APP_NAME, APP_VERSION, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR

def setup_page():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="💠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS básico para el branding
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        }}
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}
        .cab-logo {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {PRIMARY_COLOR};
        }}
        .cab-subtitle {{
            font-size: 0.85rem;
            color: #B0BEC5;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="cab-logo">CompraAbierta Finance PRO</div>', unsafe_allow_html=True)
        st.markdown('<div class="cab-subtitle">Panel Operador / OU — The Platform Core</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:right;color:#B0BEC5;'>v{APP_VERSION}</div>", unsafe_allow_html=True)


def render_sidebar() -> str:
    st.sidebar.markdown("### 📊 Navegación")

    choice = st.sidebar.radio(
        "Selecciona módulo",
        [
            "Parque de Sesiones",
            "Sesiones Activas",
            "Cadenas",
            "Programadas",
            "Standby",
            "Participantes",
            "Adjudicaciones",
            "OU Global",
            "Configuración",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Operador:** ES / PT / FR (MVP manual)")
    return choice

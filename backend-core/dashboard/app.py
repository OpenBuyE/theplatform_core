import streamlit as st
from dashboard.ui.layout import setup_page, render_header, render_sidebar
from dashboard.views.park_sessions import render_park_sessions
from dashboard.views.active_sessions import render_active_sessions
from dashboard.views.chains import render_chains
# (cuando los tengas): from .views.scheduled import render_scheduled
# ...

def main():
    setup_page()
    render_header()
    choice = render_sidebar()

    if choice == "Parque de Sesiones":
        render_park_sessions()
    elif choice == "Sesiones Activas":
        render_active_sessions()
    elif choice == "Cadenas":
        render_chains()
    elif choice == "Programadas":
        st.warning("Vista 'Programadas' aún en desarrollo.")
    elif choice == "Standby":
        st.warning("Vista 'Standby' aún en desarrollo.")
    elif choice == "Participantes":
        st.warning("Vista 'Participantes' aún en desarrollo.")
    elif choice == "Adjudicaciones":
        st.warning("Vista 'Adjudicaciones' aún en desarrollo.")
    elif choice == "OU Global":
        st.warning("Vista 'OU Global' aún en desarrollo.")
    elif choice == "Configuración":
        st.info("Configuración general del panel (pendiente).")

if __name__ == "__main__":
    main()

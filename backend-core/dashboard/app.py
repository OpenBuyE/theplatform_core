import streamlit as st

# 🟩 IMPORTS ABSOLUTOS (CORRECTOS)
from dashboard.ui.layout import setup_page, render_header, render_sidebar
from dashboard.views.park_sessions import render_park_sessions
from dashboard.views.active_sessions import render_active_sessions
from dashboard.views.chains import render_chains


def main():
    # Configuración base de la página
    setup_page()

    # Renderizar header y sidebar
    render_header()
    menu_option = render_sidebar()

    # Navegación
    if menu_option == "Parque de Sesiones":
        render_park_sessions()

    elif menu_option == "Sesiones Activas":
        render_active_sessions()

    elif menu_option == "Cadenas de Sesiones":
        render_chains()

    else:
        st.write("Selecciona una opción en el menú lateral.")


if __name__ == "__main__":
    main()


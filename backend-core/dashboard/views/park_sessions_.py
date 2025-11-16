import streamlit as st
from services.database import DatabaseService
from ..ui.components import kpi_card, status_badge
from ..config import MUTED_TEXT_COLOR


def render_park_sessions():
    st.markdown("## 📦 Parque de Sesiones (sessions_pool)")

    db = DatabaseService()
    result = db.fetch_all("sessions_pool")
    rows = result.data or []

    # Filtros
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        operator_filter = st.selectbox("Operador", ["Todos", "ES", "PT", "FR"])
    with col_f2:
        type_filter = st.selectbox("Tipo", ["Todos", "scheduled", "chain", "standby", "manual"])
    with col_f3:
        chain_filter = st.text_input("Cadena (chain_group_id)", "")
    with col_f4:
        product_filter = st.text_input("Producto (product_id)", "")

    filtered = []
    for r in rows:
        if operator_filter != "Todos" and r.get("operator_code") != operator_filter:
            continue
        if type_filter != "Todos" and r.get("type") != type_filter:
            continue
        if chain_filter and (r.get("chain_group_id") or "") != chain_filter:
            continue
        if product_filter and product_filter not in (r.get("product_id") or ""):
            continue
        filtered.append(r)

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Total plantillas en parque", str(len(rows)))
    with col2:
        kpi_card("Visible tras filtros", str(len(filtered)))
    with col3:
        chains = len({r.get("chain_group_id") for r in rows if r.get("chain_group_id")})
        kpi_card("Cadenas configuradas", str(chains))

    st.markdown("---")

    if not filtered:
        st.info("No hay resultados con los filtros actuales.")
        return

    for row in filtered:
        with st.expander(f"{row.get('description') or row['product_id']} — {row['operator_code']}"):
            col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
            with col_a:
                st.write(f"**Producto:** `{row['product_id']}`")
                st.write(f"**Cadena:** `{row.get('chain_group_id')}`  •  índice: `{row.get('chain_index')}`")
                st.write(f"**Tipo:** `{row.get('type')}`")
                st.write(f"<span style='color:{MUTED_TEXT_COLOR};font-size:0.8rem;'>ID pool: {row['id']}</span>", unsafe_allow_html=True)
            with col_b:
                st.write(f"**Operador:** {row['operator_code']}")
                st.write(f"**Aforo base:** {row['max_participants']} pax")
                st.write(f"**Importe por pax:** {row['amount']} €")
            with col_c:
                start_ts = row.get("start_timestamp")
                st.write("**Inicio previsto:**")
                st.write(start_ts or "—")
            with col_d:
                st.write("**Acciones:**")
                st.button("Activar como sesión ahora", key=f"activate_{row['id']}")
                st.button("Clonar plantilla", key=f"clone_{row['id']}")

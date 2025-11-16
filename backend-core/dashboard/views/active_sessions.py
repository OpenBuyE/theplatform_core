import streamlit as st
from services.database import DatabaseService
from ..ui.components import kpi_card, participant_progress, status_badge
from ..config import MUTED_TEXT_COLOR


def _count_participants_for_session(db: DatabaseService, session_id: str) -> int:
    result = db.fetch_by_field("participants", "session_id", session_id)
    return len(result.data or [])


def render_active_sessions():
    st.markdown("## 🔵 Sesiones Activas y en Curso (sessions)")

    db = DatabaseService()
    result = db.fetch_all("sessions")
    rows = result.data or []

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        operator_filter = st.selectbox("Operador", ["Todos", "ES", "PT", "FR"])
    with col_f2:
        status_filter = st.selectbox("Estado", ["Todos", "open", "complete", "adjudicated", "expired", "closed"])
    with col_f3:
        chain_filter = st.text_input("Cadena (chain_group_id)", "")

    filtered = []
    for r in rows:
        if operator_filter != "Todos" and r.get("operator_code") != operator_filter:
            continue
        if status_filter != "Todos" and r.get("status") != status_filter:
            continue
        if chain_filter and (r.get("chain_group_id") or "") != chain_filter:
            continue
        filtered.append(r)

    # KPIs
    total_open = sum(1 for r in rows if r.get("status") == "open")
    total_adjudicated = sum(1 for r in rows if r.get("status") == "adjudicated")
    total_expired = sum(1 for r in rows if r.get("status") == "expired")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Sesiones abiertas", str(total_open))
    with col2:
        kpi_card("Sesiones adjudicadas", str(total_adjudicated))
    with col3:
        kpi_card("Sesiones caducadas", str(total_expired))

    st.markdown("---")

    if not filtered:
        st.info("No hay sesiones con los filtros actuales.")
        return

    for row in filtered:
        session_id = row["id"]
        current_pax = _count_participants_for_session(db, session_id)
        max_pax = row["max_participants"]

        with st.expander(f"{row['product_id']} — {row.get('chain_group_id')}.{row.get('chain_index')} — {row['operator_code']}"):
            col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])

            with col_a:
                st.write(f"**Producto:** `{row['product_id']}`")
                st.write(f"**Operador:** {row['operator_code']}")
                st.write(f"**Cadena:** `{row.get('chain_group_id')}` • índice: `{row.get('chain_index')}`")
                st.write(f"<span style='color:{MUTED_TEXT_COLOR};font-size:0.8rem;'>Sesión ID: {session_id}</span>", unsafe_allow_html=True)

            with col_b:
                st.write(f"**Estado técnico:**")
                status_badge(row.get("status", "unknown"))
                st.write("")
                st.write(f"**OU status:** `{row.get('ou_status')}`")
                st.write(f"**Settlement:** `{row.get('settlement_status')}`")

            with col_c:
                st.write("**Aforo y progreso:**")
                participant_progress(current_pax, max_pax)
                st.write(f"**Importe pax:** {row['amount']} €")

            with col_d:
                st.write("**Tiempos:**")
                st.write(f"Creación: {row.get('created_at')}")
                st.write(f"Caducidad: {row.get('expiry_timestamp')}")
                st.write(f"Cierre: {row.get('closing_timestamp') or '—'}")
                st.write("")
                st.write("**Acciones:**")
                st.button("Ver participantes", key=f"view_part_{session_id}")
                st.button("Ver adjudicación", key=f"view_adj_{session_id}")
                st.button("Forzar cierre", key=f"force_close_{session_id}")

"""
Page: Upload — File ingestion with validation, preview, and status.
"""
import streamlit as st
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from services.ingestion import validate_file, ingest_file
from services.database import get_upload_history
from services.google_sheets import sync_all
from config.settings import GOOGLE_SHEETS_ENABLED


def render_upload():
    render_header(
        "Cargar Datos",
        "Importa archivos Excel con datos de inventario y exceso"
    )

    # Upload zone
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Arrastra o selecciona un archivo Excel (.xlsx)",
        type=["xlsx", "xls"],
        help="El archivo debe contener las hojas: 12 Meses, 6 Meses, o equivalentes",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # Validate
            is_valid, msg, sheets = validate_file(tmp_path)

            if is_valid:
                st.success(msg)

                # Show available sheets
                st.markdown("**Hojas detectadas:**")
                selected_sheets = []
                for sheet in sheets:
                    if st.checkbox(f"📄 {sheet}", value=True, key=f"sheet_{sheet}"):
                        selected_sheets.append(sheet)

                if selected_sheets:
                    if st.button("🚀 Procesar Archivo", type="primary", use_container_width=True):
                        with st.spinner("Procesando archivo..."):
                            result = ingest_file(
                                tmp_path,
                                uploaded_file.name,
                                sheets=selected_sheets,
                            )

                        if result["success"]:
                            st.success(f"✅ {result['message']}")

                            # Sheet-level details
                            for sheet_name, info in result.get("sheets", {}).items():
                                st.info(f"**{sheet_name}**: {info['info']}")

                            # Sync to Google Sheets
                            if GOOGLE_SHEETS_ENABLED:
                                with st.spinner("Sincronizando con Google Sheets..."):
                                    sync_all()
                                st.info("☁️ Datos sincronizados con Google Sheets")

                            st.balloons()
                        else:
                            st.error(f"❌ {result['message']}")
            else:
                st.error(f"❌ {msg}")

        finally:
            os.unlink(tmp_path)

    # Upload history
    render_section_header("Historial de Cargas")
    history = get_upload_history()
    if history.empty:
        st.info("No hay cargas previas")
    else:
        display_cols = ["filename", "uploaded_at", "sheet_name",
                        "periodo_meses", "row_count", "status"]
        available = [c for c in display_cols if c in history.columns]
        st.dataframe(
            history[available],
            use_container_width=True,
            hide_index=True,
            column_config={
                "filename": st.column_config.TextColumn("Archivo"),
                "uploaded_at": st.column_config.TextColumn("Fecha"),
                "sheet_name": st.column_config.TextColumn("Hoja"),
                "periodo_meses": st.column_config.NumberColumn("Meses"),
                "row_count": st.column_config.NumberColumn("Registros"),
                "status": st.column_config.TextColumn("Status"),
            },
        )

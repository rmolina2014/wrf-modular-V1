"""GUI Streamlit - usa orquestador Python puro."""
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Pipeline WRF PGICH", layout="wide")
st.title("Pipeline WRF PGICH")

casos_path = ROOT / "config" / "casos_oficiales.json"
try:
    casos_data = json.loads(casos_path.read_text(encoding="utf-8"))
    casos = casos_data.get("casos", [])
except Exception as e:
    st.error(f"Error cargando casos oficiales: {e}")
    casos = []

if casos:
    nombres = [f"{c['num']}: {c['id']} ({c['fecha']})" for c in casos]
    sel = st.selectbox("Seleccionar caso oficial (4)", nombres)
    idx = nombres.index(sel) if sel in nombres else 0
    c = casos[idx]
    st.write("Caso seleccionado:", c["id"])
    st.write("Resultados:", c["resultados_dir"])
    st.write("Informe:", c["informe"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Solo preparar"):
            st.info("Preparación vía orquestador (stub)")
    with col2:
        if st.button("Ejecutar completo (nudged+control+validación)"):
            st.info("Ejecución vía orquestador Python puro (stub)")

st.caption("GUI migrada a núcleo orquestador único")

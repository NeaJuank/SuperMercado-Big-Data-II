import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.load_data import load_config

config = load_config()

st.set_page_config(page_title="Dashboard Supermercado", layout="wide")
st.title("Dashboard Analítico - Predicción de Demanda")

try:
    df = pd.read_csv(config["paths"]["features_data"])
except Exception:
    st.error("No se encontró el archivo de features. Ejecuta el pipeline primero.")
    st.stop()

kpi_tab, ventas_tab, vencimientos_tab, predicciones_tab, etl_tab = st.tabs([
    "KPIs", "Ventas", "Vencimientos", "Predicciones", "Reporte ETL"
])

with kpi_tab:
    st.header("KPIs principales")
    col1, col2, col3 = st.columns(3)
    rotacion = df["cantidad_vendida"].sum() / ((df["stock_inicial"].mean() + df["stock_disponible"].mean()) / 2 + 1e-6)
    perdida = df["perdida_vencimiento"].sum()
    promo = (df[df["tiene_promocion"] == 1]["ingresos"].mean() - df[df["tiene_promocion"] == 0]["ingresos"].mean()) / (df[df["tiene_promocion"] == 0]["ingresos"].mean() + 1e-6)
    col1.metric("Rotación inventario", round(rotacion, 2))
    col2.metric("Pérdidas por vencimiento", f"${round(perdida, 2)}")
    col3.metric("Impacto de promociones", f"{round(promo * 100, 2)}%")

with ventas_tab:
    st.header("Ventas")
    st.bar_chart(df.groupby("producto")["cantidad_vendida"].sum())
    st.bar_chart(df.groupby("ciudad")["cantidad_vendida"].sum())

with vencimientos_tab:
    st.header("Productos con mayor riesgo de vencimiento")
    riesgo = df[df["riesgo_vencimiento"] == 1].groupby("producto")["cantidad_vendida"].sum().sort_values(ascending=False)
    st.dataframe(riesgo.head(10))
    st.write("Top 10 pérdidas por ciudad")
    st.dataframe(df.groupby("ciudad")["perdida_vencimiento"].sum().sort_values(ascending=False).head(10))

with predicciones_tab:
    st.header("Predicciones históricas")
    if os.path.exists(config["reports"]["reports_path"] + "/predicciones_historicas.csv"):
        pred_hist = pd.read_csv(config["reports"]["reports_path"] + "/predicciones_historicas.csv")
        st.dataframe(pred_hist.head(100))
    else:
        st.warning("Predicciones históricas no disponibles. Ejecuta el pipeline.")

with etl_tab:
    st.header("Reporte natural")
    path_report = config["reports"]["natural_report_path"]
    if os.path.exists(path_report):
        with open(path_report, "r", encoding="utf-8") as f:
            st.text(f.read())
    else:
        st.warning("Reporte natural no generado aún.")

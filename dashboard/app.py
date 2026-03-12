import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.load_data import load_config, load_dataset
from src.kpis.inventory_rotation import calculate_inventory_rotation
from src.kpis.expired_losses import calculate_total_expired_losses
from src.kpis.promotion_impact import promotion_sales_comparison


# -------------------------
# CONFIGURACIÓN DASHBOARD
# -------------------------

st.set_page_config(
    page_title="Predicción de Demanda Supermercado",
    layout="wide"
)

st.title("Sistema de Predicción de Demanda para Supermercados")

st.write("Dashboard de análisis de ventas y KPIs")


# -------------------------
# CARGAR DATOS
# -------------------------

config = load_config()

df = pd.read_csv(config["paths"]["features_data"])


# -------------------------
# KPIs PRINCIPALES
# -------------------------

st.header("KPIs del Negocio")

col1, col2, col3 = st.columns(3)

rotation = calculate_inventory_rotation(df)
expired = calculate_total_expired_losses(df)
promotion = promotion_sales_comparison(df)

with col1:
    st.metric("Rotación Inventario", round(rotation,2))

with col2:
    st.metric("Pérdidas por Vencimiento", f"${round(expired,2)}")

with col3:
    st.metric("Impacto Promociones", round(promotion,2))


# -------------------------
# ANALISIS DE VENTAS
# -------------------------

st.header("Ventas por Producto")

ventas_producto = df.groupby("producto")["cantidad_vendida"].sum()

st.bar_chart(ventas_producto)


# -------------------------
# ANALISIS POR CIUDAD
# -------------------------

st.header("Ventas por Ciudad")

ventas_ciudad = df.groupby("ciudad")["cantidad_vendida"].sum()

st.bar_chart(ventas_ciudad)


# -------------------------
# PROMOCIONES
# -------------------------

st.header("Impacto de Promociones")

promocion_data = df.groupby("promocion")["cantidad_vendida"].mean()

st.bar_chart(promocion_data)


# -------------------------
# TABLA DE DATOS
# -------------------------

st.header("Dataset")

st.dataframe(df.head(100))
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from db import obtener_registros_rutas, obtener_conductores_por_empresa
import plotly.express as px
import plotly.graph_objects as go

def calcular_rango_mes_actual():
    hoy = datetime.today()
    inicio = hoy.replace(day=1)
    fin = (inicio + relativedelta(months=1)) - timedelta(days=1)
    return inicio.date(), fin.date()

def calcular_quincena_actual():
    hoy = datetime.today()
    if hoy.day <= 15:
        inicio = hoy.replace(day=1)
        fin = hoy.replace(day=15)
    else:
        inicio = hoy.replace(day=16)
        fin = (hoy + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
    return inicio.date(), fin.date()


def parsear_clp(valor):
    """
    Convierte un string con formato CLP como '$650.000' en un float: 650000.0
    """
    if not valor:
        return 0.0
    if isinstance(valor, str):
        try:
            return float(valor.replace("$", "").replace(".", "").replace(",", "").strip())
        except ValueError:
            return 0.0
    return float(valor)


def formatear_clp(valor):
    """
    Convierte un número a formato CLP: 650000 -> $650.000
    """
    try:
        valor = float(valor)
        return "${:,.0f}".format(valor).replace(",", ".")
    except:
        return "$0"


def resumen_por_conductor():
    st.header("📊 Resumen por Conductor")

    empresa_id = st.session_state["empresa_id"]
    conductores = obtener_conductores_por_empresa(empresa_id)
    conductores_dict = {c["id"]: {"nombre": c["nombre"], "sueldo_base": c["sueldo_base"]} for c in conductores}

    inicio_defecto, fin_defecto = calcular_quincena_actual()

    with st.form("form_filtro_quincena"):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=inicio_defecto)
        with col2:
            fecha_fin = st.date_input("Hasta", value=fin_defecto)
        submitted = st.form_submit_button("Filtrar")

    if not submitted:
        fecha_inicio, fecha_fin = inicio_defecto, fin_defecto

    registros = obtener_registros_rutas(empresa_id, fecha_inicio, fecha_fin)
    df = pd.DataFrame(registros, columns=[
        "id", "fecha", "destino", "gasto_conductor", "gasto_petroleo", "valor_total",
        "conductor_id", "nombre_conductor", "rut", "sueldo_base"
    ])

    if df.empty:
        st.info("No hay registros en este rango de fechas.")
        return

    resumen = []
    for conductor_id, data in df.groupby("conductor_id"):
        nombre = conductores_dict.get(conductor_id, {}).get("nombre", "Desconocido")
        sueldo_base = conductores_dict.get(conductor_id, {}).get("sueldo_base", 0)
        gasto_conductor = data["gasto_conductor"].sum()
        total_rutas = len(data)

        sueldo_base_float = parsear_clp(sueldo_base)
        gasto_conductor_float = parsear_clp(gasto_conductor)
        total_a_pagar = sueldo_base_float + gasto_conductor_float

        resumen.append({
            "Conductor": nombre,
            "Sueldo Base": formatear_clp(sueldo_base_float),
            "Rutas Realizadas": total_rutas,
            "Total Rutas CLP": formatear_clp(gasto_conductor_float),
            "Total a Pagar": formatear_clp(total_a_pagar)
        })

    resumen_df = pd.DataFrame(resumen)
    resumen_df = resumen_df.sort_values("Conductor")

    st.dataframe(resumen_df, use_container_width=True, hide_index=True, height=400)

def resumen_general():
    st.subheader("📅 Resumen General del Mes")

    empresa_id = st.session_state["empresa_id"]
    inicio_defecto, fin_defecto = calcular_rango_mes_actual()

    with st.form("form_resumen_general"):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=inicio_defecto)
        with col2:
            fecha_fin = st.date_input("Hasta", value=fin_defecto)
        submitted = st.form_submit_button("Filtrar")

    if not submitted:
        fecha_inicio, fecha_fin = inicio_defecto, fin_defecto

    registros = obtener_registros_rutas(empresa_id, fecha_inicio, fecha_fin)
    df = pd.DataFrame(registros, columns=[
        "id", "fecha", "destino", "gasto_conductor", "gasto_petroleo", "valor_total",
        "conductor_id", "nombre_conductor", "rut", "sueldo_base"
    ])

    if df.empty:
        st.info("No hay registros en el rango seleccionado.")
        return

    total_rutas = len(df)
    total_valor = df["valor_total"].sum()
    total_gastos = df["gasto_conductor"].sum() + df["gasto_petroleo"].sum()
    utilidad = total_valor - total_gastos

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.metric("📦 Total de Rutas", total_rutas)
    col2.metric("💰 Total Ingresos", formatear_clp(total_valor))
    col3.metric("🛠️ Total Gastos", formatear_clp(total_gastos))
    col4.metric("📈 Utilidad", formatear_clp(utilidad))

    fig = px.pie(
        names=["Ingresos", "Gastos", "Utilidad"],
        values=[total_valor, total_gastos, utilidad],
        title="Distribución Ingresos vs. Gastos",
        color_discrete_sequence=px.colors.sequential.algae
    )
    st.plotly_chart(fig, use_container_width=True)

    # Agrupamos por conductor
    df_conductores = df.groupby("nombre_conductor").agg({
        "valor_total": "sum",
        "gasto_conductor": "sum",
        "gasto_petroleo": "sum"
    }).reset_index()

    df_conductores["utilidad"] = df_conductores["valor_total"] - (
            df_conductores["gasto_conductor"] + df_conductores["gasto_petroleo"]
    )

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_conductores["nombre_conductor"],
        y=df_conductores["valor_total"],
        name="Ingresos",
        marker_color="green"
    ))
    fig_bar.add_trace(go.Bar(
        x=df_conductores["nombre_conductor"],
        y=df_conductores["gasto_conductor"] + df_conductores["gasto_petroleo"],
        name="Gastos",
        marker_color="red"
    ))
    fig_bar.add_trace(go.Bar(
        x=df_conductores["nombre_conductor"],
        y=df_conductores["utilidad"],
        name="Utilidad",
        marker_color="blue"
    ))

    fig_bar.update_layout(
        barmode="group",
        title="Resumen por Conductor (Ingresos vs Gastos vs Utilidad)",
        xaxis_title="Conductor",
        yaxis_title="CLP",
        legend_title="Categoría",
    )

    st.plotly_chart(fig_bar, use_container_width=True)
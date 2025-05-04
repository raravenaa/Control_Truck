import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from db import obtener_registros_rutas, obtener_conductores_por_empresa


def calcular_quincena_actual():
    hoy = datetime.today()
    inicio, fin = None, None
    if hoy.day <= 15:
        inicio = hoy.replace(day=1)
        fin = hoy.replace(day=15)
    else:
        inicio = hoy.replace(day=16)
        fin = (hoy + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
    return inicio.date(), fin.date()


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



        def parsear_clp(sueldo_base):
            """
            Convierte un string con formato CLP como '$650.000' en un float: 650000.0
            """
            if not sueldo_base:
                return 0.0
            if isinstance(sueldo_base, str):
                try:
                    return float(sueldo_base.replace("$", "").replace(".", "").replace(",", "").strip())
                except ValueError:
                    return 0.0
            return float(sueldo_base)
        total_a_pagar = parsear_clp(sueldo_base) + parsear_clp(gasto_conductor)

        resumen.append({
            "Conductor": nombre,
            "Sueldo Base": sueldo_base,
            "Rutas Realizadas": total_rutas,
            "Total Rutas CLP": gasto_conductor,
            "Total a Pagar": total_a_pagar
        })

    resumen_df = pd.DataFrame(resumen)
    resumen_df = resumen_df.sort_values("Conductor")

    st.dataframe(resumen_df, use_container_width=True, hide_index=True, height=400)

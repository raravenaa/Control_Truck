import streamlit as st
import pandas as pd
from db import obtener_registros_por_empresa, obtener_estados, actualizar_estado_registro
from utils import formato_clp

def mostrar_visualizacion():
    st.header("📋 Visualización de Registros")

    estados = obtener_estados()
    estado_nombres = [e["nombre"] for e in estados]
    estado_dict = {e["nombre"]: e["id"] for e in estados}

    # Filtros
    estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estado_nombres)
    filtro_control = st.text_input("🔎 Buscar por N° de Control")

    registros = obtener_registros_por_empresa(st.session_state["empresa_id"])
    df = pd.DataFrame(registros, columns=[
        "ID", "Fecha", "N° Control", "N° Guía", "Destino",
        "Gasto Conductor", "Gasto Petróleo", "Valor Total", "Estado"
    ])

    if estado_filtro != "Todos":
        df = df[df["Estado"] == estado_filtro]

    if filtro_control:
        df = df[df["N° Control"].str.contains(filtro_control, case=False)]

    # Formato CLP
    for campo in ["Gasto Conductor", "Gasto Petróleo", "Valor Total"]:
        df[campo] = df[campo].apply(formato_clp)

    def emoji_estado(estado):
        estado = estado.lower()
        return {
            "pagado": "🟢",
            "rechazado": "🔴",
            "pendiente pago": "🟡",
            "rendido": "🔵",
            "pago chofer": "🟠",
            "entregado": "🟣",
        }.get(estado, "⬜️")

    df[" "] = df["Estado"].map(emoji_estado)

    df_original = df.copy()

    st.write("✏️ Puedes cambiar el estado directamente:")
    edited_df = st.data_editor(
        df,
        column_config={
            "Estado": st.column_config.SelectboxColumn("Estado", options=estado_nombres),
        },
        disabled=["ID", "Fecha", "N° Control", "N° Guía", "Destino", "Gasto Conductor", "Gasto Petróleo", "Valor Total", " "],
        hide_index=True,
        use_container_width=True
    )

    # Detectar cambios
    cambios = edited_df[edited_df["Estado"] != df_original["Estado"]]
    for _, row in cambios.iterrows():
        actualizar_estado_registro(row["ID"], estado_dict[row["Estado"]])
        st.success(f"✅ Estado actualizado para el N° Control {row['N° Control']}")

    if not cambios.empty:
        st.rerun()

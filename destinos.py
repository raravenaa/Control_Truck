import streamlit as st
import pandas as pd
from db import (
    obtener_destinos_completos,
    obtener_conductores_por_empresa,
    crear_destino,
    actualizar_destino,
    # deshabilitar_destino
)
from utils import formato_clp


def mostrar_destinos():
    st.header("📍 Gestión de Destinos o Rutas")

    empresa_id = st.session_state["empresa_id"]
    destinos = obtener_destinos_completos(empresa_id)
    conductores = obtener_conductores_por_empresa(empresa_id)
    conductores_dict = {c["id"]: f"{c['nombre']} {c['apellidos']}" for c in conductores}

    columnas = ["id", "nombre", "conductor", "gasto_conductor", "gasto_petroleo", "valor_total", "activo"]
    df_original = pd.DataFrame(destinos, columns=columnas)

    # Mostrar nombre del conductor en vez del ID
    df_original["conductor"] = df_original["conductor"].map(conductores_dict)

    # Renombrar columnas para mostrar en Data Editor
    df_original.rename(columns={
        "id": "ID",
        "nombre": "Nombre",
        "conductor": "Conductor",
        "gasto_conductor": "Gasto Conductor",
        "gasto_petroleo": "Gasto Petróleo",
        "valor_total": "Valor Total",
        "activo": "Activo"
    }, inplace=True)

    # Formato CLP
    for campo in ["Gasto Conductor", "Gasto Petróleo", "Valor Total"]:
        df_original[campo] = df_original[campo].apply(formato_clp)

    st.subheader("📋 Lista de Destinos")
    edited_df = st.data_editor(
        df_original,
        disabled=["ID","Nombre","Conductor"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    # Detectar y aplicar cambios
    for idx, row in edited_df.iterrows():
        original_row = df_original.loc[idx]
        if not row.equals(original_row):
            actualizar_destino(
                id=row["ID"],
                nombre=row["Nombre"],
                conductor=row["Conductor"],
                gasto_conductor=row["Gasto Conductor"],
                gasto_petroleo=row["Gasto Petróleo"],
                valor_total=row["Valor Total"],
                activo=row["Activo"]
            )
            st.success(f"✅ Destino '{row['Nombre']}' actualizado correctamente.")
            st.rerun()

    st.markdown("---")
    # Si se acaba de enviar un formulario, limpiamos el estado
    if st.session_state.get("form_submitted"):
        del st.session_state["form_submitted"]
        st.rerun()

    with st.expander("➕ Agregar nuevo destino"):
        with st.form("form_nuevo_destino"):
            nombre = st.text_input("Nombre")
            gasto_conductor = st.number_input("Gasto Conductor", min_value=0)
            gasto_petroleo = st.number_input("Gasto Petróleo", min_value=0)
            valor_total = st.number_input("Valor Total", min_value=0)
            conductor_id = st.selectbox("Conductor", options=list(conductores_dict.keys()),
                                        format_func=lambda x: conductores_dict[x])
            submitted = st.form_submit_button("Agregar")

            if submitted:
                if not nombre:
                    st.warning("⚠️ El nombre es obligatorio.")
                else:
                    crear_destino(nombre, gasto_conductor, gasto_petroleo, valor_total, conductor_id, empresa_id)
                    st.success("✅ Destino agregado correctamente.")
                    st.session_state["form_submitted"] = True
                    st.rerun()


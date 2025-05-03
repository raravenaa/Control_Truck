import streamlit as st
import pandas as pd
from db import (
    obtener_destinos_completos,
    obtener_conductores_por_empresa,
    #crear_destino,
    actualizar_destino,
    # deshabilitar_destino
)

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

    st.subheader("📋 Lista de Destinos")
    edited_df = st.data_editor(
        df_original,
        disabled=["ID","Conductor"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    # Detectar y aplicar cambios
    for idx, row in edited_df.iterrows():
        original_row = df_original.loc[idx]
        if not row.equals(original_row):
            conductor_id = next((id for id, nombre in conductores_dict.items() if nombre == row["Conductor"]), None)
            if conductor_id is None:
                st.warning(f"⚠️ El conductor asignado ya no existe para el destino '{row['Nombre']}'.")
                continue

            actualizar_destino(
                id=row["ID"],
                nombre=row["Nombre"],
                gasto_conductor=row["Gasto Conductor"],
                gasto_petroleo=row["Gasto Petróleo"],
                valor_total=row["Valor Total"],
                conductor_id=conductor_id
            )
            st.success(f"✅ Destino '{row['Nombre']}' actualizado correctamente.")
            st.rerun()

    st.markdown("---")
    with st.expander("➕ Agregar nuevo destino"):
        with st.form("form_nuevo_destino"):
            nombre = st.text_input("Nombre", key="nuevo_nombre")
            gasto_conductor = st.number_input("Gasto Conductor", min_value=0, key="nuevo_gc")
            gasto_petroleo = st.number_input("Gasto Petróleo", min_value=0, key="nuevo_gp")
            valor_total = st.number_input("Valor Total", min_value=0, key="nuevo_vt")
            conductor_id = st.selectbox("Conductor", options=list(conductores_dict.keys()), format_func=lambda x: conductores_dict[x], key="nuevo_conductor")
            submitted = st.form_submit_button("Agregar")

            if submitted:
                if not nombre:
                    st.warning("⚠️ El nombre es obligatorio.")
                else:
                    crear_destino(nombre, gasto_conductor, gasto_petroleo, valor_total, conductor_id, empresa_id)
                    st.success("✅ Destino agregado correctamente.")
                    for campo in ["nuevo_nombre", "nuevo_gc", "nuevo_gp", "nuevo_vt"]:
                        st.session_state[campo] = 0 if isinstance(st.session_state[campo], (int, float)) else ""
                    st.rerun()

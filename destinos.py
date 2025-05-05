import streamlit as st
import pandas as pd
from db import (
    obtener_destinos_completos,
    obtener_conductores_por_empresa,
    crear_destino,
    actualizar_destino,
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

    # Guardar el ID del conductor y mostrar el nombre en una columna separada
    df_original["Conductor ID"] = df_original["conductor"]
    df_original["Conductor Nombre"] = df_original["Conductor ID"].map(conductores_dict)

    # Renombrar columnas para mostrar en el editor
    df_original.rename(columns={
        "id": "ID",
        "nombre": "Nombre",
        "gasto_conductor": "Gasto Conductor",
        "gasto_petroleo": "Gasto Petróleo",
        "valor_total": "Valor Total",
        "activo": "Activo"
    }, inplace=True)

    # Mapeo visual para estado activo
    estado_display = {1: "🟢 Activado", 0: "🔴 Desactivado"}
    estado_reverse = {"🟢 Activado": 1, "🔴 Desactivado": 0}
    df_original["Activo"] = df_original["Activo"].map(estado_display)

    # Mostrar Data Editor
    st.subheader("📋 Lista de Destinos")
    edited_df = st.data_editor(
        df_original,
        column_config={
            "Activo": st.column_config.SelectboxColumn(
                label="Estado",
                help="Estado del destino",
                options=["🟢 Activado", "🔴 Desactivado"],
                required=True
            )
        },
        disabled=["ID", "Nombre", "Conductor Nombre"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_order=[
            "ID", "Nombre", "Conductor Nombre",
            "Gasto Conductor", "Gasto Petróleo", "Valor Total", "Activo"
        ]
    )

    # Detectar y aplicar cambios
    for idx, row in edited_df.iterrows():
        original_row = df_original.loc[idx]
        if not row.equals(original_row):
            def parsear_clp(valor):
                if isinstance(valor, str):
                    return float(valor.replace("$", "").replace(".", "").replace(",", "").strip())
                return float(valor)

            actualizar_destino(
                id=row["ID"],
                nombre=row["Nombre"],
                conductor=row["Conductor ID"],
                gasto_conductor=parsear_clp(row["Gasto Conductor"]),
                gasto_petroleo=parsear_clp(row["Gasto Petróleo"]),
                valor_total=parsear_clp(row["Valor Total"]),
                activo=estado_reverse[row["Activo"]]  # Convertimos la etiqueta visual a 0 o 1
            )
            st.success(f"✅ Destino '{row['Nombre']}' actualizado correctamente.")
            st.rerun()

    st.markdown("---")
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

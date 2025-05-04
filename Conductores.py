import streamlit as st
import pandas as pd
from db import (
    obtener_conductores_por_empresa,
    agregar_conductor,
    actualizar_conductor,
    deshabilitar_conductor
)
from utils import formato_clp


def mostrar_conductores():
    st.header("🧑‍✈️ Gestión de Conductores")

    empresa_id = st.session_state["empresa_id"]
    conductores = obtener_conductores_por_empresa(empresa_id)
    columnas = ["ID", "Nombre", "Apellidos", "RUT", "Tipo De Licencia", "Telefono", "Correo", "Sueldo Base", "Activo"]
    df_original = pd.DataFrame(conductores, columns=columnas)
    df_original["Sueldo Base"] = df_original["Sueldo Base"].apply(formato_clp)


    st.subheader("📋 Lista de Conductores Activos")
    edited_df = st.data_editor(
        df_original,
        disabled=["ID", "RUT"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    # Detectar y aplicar cambios
    for idx, row in edited_df.iterrows():
        original_row = df_original.loc[idx]
        if not row.equals(original_row):
            actualizar_conductor(
                id=row["ID"],
                nombre=row["Nombre"],
                apellidos=row["Apellidos"],
                rut=row["RUT"],
                tipo_licencia=row["Tipo De Licencia"],
                telefono=row["Telefono"],
                correo=row["Correo"],
                sueldo_base=row["Sueldo Base"],
                activo=row["Activo"]
            )
            st.success(f"✅ Conductor '{row['Nombre']}' actualizado correctamente.")
            st.rerun()

    # Formulario para agregar nuevo conductor
    st.markdown("---")

    with st.expander("➕ Agregar nuevo conductor"):
        with st.form("form_nuevo_conductor"):
            if "limpiar_campos" not in st.session_state:
                st.session_state.limpiar_campos = False

            if st.session_state.limpiar_campos:
                nombre = ""
                apellidos = ""
                rut = ""
                tipo_licencia = ""
                telefono = ""
                correo = ""
                sueldo_base = ""
                st.session_state.limpiar_campos = False
            else:
                nombre = st.text_input("Nombre", key="nuevo_nombre")
                apellidos = st.text_input("Apellidos", key="nuevo_apellidos")
                rut = st.text_input("RUT", key="nuevo_rut")
                tipo_licencia = st.text_input("Tipo de Licencia", key="nuevo_tipo_licencia")
                telefono = st.text_input("Teléfono", key="nuevo_telefono")
                correo = st.text_input("Correo", key="nuevo_correo")
                sueldo_base = st.text_input("Sueldo Base", key="nuevo_sueldo_base")

            submitted = st.form_submit_button("Agregar")

            if submitted:
                if not nombre or not rut:
                    st.warning("⚠️ Nombre y RUT son obligatorios.")
                else:
                    ruts_existentes = df_original["RUT"].tolist()
                    if rut in ruts_existentes:
                        st.error("❌ Este RUT ya ha sido utilizado.")
                    else:
                        agregar_conductor(empresa_id, nombre, apellidos, rut, tipo_licencia, telefono, correo,
                                          sueldo_base)
                        st.success("✅ Conductor agregado correctamente.")
                        st.session_state.limpiar_campos = True
                        st.rerun()



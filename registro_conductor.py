# registro_conductor.py

import streamlit as st
from datetime import date
from db import (
    obtener_destinos,
    obtener_estados,
    insertar_registro,
    existe_numero_control,
)
from utils import formato_clp


def mostrar_registro_conductor():
    st.header("🚛 Registro de Ruta (Conductor)")

    empresa_id = st.session_state["empresa_id"]
    conductor_id = st.session_state["conductor_id"]
    conductor_nombre = st.session_state["conductor_nombre"]

    destinos = obtener_destinos()
    estados = obtener_estados()

    destinos_conductor = [d for d in destinos if d["conductor"] == conductor_id]
    if not destinos_conductor:
        st.warning("⚠️ No tienes destinos asignados. Contacta a tu administrador.")
        return

    destino_nombres = list(set([d["nombre"] for d in destinos_conductor]))
    estado_nombres = [e["nombre"] for e in estados]

    st.markdown(f"👨‍✈️ Conductor: **{conductor_nombre}**")

    destino_seleccionado = st.selectbox("📍 Destino", destino_nombres)

    datos_destino = next(
        (d for d in destinos_conductor if d["nombre"] == destino_seleccionado),
        None
    )

    if not datos_destino:
        st.warning("⚠️ No tienes ese destino asignado.")
        return

    with st.container():
        st.markdown("### 📝 Datos del Registro")
        with st.form("form_registro_conductor", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("📅 Fecha", value=date.today())
                numero_control = st.text_input("🔢 N° de Control")

                if numero_control:
                    if existe_numero_control(numero_control, empresa_id):
                        st.error("❌ Ya existe un registro con ese N° de Control.")
                    else:
                        st.success("✅ N° de Control disponible.")

            with col2:
                numero_guia = st.text_input("📦 N° de Guía")

            st.divider()
            estado_elegido = st.selectbox("📌 Estado del Registro", estado_nombres)
            id_estado = next(e["id"] for e in estados if e["nombre"] == estado_elegido)

            enviar = st.form_submit_button("💾 Guardar Registro")

            if enviar:
                if existe_numero_control(numero_control, empresa_id):
                    st.error("❌ Ese N° de Control ya existe.")
                else:
                    data = (
                        empresa_id,
                        conductor_id,
                        fecha.isoformat(),
                        numero_control,
                        numero_guia,
                        destino_seleccionado,
                        datos_destino["gasto_conductor"],
                        datos_destino["gasto_petroleo"],
                        datos_destino["valor_total"],
                        id_estado
                    )
                    insertar_registro(data)
                    st.success("✅ Registro guardado correctamente.")

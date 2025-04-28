# ingreso.py

import streamlit as st
from datetime import date
from db import obtener_destinos, obtener_estados, insertar_registro
from utils import formato_clp

def mostrar_ingreso():
    st.header("🚛 Registro de Ruta")

    destinos = obtener_destinos()
    estados = obtener_estados()

    destino_nombres = [d["nombre"] for d in destinos]
    estado_nombres = [e["nombre"] for e in estados]

    destino_seleccionado = st.selectbox("📍 Destino", destino_nombres)
    datos_destino = next(d for d in destinos if d["nombre"] == destino_seleccionado)

    # Contenedor visual tipo "card"
    with st.container():
        st.markdown("### 📝 Datos del Registro")
        with st.form("form_registro", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                fecha = st.date_input("📅 Fecha", value=st.session_state.get("form_fecha", date.today()))
                numero_control = st.text_input("🔢 N° de Control", value=st.session_state.get("form_control", ""))

            with col2:
                numero_guia = st.text_input("📦 N° de Guía", value=st.session_state.get("form_guia", ""))

            st.divider()
            st.markdown("### 💰 Detalles del Viaje (no editables)")
            col3, col4, col5 = st.columns(3)
            col3.metric("Gasto Conductor", formato_clp(datos_destino["gasto_conductor"]))
            col4.metric("Gasto Petróleo", formato_clp(datos_destino["gasto_petroleo"]))
            col5.metric("Valor Total", formato_clp(datos_destino["valor_total"]))

            st.divider()
            estado_elegido = st.selectbox("📌 Estado del Registro", estado_nombres)
            id_estado = next(e["id"] for e in estados if e["nombre"] == estado_elegido)

            enviar = st.form_submit_button("💾 Guardar Registro")

            if enviar:
                data = (
                    st.session_state["empresa_id"],
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

                # Limpiar
                st.session_state["form_fecha"] = date.today()
                st.session_state["form_control"] = ""
                st.session_state["form_guia"] = ""

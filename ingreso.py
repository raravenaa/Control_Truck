import streamlit as st
from datetime import date
from db import (
    obtener_destinos,
    obtener_estados,
    obtener_conductores_por_empresa,
    insertar_registro,
    existe_numero_control
)
from utils import formato_clp


def mostrar_ingreso():
    st.header("🚛 Registro de Ruta")

    empresa_id = st.session_state["empresa_id"]
    destinos = obtener_destinos()
    estados = obtener_estados()
    conductores = obtener_conductores_por_empresa(empresa_id)
    conductores_activos = [c for c in conductores if c["activo"]]

    destino_nombres = list(set([d["nombre"] for d in destinos]))  # evitar repetidos
    estado_nombres = [e["nombre"] for e in estados]
    conductor_nombres = [f"{c['nombre']} (RUT: {c['rut']})" for c in conductores_activos]

    conductor_idx = st.selectbox("🧑‍✈️ Conductor", conductor_nombres)
    conductor_seleccionado = conductores_activos[conductor_nombres.index(conductor_idx)]
    conductor_id = conductor_seleccionado["id"]

    destino_seleccionado = st.selectbox("📍 Destino", destino_nombres)

    # Buscar el destino exacto para el conductor
    datos_destino = next(
        (d for d in destinos if d["nombre"] == destino_seleccionado and d["conductor"] == conductor_id),
        None
    )

    if not datos_destino:
        st.warning("⚠️ Este conductor no tiene asignado ese destino.")
        return

    gasto_conductor = datos_destino["gasto_conductor"]
    gasto_petroleo = datos_destino["gasto_petroleo"]
    valor_total = datos_destino["valor_total"]

    with st.container():
        st.markdown("### 📝 Datos del Registro")
        with st.form("form_registro", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("📅 Fecha", value=st.session_state.get("form_fecha", date.today()))

                numero_control = st.text_input("🔢 N° de Control", value=st.session_state.get("form_control", ""))

                if numero_control:
                    # Validamos si el número de control ya existe
                    if existe_numero_control(numero_control, empresa_id):
                        st.error("❌ Ya existe un registro con ese N° de Control.")
                    else:
                        st.success("✅ N° de Control disponible.")

            with col2:
                numero_guia = st.text_input("📦 N° de Guía", value=st.session_state.get("form_guia", ""))

            st.divider()
            st.markdown("### 💰 Detalles del Viaje (no editables)")
            col3, col4, col5 = st.columns(3)
            col3.metric("Gasto Conductor", formato_clp(gasto_conductor))
            col4.metric("Gasto Petróleo", formato_clp(gasto_petroleo))
            col5.metric("Valor Total", formato_clp(valor_total))

            st.divider()
            estado_elegido = st.selectbox("📌 Estado del Registro", estado_nombres)
            id_estado = next(e["id"] for e in estados if e["nombre"] == estado_elegido)

            # Lógica del formulario
            enviar = st.form_submit_button("💾 Guardar Registro")

            # Validación al momento de enviar el formulario
            if enviar:
                if existe_numero_control(numero_control, empresa_id):
                    st.error("❌ Ya existe un registro con ese N° de Control. Por favor ingresa uno diferente.")
                else:
                    # Insertar el registro solo si no existe
                    data = (
                        empresa_id,
                        conductor_id,
                        fecha.isoformat(),
                        numero_control,
                        numero_guia,
                        destino_seleccionado,
                        gasto_conductor,
                        gasto_petroleo,
                        valor_total,
                        id_estado
                    )
                    insertar_registro(data)
                    st.success("✅ Registro guardado correctamente.")

                    # Limpiar
                    st.session_state["form_fecha"] = date.today()
                    st.session_state["form_control"] = ""
                    st.session_state["form_guia"] = ""


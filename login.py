# login.py

import streamlit as st
from db import conexion


def verificar_credenciales(usuario: str, password: str):
    """
    Verifica que el par (usuario, password) exista en la tabla empresas.
    Devuelve (id, nombre) o None.
    """
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre FROM empresas WHERE usuario = ? AND contraseña = ?",
        (usuario, password)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado


def cerrar_sesion():
    """
    Limpia la sesión de Streamlit.
    """
    for key in ["empresa_id", "empresa_nombre"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def mostrar_login():
    """
    Muestra un formulario de login.
    Si las credenciales son válidas, guarda id y nombre en session_state.
    """
    st.title("🔒 Inicio de Sesión")
    st.write("Ingresa tu usuario y contraseña para acceder.")

    with st.form("form_login", clear_on_submit=False):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")

    if submit:
        resultado = verificar_credenciales(usuario, password)
        if resultado:
            st.success(f"✔️ Bienvenido, {resultado['nombre']}!")
            st.session_state["empresa_id"] = resultado["id"]
            st.session_state["empresa_nombre"] = resultado["nombre"]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")


def mostrar_logout():
    """
    Muestra el nombre de la empresa conectada y un botón para cerrar sesión.
    """
    st.sidebar.markdown(f"**Empresa:** {st.session_state.get('empresa_nombre', '')}")
    if st.sidebar.button("🔓 Cerrar sesión"):
        cerrar_sesion()

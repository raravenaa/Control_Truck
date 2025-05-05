# login.py

import streamlit as st
from db import conexion


def verificar_credenciales(usuario: str, password: str):
    """
    Verifica si el usuario corresponde a una empresa o a un conductor.
    Devuelve un dict con tipo ("empresa" o "conductor") e info correspondiente, o None.
    """
    conn = conexion()
    cursor = conn.cursor()

    # Verificar en empresas
    cursor.execute(
        "SELECT id, nombre FROM empresas WHERE usuario = ? AND contraseña = ?",
        (usuario, password)
    )
    empresa = cursor.fetchone()
    if empresa:
        conn.close()
        return {
            "tipo": "empresa",
            "id": empresa["id"],
            "nombre": empresa["nombre"]
        }

    # Verificar en conductores
    cursor.execute(
        "SELECT id, username, empresa_id FROM usuarios WHERE username = ? AND password_hash = ? AND activo = 1",
        (usuario, password)
    )
    conductor = cursor.fetchone()
    conn.close()
    if conductor:
        return {
            "tipo": "conductor",
            "id": conductor["id"],
            "nombre": conductor["username"],
            "empresa_id": conductor["empresa_id"]
        }

    return None


def cerrar_sesion():
    """
    Limpia todos los datos de sesión.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def mostrar_login():
    """
    Formulario de login para empresa o conductor.
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
            if resultado["tipo"] == "empresa":
                st.session_state["tipo_usuario"] = "empresa"
                st.session_state["empresa_id"] = resultado["id"]
                st.session_state["empresa_nombre"] = resultado["nombre"]
                st.success(f"✔️ Bienvenido, {resultado['nombre']} (Empresa)")

            elif resultado["tipo"] == "conductor":
                st.session_state["tipo_usuario"] = "conductor"
                st.session_state["empresa_id"] = resultado["empresa_id"]
                st.session_state["conductor_id"] = resultado["id"]
                st.session_state["conductor_nombre"] = resultado["nombre"]
                st.success(f"✔️ Bienvenido, {resultado['nombre']} (Conductor)")

            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")


def mostrar_logout():
    """
    Muestra el nombre del usuario conectado y botón para cerrar sesión.
    """
    tipo = st.session_state.get("tipo_usuario")
    if tipo == "empresa":
        nombre = st.session_state.get("empresa_nombre", "")
    elif tipo == "conductor":
        nombre = st.session_state.get("conductor_nombre", "")
    else:
        nombre = "Desconocido"

    st.sidebar.markdown(f"**Usuario:** {nombre}")
    if st.sidebar.button("🔓 Cerrar sesión"):
        cerrar_sesion()

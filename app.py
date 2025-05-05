# app.py

import streamlit as st
from streamlit_option_menu import option_menu

from Conductores import mostrar_conductores
from destinos import mostrar_destinos
from login import mostrar_login, mostrar_logout
from ingreso import mostrar_ingreso
from resumen import resumen_por_conductor, resumen_general
from visualizacion import mostrar_visualizacion
from registro_conductor import mostrar_registro_conductor  # nuevo archivo

st.set_page_config(page_title="Gestión de Flota", layout="wide")

# 1) Si no hay sesión activa
if "tipo_usuario" not in st.session_state:
    mostrar_login()
    st.stop()

# 2) Mostrar logout
mostrar_logout()

tipo_usuario = st.session_state["tipo_usuario"]

# 3) Menú según tipo de usuario
with st.sidebar:
    if tipo_usuario == "empresa":
        menu = option_menu(
            menu_title="Menú Principal",
            options=["Ingreso", "Visualización", "Conductores", "Rutas", "Resumen"],
            icons=["plus-circle", "card-list", "truck", "map", "bar-chart"],
            menu_icon="cast",
            default_index=0
        )
    elif tipo_usuario == "conductor":
        menu = option_menu(
            menu_title="Menú Conductor",
            options=["Registro"],
            icons=["clipboard-plus"],
            menu_icon="person",
            default_index=0
        )

# 4) Mostrar secciones según usuario
if tipo_usuario == "empresa":
    if menu == "Ingreso":
        mostrar_ingreso()
    elif menu == "Visualización":
        mostrar_visualizacion()
    elif menu == "Conductores":
        mostrar_conductores()
    elif menu == "Rutas":
        mostrar_destinos()
    elif menu == "Resumen":
        tab1, tab2 = st.tabs(["📅 General", "👨‍✈️ Por Conductor"])
        with tab1:
            resumen_general()
        with tab2:
            resumen_por_conductor()

elif tipo_usuario == "conductor":
    if menu == "Registro":
        mostrar_registro_conductor()

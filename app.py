import streamlit as st
from streamlit_option_menu import option_menu

from Conductores import mostrar_conductores
from destinos import mostrar_destinos
from login import mostrar_login, mostrar_logout
from ingreso import mostrar_ingreso
from resumen import resumen_por_conductor
from visualizacion import mostrar_visualizacion
# from camioneros import mostrar_camioneros
# from resumen import mostrar_resumen

# Configuración de la página
st.set_page_config(page_title="Gestión de Flota", layout="wide")

# 1) Mostrar login si no hay sesión activa
if "empresa_id" not in st.session_state:
    mostrar_login()
    st.stop()

# 2) Mostrar logout y nombre de empresa en sidebar
mostrar_logout()

# 3) Menú estilo macOS
with st.sidebar:
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Ingreso", "Visualización", "Conductores","Rutas", "Resumen"],
        icons=["plus-circle", "card-list", "truck","map", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "10px", "background-color": "#f9f9f9"},
            "icon": {"color": "black", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": "#e1e1e1",
            },
            "nav-link-selected": {"background-color": "#d6d6d6"},
        }
    )

# 4) Mostrar la sección correspondiente
empresa_id = st.session_state["empresa_id"]

if menu == "Ingreso":
    mostrar_ingreso()
elif menu == "Visualización":
    mostrar_visualizacion()
elif menu == "Conductores":
    mostrar_conductores()
elif menu == "Rutas":
    mostrar_destinos()
elif menu == "Resumen":
    resumen_por_conductor()

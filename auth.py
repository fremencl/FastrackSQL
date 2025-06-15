# auth.py
import hmac
import streamlit as st
import os

def check_password():
    """
    Retorna `True` si el usuario ha ingresado la contraseña correcta.
    Caso contrario, muestra un cuadro de texto para ingresar password y retorna `False`.
    """
    def password_entered():
        app_password = os.getenv("PASSWORD")  # Leer desde variable de entorno
        if hmac.compare_digest(st.session_state["password"], app_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Se elimina la contraseña de la sesión por seguridad.
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Ingrese la contraseña",
        type="password",
        on_change=password_entered,
        key="password"
    )

    if "password_correct" in st.session_state and st.session_state["password_correct"] is False:
        st.error("❌ Contraseña incorrecta. Intente de nuevo.")

    return False

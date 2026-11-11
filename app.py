import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Predictivo Mantenimiento",
    page_icon="⚡",
    layout="centered"
)

# Conexión directa a nivel raíz de los Secrets
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    if "client_email" in st.secrets:
        secrets_dict = {
            "type": st.secrets.get("type", "service_account"),
            "project_id": st.secrets.get("project_id"),
            "private_key_id": st.secrets.get("private_key_id"),
            "private_key": st.secrets.get("private_key", "").replace("\\n", "\n"),
            "client_email": st.secrets.get("client_email"),
            "client_id": st.secrets.get("client_id"),
            "auth_uri": st.secrets.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": st.secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": st.secrets.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": st.secrets.get("client_x509_cert_url")
        }
        
        creds = Credentials.from_service_account_info(secrets_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("HISTORIAL PREDICTIVO EMPRESA").sheet1
        return sheet
    else:
        st.warning("⚠️ Faltan configurar las credenciales en los Secrets de Streamlit.")
        return None

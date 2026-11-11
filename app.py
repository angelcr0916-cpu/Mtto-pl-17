import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

st.set_page_config(
    page_title="Predictivo Mantenimiento",
    page_icon="📁",
    layout="centered"
)

# Configuración de credenciales y cliente de Google Drive mediante archivo JSON temporal
@st.cache_resource
def get_drive_service():
    if "gcp_service_account" in st.secrets:
        sec = st.secrets["gcp_service_account"]
        raw_key = sec.get("private_key", "").replace("\\n", "\n")
        
        creds_dict = {
            "type": sec.get("type", "service_account"),
            "project_id": sec.get("project_id"),
            "private_key_id": sec.get("private_key_id"),
            "private_key": raw_key,
            "client_email": sec.get("client_email"),
            "client_id": sec.get("client_id"),
            "auth_uri": sec.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": sec.get("token_uri", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": sec.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": sec.get("client_x509_cert_url")
        }
        
        # Archivo temporal para evitar errores de validación de tipos en la nube
        with open("temp_drive_creds.json", "w") as f:
            json.dump(creds_dict, f)
            
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("temp_drive_creds.json", scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        return service
    return None

drive_service = get_drive_service()
FOLDER_ID = "15T6wDRWDHQBKtFn_PUv00AccC9dujuv9r"
FILE_NAME = "historial_predictivo.csv"

# Función para leer el archivo CSV desde tu carpeta de Drive
def cargar_datos_drive():
    if not drive_service:
        return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])
    
    try:
        query = f"q='{FOLDER_ID}' in parents and name='{FILE_NAME}' and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if not files:
            df_vacio = pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])
            guardar_datos_drive(df_vacio)
            return df_vacio
        
        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        fh.seek(0)
        return pd.read_csv(fh)
    except Exception as e:
        st.error(f"Error al leer de Google Drive: {e}")
        return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])

# Función para guardar el archivo CSV directamente en tu carpeta de Drive
def guardar_datos_drive(df):
    if not drive_service:
        return
    
    try:
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        query = f"q='{FOLDER_ID}' in parents and name='{FILE_NAME}' and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
        
        if files:
            file_id = files[0]['id']
            drive_service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
        else:
            file_metadata = {
                'name': FILE_NAME,
                'parents': [FOLDER_ID]
            }
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
    except Exception as e:
        st.error(f"Error al guardar en Google Drive: {e}")

# Interfaz de Usuario
st.title("📁 Monitoreo Predictivo")
st.markdown("Registro de parámetros críticos sincronizado en tu carpeta de Google Drive")

df_existente = cargar_datos_drive()

# --- FORMULARIO DE CAPTURA ---
with st.form("registro_form", clear_on_submit=True):
    st.subheader("➕ Nuevo Registro")
    
    col1, col2 = st.columns(2)
    with col1:
        linea = st.text_input("Línea de Producción", placeholder="Ej. Línea 1")
    with col2:
        equipo = st.text_input("Número de Equipo", placeholder="Ej. Motor M-04")
        
    mes = st.selectbox("Mes de Monitoreo", [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ], index=10)
    
    col3, col4, col5 = st.columns(3)
    with col3:
        temp = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f")
    with col4:
        amp = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f")
    with col5:
        vib = st.number_input("Vibración", min_value=0.0, step=0.1, format="%.1f")
        
    submitted = st.form_submit_button("Guardar Lectura en Drive")
    
    if submitted:
        if linea and equipo:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha_actual,
                "Línea": linea,
                "Equipo": equipo,
                "Mes": mes,
                "Temperatura (°C)": temp,
                "Amperaje (A)": amp,
                "Vibración (mm/s)": vib
            }])
            
            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
            guardar_datos_drive(df_actualizado)
            
            st.success(f"¡Lectura guardada con éxito en tu carpeta de Drive para el equipo {equipo}!")
            st.rerun()
        else:
            st.error("Por favor completa la Línea y el Número de Equipo.")

st.divider()

# --- HISTÓRICO ---
st.subheader("📊 Histórico de Equipos")

if not df_existente.empty:
    busqueda = st.text_input("🔍 Buscar equipo o línea...", "")
    
    if busqueda:
        df_filtrado = df_existente[df

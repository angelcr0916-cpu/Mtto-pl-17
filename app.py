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

# Configuración de conexión a Google Sheets corregida
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if "gcp_service_account" in st.secrets:
        # Cargamos los secretos como diccionario directo
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Usamos google.oauth2 para evitar errores de codificación
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("HISTORIAL PREDICTIVO EMPRESA").sheet1
        return sheet
    else:
        st.warning("⚠️ Faltan configurar las credenciales de Google Sheets en los Secrets de Streamlit.")
        return None

st.title("⚡ Monitoreo Predictivo")
st.markdown("Registro de parámetros críticos por equipo (Sincronizado en la Nube)")

sheet = init_connection()

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
        
    submitted = st.form_submit_button("Guardar Lectura en la Nube")
    
    if submitted:
        if linea and equipo and sheet:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            sheet.append_row([fecha_actual, linea, equipo, mes, temp, amp, vib])
            st.success(f"¡Lectura guardada con éxito para el equipo {equipo} en Google Sheets!")
        else:
            st.error("Por favor completa la Línea y el Número de Equipo.")

st.divider()

# --- HISTÓRICO DESDE GOOGLE SHEETS ---
st.subheader("📊 Histórico de Equipos")

if sheet:
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar equipo o línea...", "")
            
            if busqueda:
                df_filtrado = df[df['Equipo'].astype(str).str.contains(busqueda, case=False, na=False) | 
                                 df['Línea'].astype(str).str.contains(busqueda, case=False, na=False)]
            else:
                df_filtrado = df

            st.dataframe(df_filtrado, use_container_width=True)
            
            if 'Equipo' in df.columns:
                equipos_disponibles = df['Equipo'].unique()
                equipo_seleccionado = st.selectbox("Ver tendencia histórica de:", equipos_disponibles)
                
                if equipo_seleccionado:
                    df_eq = df[df['Equipo'] == equipo_seleccionado]
                    st.write(f"Tendencia para: **{equipo_seleccionado}**")
                    if len(df_eq) > 1 and 'Mes' in df.columns:
                        st.line_chart(df_eq.set_index('Mes')[['Temperatura (°C)', 'Amperaje (A)', 'Vibración (mm/s)']])
        else:
            st.info("Tu Google Sheet está vacío. Haz tu primer registro arriba para comenzar.")
    except Exception as e:
        st.error(f"Error al cargar los datos de la hoja: {e}")

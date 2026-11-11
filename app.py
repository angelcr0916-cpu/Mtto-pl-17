import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Monitoreo Predictivo - Local",
    page_icon="⚡",
    layout="centered"
)

# Archivo CSV local donde se guardará todo el historial de forma directa
DB_FILE = "historial_predictivo.csv"

def cargar_datos_locales():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except Exception:
            pass
    # Si no existe, creamos un DataFrame vacío con las columnas necesarias
    df_vacio = pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])
    df_vacio.to_csv(DB_FILE, index=False)
    return df_vacio

def guardar_datos_locales(df):
    df.to_csv(DB_FILE, index=False)

# Interfaz de Usuario
st.title("⚡ Monitoreo Predictivo (Modo Directo)")
st.markdown("Registro y control de parámetros críticos operando de forma limpia y sin complicaciones.")

df_existente = cargar_datos_locales()

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
    
    col3, col4, col5 = st.columns3()
    with col3:
        temp = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f")
    with col4:
        amp = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f")
    with col5:
        vib = st.number_input("Vibración", min_value=0.0, step=0.1, format="%.1f")
        
    submitted = st.form_submit_button("Guardar Lectura")
    
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
            guardar_datos_locales(df_actualizado)
            
            st.success(f"¡Lectura registrada con éxito para el equipo {equipo}!")
            st.rerun()
        else:
            st.error("Por favor completa la Línea y el Número de Equipo.")

st.divider()

# --- HISTÓRICO Y TENDENCIAS ---
st.subheader("📊 Histórico de Equipos")

if not df_existente.empty:
    busqueda = st.text_input("🔍 Buscar equipo o línea...", "")
    
    if busqueda:
        df_filtrado = df_existente[
            df_existente['Equipo'].astype(str).str.contains(busqueda, case=False, na=False) | 
            df_existente['Línea'].astype(str).str.contains(busqueda, case=False, na=False)
        ]
    else:
        df_filtrado = df_existente

    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón para descargar el archivo CSV directamente cuando lo necesites
    with open(DB_FILE, "rb") as file:
        st.download_button(
            label="📥 Descargar Base de Datos (CSV)",
            data=file,
            file_name="historial_predictivo.csv",
            mime="text/csv"
        )
    
    st.divider()
    
    if 'Equipo' in df_existente.columns and not df_existente['Equipo'].dropna().empty:
        equipos_disponibles = df_existente['Equipo'].dropna().unique()
        equipo_seleccionado = st.selectbox("Ver tendencia histórica de:", equipos_disponibles)
        
        if equipo_seleccionado:
            df_eq = df_existente[df_existente['Equipo'] == equipo_seleccionado]
            st.write(f"Tendencia para: **{equipo_seleccionado}**")
            if len(df_eq) > 1 and 'Mes' in df_existente.columns:
                st.line_chart(df_eq.set_index('Mes')[['Temperatura (°C)', 'Amperaje (A)', 'Vibración (mm/s)']])
else:
    st.info("Aún no hay registros en la base de datos. Haz tu primer registro arriba.")

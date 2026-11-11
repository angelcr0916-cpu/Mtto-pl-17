import streamlit as st
import pandas as pd
import os

# Configuración de la página para vista móvil
st.set_page_config(
    page_title="Predictivo Mantenimiento",
    page_icon="⚡",
    layout="centered"
)

# Archivo local para persistencia de datos
DATA_FILE = "historico_predictivo.csv"

# Función para cargar datos
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])

df = load_data()

st.title("⚡ Monitoreo Predictivo")
st.markdown("Registro de parámetros críticos por equipo")

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
    ], index=10) # Default Noviembre
    
    col3, col4, col5 = st.columns(3)
    with col3:
        temp = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f")
    with col4:
        amp = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f")
    with col5:
        vib = st.number_input("Vibración", min_value=0.0, step=0.1, format="%.1f")
        
    submitted = st.form_submit_button("Guardar Lectura")
    
    if submitted:
        if linea and equipo:
            nuevo_registro = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "Línea": linea,
                "Equipo": equipo,
                "Mes": mes,
                "Temperatura (°C)": temp,
                "Amperaje (A)": amp,
                "Vibración (mm/s)": vib
            }])
            
            df = pd.concat([nuevo_registro, df], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"¡Lectura guardada para el equipo {equipo}!")
        else:
            st.error("Por favor completa la Línea y el Número de Equipo.")

st.divider()

# --- HISTÓRICO Y FILTROS ---
st.subheader("📊 Histórico de Equipos")

if not df.empty:
    # Filtro rápido por equipo o línea
    busqueda = st.text_input("🔍 Buscar equipo o línea...", "")
    
    if busqueda:
        df_filtrado = df[df['Equipo'].str.contains(busqueda, case=False, na=False) | df['Línea'].str.contains(busqueda, case=False, na=False)]
    else:
        df_filtrado = df

    st.dataframe(df_filtrado, use_container_width=True)

    # Gráfica rápida de tendencia si seleccionan un equipo específico
    equipos_disponibles = df['Equipo'].unique()
    equipo_seleccionado = st.selectbox("Ver tendencia histórica de:", equipos_disponibles)
    
    if equipo_seleccionado:
        df_eq = df[df['Equipo'] == equipo_seleccionado]
        st.write(f"Tendencia para: *{equipo_seleccionado}*")
        
        if len(df_eq) > 1:
            st.line_chart(df_eq.set_index('Mes')[['Temperatura (°C)', 'Amperaje (A)', 'Vibración (mm/s)']])
        else:
            st.info("Agrega más registros en diferentes meses para visualizar la gráfica de tendencia completa.")

    # Botón para descargar el reporte en CSV (Excel)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Histórico en CSV (Excel)",
        data=csv,
        file_name='historico_predictivo_equipos.csv',
        mime='text/csv',
    )
else:
    st.info("Aún no hay registros guardados. Rellena el formulario de arriba para empezar.")

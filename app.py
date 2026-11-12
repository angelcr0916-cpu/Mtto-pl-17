import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Monitoreo Predictivo - Seguro",
    page_icon="🔒",
    layout="centered"
)

# PIN de seguridad de 4 dígitos para modificaciones/borrados (puedes cambiarlo aquí cuando quieras)
PIN_SEGURIDAD = "2026"

# Archivo CSV local donde se acumulan las lecturas mes con mes
DB_FILE = "historial_predictivo.csv"

def cargar_datos_locales():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            expected_cols = ["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            pass
    df_vacio = pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])
    df_vacio.to_csv(DB_FILE, index=False)
    return df_vacio

def guardar_datos_locales(df):
    df.to_csv(DB_FILE, index=False)

# Interfaz de Usuario
st.title("🔒 Monitoreo Predictivo")
st.markdown("Registro acumulativo por secciones, evolución mensual y protección por PIN.")

df_existente = cargar_datos_locales()

# --- FORMULARIO DE CAPTURA ACUMULATIVA ---
with st.form("registro_form", clear_on_submit=True):
    st.subheader("➕ Agregar Medición Mensual")
    
    col1, col2 = st.columns(2)
    with col1:
        linea = st.selectbox(
            "Seleccionar o Indicar Línea",
            ["Línea 1", "Línea 2", "Línea 3", "Línea Extrusión", "Otra (Escribir abajo)"]
        )
        if linea == "Otra (Escribir abajo)":
            linea = st.text_input("Nombre de la nueva Línea", placeholder="Ej. Línea Auxiliar")
            
    with col2:
        equipo = st.text_input("Nombre / Número de Equipo", placeholder="Ej. Motor M-04")
        
    mes = st.selectbox("Mes de la Medición", [
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
        
    submitted = st.form_submit_button("Guardar Medición al Historial")
    
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
            
            st.success(f"¡Medición de **{mes}** agregada con éxito para el equipo **{equipo}** ({linea})!")
            st.rerun()
        else:
            st.error("Por favor completa la Línea y el Nombre del Equipo.")

st.divider()

# --- HISTÓRICO Y FILTROS ---
st.subheader("📊 Histórico Acumulado por Secciones")

if not df_existente.empty:
    lineas_registradas = ["Todas las Líneas"] + list(df_existente['Línea'].dropna().unique())
    linea_seleccionada_filtro = st.selectbox("🔍 Filtrar vista por Línea:", lineas_registradas)
    
    if linea_seleccionada_filtro != "Todas las Líneas":
        df_filtrado = df_existente[df_existente['Línea'] == linea_seleccionada_filtro]
    else:
        df_filtrado = df_existente
        
    busqueda = st.text_input("🔎 Buscar equipo específico en la tabla...", "")
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado['Equipo'].astype(str).str.contains(busqueda, case=False, na=False) | 
            df_filtrado['Línea'].astype(str).str.contains(busqueda, case=False, na=False)
        ]

    st.dataframe(df_filtrado, use_container_width=True)
    
    # --- ZONA PROTEGIDA POR PIN PARA BORRAR REGISTROS ---
    with st.expander("🗑️ Zona de Modificación / Borrado (Protegido con PIN)"):
        st.markdown("Para realizar cambios o eliminar registros guardados, ingresa tu PIN de 4 dígitos.")
        
        pin_ingresado = st.text_input("Ingresa PIN de seguridad", type="password", max_chars=4, placeholder="****")
        
        if pin_ingresado == PIN_SEGURIDAD:
            st.success("✅ PIN correcto. Zona de modificaciones desbloqueada.")
            
            df_existente['Identificador'] = (
                "Fila " + df_existente.index.astype(str) + 
                " | Línea: " + df_existente['Línea'].astype(str) +
                " | Eq: " + df_existente['Equipo'].astype(str) + 
                " | Mes: " + df_existente['Mes'].astype(str) + 
                " | T: " + df_existente['Temperatura (°C)'].astype(str) + "°C"
            )
            
            registros_a_borrar = st.multiselect(
                "Selecciona los registros que deseas eliminar del historial:",
                options=df_existente['Identificador'].tolist()
            )
            
            if st.button("❌ Borrar seleccionados definitivamente"):
                if registros_a_borrar:
                    indices_a_dropear = []
                    for item in registros_a_borrar:
                        idx_str = item.split(" | ")[0].replace("Fila ", "")
                        indices_a_dropear.append(int(idx_str))
                    
                    df_limpio = df_existente.drop(indices_a_dropear).drop(columns=['Identificador'])
                    guardar_datos_locales(df_limpio)
                    st.success("¡Registros eliminados del documento correctamente!")
                    st.rerun()
                else:
                    st.warning("Selecciona al menos un registro para borrar.")
                    
        elif pin_ingresado != "":
            st.error("❌ PIN incorrecto. No se pueden realizar modificaciones.")
        else:
            st.info("💡 Ingresa el PIN para habilitar la opción de borrado.")

    st.divider()
    
    # Botón para descargar respaldo en CSV
    with open(DB_FILE, "rb") as file:
        st.download_button(
            label="📥 Descargar Base de Datos Acumulada (CSV)",
            data=file,
            file_name="historial_predictivo.csv",
            mime="text/csv"
        )
    
    st.divider()
    
    # --- GRÁFICA DE TENDENCIA EVOLUTIVA (MES A MES) ---
    st.subheader("📉 Evolución Gráfica Mensual por Equipo")
    if 'Equipo' in df_existente.columns and not df_existente['Equipo'].dropna().empty:
        equipos_disponibles = df_existente['Equipo'].dropna().unique()
        equipo_seleccionado = st.selectbox("Selecciona el equipo para ver su comportamiento mes a mes:", equipos_disponibles)
        
        if equipo_seleccionado:
            df_eq = df_existente[df_existente['Equipo'] == equipo_seleccionado].copy()
            
            if 'Fecha' in df_eq.columns:
                df_eq = df_eq.sort_values('Fecha')
                
            st.write(f"Mostrando historial evolutivo para: **{equipo_seleccionado}**")
            
            if len(df_eq) > 0:
                df_eq['Evolución_Mes'] = df_eq['Mes'] + " (" + df_eq['Fecha'].astype(str).str.sub(0, 10) + ")"
                
                chart_data = df_eq.set_index('Evolución_Mes')[['Temperatura (°C)', 'Amperaje (A)', 'Vibración (mm/s)']]
                st.line_chart(chart_data)
                
                st.markdown("Registros históricos de este equipo:")
                st.dataframe(df_eq[['Fecha', 'Línea', 'Mes', 'Temperatura (°C)', 'Amperaje (A)']], use_container_width=True)
            else:
                st.info("Aún no hay suficientes datos históricos para este equipo.")
else:
    st.info("Aún no hay registros en la base de datos. Haz tu primer registro arriba para comenzar a acumular el historial.")

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="Monitoreo Predictivo Integral",
    page_icon="🔒",
    layout="centered"
)

# PIN de seguridad de 4 dígitos para modificaciones/borrados/configuración
PIN_SEGURIDAD = "2026"

# Archivos locales
DB_FILE = "historial_predictivo.csv"
PERF_FILE = "historial_perfileria.csv"
CONFIG_FILE = "perfileria_config.json"

# --- CONFIGURACIÓN Y DATOS DE PERFILERÍA ---
def cargar_config_perfileria():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Configuración predeterminada inicial
    config_default = {
        "lineas": ["Perfilería 1", "Perfilería 2", "Perfilería 3"],
        "zonas": ["Cañón 1", "Cañón 2", "Cañón 3", "Zona 1", "Zona 2", "Zona 3", "Zona 4"]
    }
    guardar_config_perfileria(config_default)
    return config_default

def guardar_config_perfileria(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def cargar_datos_generales():
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

def guardar_datos_generales(df):
    df.to_csv(DB_FILE, index=False)

def cargar_datos_perfileria():
    if os.path.exists(PERF_FILE):
        try:
            return pd.read_csv(PERF_FILE)
        except Exception:
            pass
    df_vacio = pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Zona", "Temperatura (°C)"])
    df_vacio.to_csv(PERF_FILE, index=False)
    return df_vacio

def guardar_datos_perfileria(df):
    df.to_csv(PERF_FILE, index=False)

# --- INTERFAZ PRINCIPAL ---
st.title("🔒 Monitoreo Predictivo Integral")

# Menú superior para alternar entre el módulo General y Perfilería
modo = st.sidebar.radio("Seleccionar Módulo:", ["⚙️ Monitoreo General", "🏭 Perfilería (Extrusión / Zonas)"])

config_perf = cargar_config_perfileria()

if modo == "⚙️ Monitoreo General":
    st.subheader("⚙️ Módulo General (Motores, Bandas, etc.)")
    df_existente = cargar_datos_generales()

    with st.form("registro_general", clear_on_submit=True):
        st.subheader("➕ Agregar Medición General")
        col1, col2 = st.columns(2)
        with col1:
            linea = st.selectbox("Línea", ["Línea 1", "Línea 2", "Línea 3", "Línea Extrusión"])
        with col2:
            equipo = st.text_input("Número de Equipo", placeholder="Ej. Motor M-04")
            
        mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10)
        
        col3, col4, col5 = st.columns(3)
        with col3:
            temp = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f")
        with col4:
            amp = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f")
        with col5:
            vib = st.number_input("Vibración", min_value=0.0, step=0.1, format="%.1f")
            
        submitted = st.form_submit_button("Guardar Medición General")
        if submitted:
            if linea and equipo:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                nueva_fila = pd.DataFrame([{"Fecha": fecha_actual, "Línea": linea, "Equipo": equipo, "Mes": mes, "Temperatura (°C)": temp, "Amperaje (A)": amp, "Vibración (mm/s)": vib}])
                df_act = pd.concat([df_existente, nueva_fila], ignore_index=True)
                guardar_datos_generales(df_act)
                st.success(f"¡Medición guardada para {equipo}!")
                st.rerun()
            else:
                st.error("Completa la Línea y el Equipo.")

    st.divider()
    st.subheader("📊 Histórico General")
    if not df_existente.empty:
        st.dataframe(df_existente, use_container_width=True)
        
        with st.expander("🗑️ Zona de Borrado (Protegido con PIN)"):
            pin = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_gen")
            if pin == PIN_SEGURIDAD:
                st.success("PIN Correcto")
                df_existente['Identificador'] = "Fila " + df_existente.index.astype(str) + " | " + df_existente['Equipo'].astype(str) + " | " + df_existente['Mes'].astype(str)
                a_borrar = st.multiselect("Selecciona filas a borrar:", df_existente['Identificador'].tolist())
                if st.button("Borrar seleccionados Gral"):
                    idxs = [int(x.split(" | ")[0].replace("Fila ", "")) for x in a_borrar]
                    df_limpio = df_existente.drop(idxs).drop(columns=['Identificador'])
                    guardar_datos_generales(df_limpio)
                    st.success("¡Eliminado!")
                    st.rerun()
            elif pin != "":
                st.error("PIN Incorrecto")
    else:
        st.info("Sin registros generales aún.")

else:
    # --- MÓDULO DE PERFILERÍA ---
    st.subheader("🏭 Módulo de Perfilería (Zonas de Cañón)")
    df_perf = cargar_datos_perfileria()

    # Formulario para registrar temperaturas por zona
    with st.form("registro_perfileria", clear_on_submit=True):
        st.subheader("➕ Registro Térmico por Zonas")
        
        col1, col2 = st.columns(2)
        with col1:
            linea_perf = st.selectbox("Línea de Perfilería", config_perf["lineas"])
        with col2:
            equipo_perf = st.text_input("Nombre de Máquina / Extrusora", placeholder="Ej. Extrusora Principal")
            
        mes_perf = st.selectbox("Mes de Medición", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10, key="mes_p")
        
        st.markdown("---")
        st.markdown("🌡️ **Temperaturas por Zona Configurada:**")
        
        # Generar dinámicamente campos de temperatura según las zonas activas
        temperaturas_capturadas = {}
        cols_zonas = st.columns(3)
        for idx, zona in enumerate(config_perf["zonas"]):
            with cols_zonas[idx % 3]:
                temperaturas_capturadas[zona] = st.number_input(f"{zona} (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"z_{zona}")

        submitted_perf = st.form_submit_button("Guardar Temperaturas de Perfilería")
        
        if submitted_perf:
            if linea_perf and equipo_perf:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                filas_nuevas = []
                for zona, temp_val in temperaturas_capturadas.items():
                    filas_nuevas.append({
                        "Fecha": fecha_actual,
                        "Línea": linea_perf,
                        "Equipo": equipo_perf,
                        "Mes": mes_perf,
                        "Zona": zona,
                        "Temperatura (°C)": temp_val
                    })
                df_nuevas = pd.DataFrame(filas_nuevas)
                df_act_perf = pd.concat([df_perf, df_nuevas], ignore_index=True)
                guardar_datos_perfileria(df_act_perf)
                st.success(f"¡Mediciones de perfilería guardadas para **{equipo_perf}** en **{linea_perf}**!")
                st.rerun()
            else:
                st.error("Por favor completa la Línea y el Nombre de la Máquina.")

    st.divider()
    st.subheader("📊 Histórico y Evolución de Perfilería")

    if not df_perf.empty:
        # Filtros de vista
        lineas_p_reg = ["Todas las Líneas"] + list(df_perf['Línea'].dropna().unique())
        f_linea = st.selectbox("🔍 Filtrar por Línea de Perfilería:", lineas_p_reg)
        
        if f_linea != "Todas las Líneas":
            df_perf_filtrado = df_perf[df_perf['Línea'] == f_linea]
        else:
            df_perf_filtrado = df_perf

        st.dataframe(df_perf_filtrado, use_container_width=True)

        # Gráfica de evolución mensual por zona para un equipo de perfilería
        st.subheader("📉 Tendencia de Temperaturas por Zona (Mes a Mes)")
        equipos_perf = df_perf['Equipo'].dropna().unique()
        if len(equipos_perf) > 0:
            eq_p_sel = st.selectbox("Selecciona la máquina/extrusora:", equipos_perf, key="eq_p")
            df_eq_p = df_perf[df_perf['Equipo'] == eq_p_sel].copy()
            
            if 'Fecha' in df_eq_p.columns:
                df_eq_p = df_eq_p.sort_values('Fecha')
                df_eq_p['Evolución_Mes'] = df_eq_p['Mes'] + " (" + df_eq['Fecha'].astype(str).str[:10] + ")"
                
                # Pivotear tabla para que las zonas sean columnas en la gráfica de líneas
                df_pivot = df_eq_p.pivot_table(index='Evolución_Mes', columns='Zona', values='Temperatura (°C)')
                st.line_chart(df_pivot)

    st.divider()

    # --- ZONA DE CONFIGURACIÓN Y BORRADO DE PERFILERÍA (PROTEGIDA CON PIN) ---
    with st.expander("🛠️ Configuración de Líneas/Zonas y Borrado (Protegido con PIN)"):
        st.markdown("Ingresa tu PIN de 4 dígitos para modificar la estructura de perfilería o borrar registros.")
        pin_perf = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_perf")
        
        if pin_perf == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado a configuración de Perfilería.")
            
            st.markdown("### ✏️ Administrar Líneas de Perfilería")
            nueva_linea = st.text_input("Agregar nueva Línea de Perfilería", placeholder="Ej. Perfilería 4")
            if st.button("Añadir Línea"):
                if nueva_linea and nueva_linea not in config_perf["lineas"]:
                    config_perf["lineas"].append(nueva_linea)
                    guardar_config_perfileria(config_perf)
                    st.success(f"Línea '{nueva_linea}' añadida correctamente.")
                    st.rerun()

            linea_a_borrar = st.selectbox("Eliminar Línea existente", ["Selecciona..."] + config_perf["lineas"])
            if st.button("Eliminar Línea seleccionada") and linea_a_borrar != "Selecciona...":
                config_perf["lineas"].remove(linea_a_borrar)
                guardar_config_perfileria(config_perf)
                st.success("Línea eliminada.")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🌡️ Administrar Zonas Térmicas (Cañones / Zonas)")
            nueva_zona = st.text_input("Agregar nueva Zona", placeholder="Ej. Cañón 5 o Zona 5")
            if st.button("Añadir Zona"):
                if nueva_zona and nueva_zona not in config_perf["zonas"]:
                    config_perf["zonas"].append(nueva_zona)
                    guardar_config_perfileria(config_perf)
                    st.success(f"Zona '{nueva_zona}' añadida correctamente.")
                    st.rerun()

            zona_a_borrar = st.selectbox("Eliminar Zona existente", ["Selecciona..."] + config_perf["zonas"])
            if st.button("Eliminar Zona seleccionada") and zona_a_borrar != "Selecciona...":
                config_perf["zonas"].remove(zona_a_borrar)
                guardar_config_perfileria(config_perf)
                st.success("Zona eliminada.")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Borrar Registros de Perfilería")
            if not df_perf.empty:
                df_perf['Identificador'] = "Fila " + df_perf.index.astype(str) + " | " + df_perf['Equipo'].astype(str) + " | Zona: " + df_perf['Zona'].astype(str) + " | " + df_perf['Mes'].astype(str)
                reg_borrar_p = st.multiselect("Selecciona registros de perfilería a borrar:", df_perf['Identificador'].tolist())
                if st.button("Borrar registros de perfilería seleccionados"):
                    idxs_p = [int(x.split(" | ")[0].replace("Fila ", "")) for x in reg_borrar_p]
                    df_perf_limpio = df_perf.drop(idxs_p).drop(columns=['Identificador'])
                    guardar_datos_perfileria(df_perf_limpio)
                    st.success("¡Registros de perfilería eliminados!")
                    st.rerun()
                    
        elif pin_perf != "":
            st.error("❌ PIN incorrecto.")
        else:
            st.info("💡 Ingresa el PIN para desbloquear la gestión de líneas, zonas y borrados.")

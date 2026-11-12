import streamlit as st
import pandas as pd
import os
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
ZONAS_FILE = "zonas_config.csv"
LINEAS_PERF_FILE = "lineas_perf_config.csv"

# --- FUNCIONES DE CONFIGURACIÓN DINÁMICA (CON PERSISTENCIA CSV) ---
def cargar_zonas():
    if os.path.exists(ZONAS_FILE):
        try:
            df = pd.read_csv(ZONAS_FILE)
            if 'Zona' in df.columns:
                return df['Zona'].dropna().tolist()
        except Exception:
            pass
    # Zonas iniciales por defecto
    zonas_default = ["Cañón 1", "Cañón 2", "Cañón 3", "Zona 1", "Zona 2", "Zona 3", "Zona 4"]
    pd.DataFrame({"Zona": zonas_default}).to_csv(ZONAS_FILE, index=False)
    return zonas_default

def guardar_zonas(lista_zonas):
    pd.DataFrame({"Zona": lista_zonas}).to_csv(ZONAS_FILE, index=False)

def cargar_lineas_perf():
    if os.path.exists(LINEAS_PERF_FILE):
        try:
            df = pd.read_csv(LINEAS_PERF_FILE)
            if 'Linea' in df.columns:
                return df['Linea'].dropna().tolist()
        except Exception:
            pass
    lineas_default = ["Perfilería 1", "Perfilería 2", "Perfilería 3"]
    pd.DataFrame({"Linea": lineas_default}).to_csv(LINEAS_PERF_FILE, index=False)
    return lineas_default

def guardar_lineas_perf(lista_lineas):
    pd.DataFrame({"Linea": lista_lineas}).to_csv(LINEAS_PERF_FILE, index=False)

def cargar_datos_generales():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])

def guardar_datos_generales(df):
    df.to_csv(DB_FILE, index=False)

def cargar_datos_perfileria():
    if os.path.exists(PERF_FILE):
        try:
            return pd.read_csv(PERF_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Zona", "Temperatura (°C)"])

def guardar_datos_perfileria(df):
    df.to_csv(PERF_FILE, index=False)

# --- INTERFAZ PRINCIPAL ---
st.title("🔒 Monitoreo Predictivo Integral")

modo = st.sidebar.radio("Seleccionar Módulo:", ["⚙️ Monitoreo General", "🏭 Perfilería (Extrusión / Zonas)"])

zonas_actuales = cargar_zonas()
lineas_perf_actuales = cargar_lineas_perf()

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
        
        with st.expander("🗑️ Zona de Borrado General (Protegido con PIN)"):
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
    st.subheader("🏭 Módulo de Perfilería (Zonas y Cañones)")
    df_perf = cargar_datos_perfileria()

    with st.form("registro_perfileria", clear_on_submit=True):
        st.subheader("➕ Registro Térmico por Zonas")
        
        col1, col2 = st.columns(2)
        with col1:
            linea_perf = st.selectbox("Línea de Perfilería", lineas_perf_actuales)
        with col2:
            equipo_perf = st.text_input("Nombre de Máquina / Extrusora", placeholder="Ej. Extrusora Principal")
            
        mes_perf = st.selectbox("Mes de Medición", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10, key="mes_p")
        
        st.markdown("---")
        st.markdown(f"🌡️ **Temperaturas por Zona Configurada ({len(zonas_actuales)} zonas activas):**")
        
        temperaturas_capturadas = {}
        if len(zonas_actuales) > 0:
            cols_zonas = st.columns(3)
            for idx, zona in enumerate(zonas_actuales):
                with cols_zonas[idx % 3]:
                    temperaturas_capturadas[zona] = st.number_input(f"{zona} (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"z_{zona}")
        else:
            st.warning("No hay zonas configuradas. Ve a la zona protegida abajo para agregar cañones o zonas.")

        submitted_perf = st.form_submit_button("Guardar Temperaturas de Perfilería")
        
        if submitted_perf:
            if linea_perf and equipo_perf and len(zonas_actuales) > 0:
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
                st.success(f"¡Mediciones guardadas para **{equipo_perf}** en **{linea_perf}**!")
                st.rerun()
            else:
                st.error("Completa la Línea, el Equipo y asegúrate de tener al menos una zona configurada.")

    st.divider()
    st.subheader("📊 Histórico y Evolución de Perfilería")

    if not df_perf.empty:
        lineas_p_reg = ["Todas las Líneas"] + list(df_perf['Línea'].dropna().unique())
        f_linea = st.selectbox("🔍 Filtrar por Línea de Perfilería:", lineas_p_reg)
        
        if f_linea != "Todas las Líneas":
            df_perf_filtrado = df_perf[df_perf['Línea'] == f_linea]
        else:
            df_perf_filtrado = df_perf

        st.dataframe(df_perf_filtrado, use_container_width=True)

        st.subheader("📉 Tendencia Térmica por Zona (Mes a Mes)")
        equipos_perf = df_perf['Equipo'].dropna().unique()
        if len(equipos_perf) > 0:
            eq_p_sel = st.selectbox("Selecciona la máquina/extrusora:", equipos_perf, key="eq_p")
            df_eq_p = df_perf[df_perf['Equipo'] == eq_p_sel].copy()
            
            if 'Fecha' in df_eq_p.columns:
                df_eq_p = df_eq_p.sort_values('Fecha')
                df_eq_p['Evolución_Mes'] = df_eq_p['Mes'] + " (" + df_eq['Fecha'].astype(str).str[:10] + ")"
                
                df_pivot = df_eq_p.pivot_table(index='Evolución_Mes', columns='Zona', values='Temperatura (°C)')
                st.line_chart(df_pivot)

    st.divider()

    # --- ZONA DE CONFIGURACIÓN (AGREGAR/QUITAR CAÑONES Y ZONAS) PROTEGIDA CON PIN ---
    with st.expander("🛠️ Configurar Cañones, Zonas y Líneas (Protegido con PIN)"):
        st.markdown("Ingresa tu PIN de 4 dígitos para **agregar o quitar cañones, zonas y líneas** a tu gusto.")
        pin_perf = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_perf")
        
        if pin_perf == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado a configuración de Perfilería.")
            
            # --- ADMINISTRAR ZONAS Y CAÑONES ---
            st.markdown("### 🌡️ Administrar Cañones y Zonas Térmicas")
            st.write("Zonas actuales activas:", zonas_actuales)
            
            nueva_zona = st.text_input("Escribe el nombre del nuevo cañón o zona a agregar", placeholder="Ej. Cañón 4, Zona 5, etc.")
            if st.button("➕ Agregar Cañón / Zona"):
                if nueva_zona and nueva_zona not in zonas_actuales:
                    zonas_actuales.append(nueva_zona)
                    guardar_zonas(zonas_actuales)
                    st.success(f"¡'{nueva_zona}' agregado exitosamente!")
                    st.rerun()
                else:
                    st.warning("Escribe un nombre válido que no esté repetido.")

            zona_a_quitar = st.selectbox("Selecciona un cañón o zona para eliminar", ["Selecciona..."] + zonas_actuales)
            if st.button("❌ Quitar Cañón / Zona seleccionado") and zona_a_quitar != "Selecciona...":
                zonas_actuales.remove(zona_a_quitar)
                guardar_zonas(zonas_actuales)
                st.success(f"'{zona_a_quitar}' eliminado correctamente.")
                st.rerun()

            st.markdown("---")
            # --- ADMINISTRAR LÍNEAS DE PERFILERÍA ---
            st.markdown("### 🏭 Administrar Líneas de Perfilería")
            st.write("Líneas actuales:", lineas_perf_actuales)
            
            nueva_linea_p = st.text_input("Escribe el nombre de la nueva línea de perfilería", placeholder="Ej. Perfilería 4")
            if st.button("➕ Agregar Línea de Perfilería"):
                if nueva_linea_p and nueva_linea_p not in lineas_perf_actuales:
                    lineas_perf_actuales.append(nueva_linea_p)
                    guardar_lineas_perf(lineas_perf_actuales)
                    st.success(f"¡Línea '{nueva_linea_p}' agregada!")
                    st.rerun()

            linea_a_quitar_p = st.selectbox("Selecciona una línea para eliminar", ["Selecciona..."] + lineas_perf_actuales)
            if st.button("❌ Quitar Línea seleccionada") and linea_a_quitar_p != "Selecciona...":
                lineas_perf_actuales.remove(linea_a_quitar_p)
                guardar_lineas_perf(lineas_perf_actuales)
                st.success("Línea eliminada.")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Borrar Registros de Perfilería")
            if not df_perf.empty:
                df_perf['Identificador'] = "Fila " + df_perf.index.astype(str) + " | " + df_perf['Equipo'].astype(str) + " | Zona: " + df_perf['Zona'].astype(str) + " | " + df_perf['Mes'].astype(str)
                reg_borrar_p = st.multiselect("Selecciona registros a borrar:", df_perf['Identificador'].tolist())
                if st.button("Borrar registros seleccionados"):
                    idxs_p = [int(x.split(" | ")[0].replace("Fila ", "")) for x in reg_borrar_p]
                    df_perf_limpio = df_perf.drop(idxs_p).drop(columns=['Identificador'])
                    guardar_datos_perfileria(df_perf_limpio)
                    st.success("¡Registros eliminados!")
                    st.rerun()
                    
        elif pin_perf != "":
            st.error("❌ PIN incorrecto.")
        else:
            st.info("💡 Ingresa el PIN para desbloquear los botones de agregar/quitar cañones y líneas.")

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

# Archivos locales de datos y configuración
CUERDA_FILE = "historial_cuerda.csv"
PERF_FILE = "historial_perfileria.csv"

ZONAS_PERF_FILE = "zonas_config.csv"
LINEAS_PERF_FILE = "lineas_perf_config.csv"
LINEAS_CUERDA_FILE = "lineas_cuerda_config.csv"

# --- FUNCIONES DE CONFIGURACIÓN DINÁMICA ---
def cargar_config(file_path, default_list, col_name):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if col_name in df.columns:
                return df[col_name].dropna().tolist()
        except Exception:
            pass
    pd.DataFrame({col_name: default_list}).to_csv(file_path, index=False)
    return default_list

def guardar_config(file_path, lista, col_name):
    pd.DataFrame({col_name: lista}).to_csv(file_path, index=False)

def cargar_datos_cuerda():
    if os.path.exists(CUERDA_FILE):
        try:
            return pd.read_csv(CUERDA_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=["Fecha", "Línea", "Equipo", "Mes", "Tipo", "Zona", "Temperatura (°C)", "Amperaje (A)", "Vibración (mm/s)"])

def guardar_datos_cuerda(df):
    df.to_csv(CUERDA_FILE, index=False)

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

modo = st.sidebar.radio("Seleccionar Módulo:", ["🧵 Cuerda", "🏭 Perfilería (Extrusión / Zonas)"])

lineas_cuerda = cargar_config(LINEAS_CUERDA_FILE, ["Cuerda 1", "Cuerda 2", "Cuerda 3"], "Linea")
lineas_perf = cargar_config(LINEAS_PERF_FILE, ["Perfilería 1", "Perfilería 2", "Perfilería 3"], "Linea")
zonas_perf = cargar_config(ZONAS_PERF_FILE, ["Cañón 1", "Cañón 2", "Cañón 3", "Zona 1", "Zona 2", "Zona 3", "Zona 4"], "Zona")

if modo == "🧵 Cuerda":
    st.subheader("🧵 Módulo Cuerda")
    df_cuerda = cargar_datos_cuerda()

    with st.form("registro_cuerda", clear_on_submit=True):
        st.subheader("➕ Agregar Medición en Cuerda")
        
        col1, col2 = st.columns(2)
        with col1:
            linea_c = st.selectbox("Línea de Cuerda", lineas_cuerda)
        with col2:
            equipo_c = st.text_input("Nombre de Equipo / Elemento", placeholder="Ej. Motor Principal o EXT-01")
            
        mes_c = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10)
        
        eq_clean = equipo_c.strip().lower()
        es_extrusor = "ext" in eq_clean or "extrusor" in eq_clean
        
        capturas_cuerda = {}
        if es_extrusor:
            st.info(f"💡 Detectado como **Extrusor / EXT**. Ingresa las temperaturas de zona ({len(zonas_perf)} zonas activas):")
            cols_zc = st.columns(3)
            for idx, zona in enumerate(zonas_perf):
                with cols_zc[idx % 3]:
                    capturas_cuerda[zona] = st.number_input(f"{zona} (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"zc_{zona}")
        else:
            st.info("💡 Equipo estándar detectado (Motor, Ventilador, Soplador, etc.).")
            col3, col4, col5 = st.columns(3)
            with col3:
                capturas_cuerda["Temp"] = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key="sc_temp")
            with col4:
                capturas_cuerda["Amp"] = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f", key="sc_amp")
            with col5:
                capturas_cuerda["Vib"] = st.number_input("Vibración", min_value=0.0, step=0.1, format="%.1f", key="sc_vib")
            
        submitted_c = st.form_submit_button("Guardar Medición de Cuerda")
        if submitted_c:
            if linea_c and equipo_c:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                filas_nuevas_c = []
                
                if es_extrusor:
                    for zona, val in capturas_cuerda.items():
                        filas_nuevas_c.append({
                            "Fecha": fecha_actual, "Línea": linea_c, "Equipo": equipo_c, "Mes": mes_c,
                            "Tipo": "Extrusor (Zonas)", "Zona": zona, "Temperatura (°C)": val, "Amperaje (A)": 0.0, "Vibración (mm/s)": 0.0
                        })
                else:
                    filas_nuevas_c.append({
                        "Fecha": fecha_actual, "Línea": linea_c, "Equipo": equipo_c, "Mes": mes_c,
                        "Tipo": "Estándar", "Zona": "General", "Temperatura (°C)": capturas_cuerda.get("Temp", 0.0),
                        "Amperaje (A)": capturas_cuerda.get("Amp", 0.0), "Vibración (mm/s)": capturas_cuerda.get("Vib", 0.0)
                    })
                    
                df_act_c = pd.concat([df_cuerda, pd.DataFrame(filas_nuevas_c)], ignore_index=True)
                guardar_datos_cuerda(df_act_c)
                st.success(f"¡Medición guardada para **{equipo_c}** en **{linea_c}**!")
                st.rerun()
            else:
                st.error("Completa la Línea y el Equipo.")

    st.divider()
    st.subheader("📊 Histórico y Evolución de Cuerda")
    
    if not df_cuerda.empty:
        f_lin_c = st.selectbox("🔍 Filtrar por Línea de Cuerda:", ["Todas las Líneas"] + list(df_cuerda['Línea'].dropna().unique()))
        if f_lin_c != "Todas las Líneas":
            df_c_filt = df_cuerda[df_cuerda['Línea'] == f_lin_c]
        else:
            df_c_filt = df_cuerda
            
        st.dataframe(df_c_filt, use_container_width=True)
        
        st.subheader("📉 Tendencia Evolutiva (Mes a Mes)")
        eqs_c = df_cuerda['Equipo'].dropna().unique()
        if len(eqs_c) > 0:
            eq_sel_c = st.selectbox("Selecciona equipo o extrusor de cuerda:", eqs_c)
            df_eq_c = df_cuerda[df_cuerda['Equipo'] == eq_sel_c].copy()
            if 'Fecha' in df_eq_c.columns:
                df_eq_c = df_eq_c.sort_values('Fecha')
                df_eq_c['Evolución_Mes'] = df_eq_c['Mes'] + " (" + df_eq_c['Fecha'].astype(str).str[:10] + ")"
                
                if "ext" in eq_sel_c.lower() or "extrusor" in eq_sel_c.lower():
                    df_pivot_c = df_eq_c.pivot_table(index='Evolución_Mes', columns='Zona', values='Temperatura (°C)')
                    st.line_chart(df_pivot_c)
                else:
                    chart_data_c = df_eq_c.set_index('Evolución_Mes')[['Temperatura (°C)', 'Amperaje (A)', 'Vibración (mm/s)']]
                    st.line_chart(chart_data_c)

    st.divider()

    # --- ZONA DE CONFIGURACIÓN DE CUERDA (PROTEGIDA CON PIN) ---
    with st.expander("🛠️ Configurar Líneas, Cañones/Zonas y Borrado de Cuerda (Protegido con PIN)"):
        st.markdown("Ingresa tu PIN de 4 dígitos para **administrar líneas, zonas de extrusores o borrar registros**.")
        pin_c = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_c")
        
        if pin_c == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado.")
            
            # 1. Administrar Cañones y Zonas también en Cuerda
            st.markdown("### 🌡️ Administrar Cañones y Zonas Térmicas (Extrusores)")
            st.write("Zonas actuales activas:", zonas_perf)
            nueva_zona_c = st.text_input("Escribe el nuevo cañón o zona", placeholder="Ej. Cañón 4, Zona 5", key="nz_c")
            if st.button("➕ Agregar Cañón / Zona en Cuerda"):
                if nueva_zona_c and nueva_zona_c not in zonas_perf:
                    zonas_perf.append(nueva_zona_c)
                    guardar_config(ZONAS_PERF_FILE, zonas_perf, "Zona")
                    st.success("¡Zona agregada exitosamente!")
                    st.rerun()

            zona_a_quitar_c = st.selectbox("Eliminar Cañón o Zona", ["Selecciona..."] + zonas_perf, key="zq_c")
            if st.button("❌ Quitar Zona seleccionada en Cuerda") and zona_a_quitar_c != "Selecciona...":
                zonas_perf.remove(zona_a_quitar_c)
                guardar_config(ZONAS_PERF_FILE, zonas_perf, "Zona")
                st.success("Zona eliminada.")
                st.rerun()

            st.markdown("---")
            # 2. Líneas de Cuerda
            st.markdown("### 🧵 Administrar Líneas de Cuerda")
            st.write("Líneas actuales:", lineas_cuerda)
            nueva_l_c = st.text_input("Agregar nueva Línea de Cuerda", placeholder="Ej. Cuerda 4")
            if st.button("➕ Agregar Línea de Cuerda"):
                if nueva_l_c and nueva_l_c not in lineas_cuerda:
                    lineas_cuerda.append(nueva_l_c)
                    guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                    st.success("¡Línea añadida!")
                    st.rerun()
            
            del_l_c = st.selectbox("Eliminar Línea de Cuerda", ["Selecciona..."] + lineas_cuerda, key="del_lc")
            if st.button("❌ Quitar Línea seleccionada") and del_l_c != "Selecciona...":
                lineas_cuerda.remove(del_l_c)
                guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                st.success("Línea eliminada.")
                st.rerun()

            st.markdown("---")
            # 3. Borrar Registros
            st.markdown("### 🗑️ Borrar Registros de Cuerda")
            if not df_cuerda.empty:
                df_cuerda['Identificador'] = "Fila " + df_cuerda.index.astype(str) + " | " + df_cuerda['Línea'].astype(str) + " | " + df_cuerda['Equipo'].astype(str) + " | " + df_cuerda['Mes'].astype(str)
                reg_b_c = st.multiselect("Selecciona registros a borrar:", df_cuerda['Identificador'].tolist())
                if st.button("Borrar registros de Cuerda seleccionados"):
                    idxs_c = [int(x.split(" | ")[0].replace("Fila ", "")) for x in reg_b_c]
                    df_c_limpio = df_cuerda.drop(idxs_c).drop(columns=['Identificador'])
                    guardar_datos_cuerda(df_c_limpio)
                    st.success("¡Registros eliminados!")
                    st.rerun()

        elif pin_c != "":
            st.error("❌ PIN incorrecto.")
        else:
            st.info("💡 Ingresa el PIN para desbloquear la gestión.")

else:
    # --- MÓDULO DE PERFILERÍA ---
    st.subheader("🏭 Módulo de Perfilería (Zonas y Cañones)")
    df_perf = cargar_datos_perfileria()

    with st.form("registro_perfileria", clear_on_submit=True):
        st.subheader("➕ Registro Térmico por Zonas")
        
        col1, col2 = st.columns(2)
        with col1:
            linea_perf = st.selectbox("Línea de Perfilería", lineas_perf)
        with col2:
            equipo_perf = st.text_input("Nombre de Máquina / Extrusora", placeholder="Ej. Extrusora Principal")
            
        mes_perf = st.selectbox("Mes de Medición", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10, key="mes_p")
        
        st.markdown("---")
        st.markdown(f"🌡️ **Temperaturas por Zona Configurada ({len(zonas_perf)} zonas activas):**")
        
        temperaturas_capturadas = {}
        if len(zonas_perf) > 0:
            cols_zonas = st.columns(3)
            for idx, zona in enumerate(zonas_perf):
                with cols_zonas[idx % 3]:
                    temperaturas_capturadas[zona] = st.number_input(f"{zona} (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"z_{zona}")
        else:
            st.warning("No hay zonas configuradas. Ve a la zona protegida abajo para agregarlas.")

        submitted_perf = st.form_submit_button("Guardar Temperaturas de Perfilería")
        
        if submitted_perf:
            if linea_perf and equipo_perf and len(zonas_perf) > 0:
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
                df_eq_p['Evolución_Mes'] = df_eq_p['Mes'] + " (" + df_eq_p['Fecha'].astype(str).str[:10] + ")"
                
                df_pivot = df_eq_p.pivot_table(index='Evolución_Mes', columns='Zona', values='Temperatura (°C)')
                st.line_chart(df_pivot)

    st.divider()

    # --- ZONA DE CONFIGURACIÓN DE PERFILERÍA (PROTEGIDA CON PIN) ---
    with st.expander("🛠️ Configurar Cañones, Zonas y Líneas de Perfilería (Protegido con PIN)"):
        st.markdown("Ingresa tu PIN de 4 dígitos para **agregar o quitar cañones, zonas y líneas** de perfilería.")
        pin_perf = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_perf")
        
        if pin_perf == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado.")
            
            # Zonas / Cañones
            st.markdown("### 🌡️ Administrar Cañones y Zonas Térmicas")
            st.write("Zonas actuales activas:", zonas_perf)
            nueva_zona = st.text_input("Escribe el nuevo cañón o zona", placeholder="Ej. Cañón 4, Zona 5")
            if st.button("➕ Agregar Cañón / Zona"):
                if nueva_zona and nueva_zona not in zonas_perf:
                    zonas_perf.append(nueva_zona)
                    guardar_config(ZONAS_PERF_FILE, zonas_perf, "Zona")
                    st.success("¡Zona agregada!")
                    st.rerun()

            zona_a_quitar = st.selectbox("Eliminar Cañón o Zona", ["Selecciona..."] + zonas_perf)
            if st.button("❌ Quitar Zona seleccionada") and zona_a_quitar != "Selecciona...":
                zonas_perf.remove(zona_a_quitar)
                guardar_config(ZONAS_PERF_FILE, zonas_perf, "Zona")
                st.success("Zona eliminada.")
                st.rerun()

            st.markdown("---")
            # Líneas de Perfilería
            st.markdown("### 🏭 Administrar Líneas de Perfilería")
            st.write("Líneas actuales:", lineas_perf)
            nueva_linea_p = st.text_input("Escribe la nueva línea de perfilería", placeholder="Ej. Perfilería 4")
            if st.button("➕ Agregar Línea de Perfilería"):
                if nueva_linea_p and nueva_linea_p not in lineas_perf:
                    lineas_perf.append(nueva_linea_p)
                    guardar_config(LINEAS_PERF_FILE, lineas_perf, "Linea")
                    st.success("¡Línea agregada!")
                    st.rerun()

            linea_a_quitar_p = st.selectbox("Eliminar Línea de Perfilería", ["Selecciona..."] + lineas_perf)
            if st.button("❌ Quitar Línea de Perfilería seleccionada") and linea_a_quitar_p != "Selecciona...":
                lineas_perf.remove(linea_a_quitar_p)
                guardar_config(LINEAS_PERF_FILE, lineas_perf, "Linea")
                st.success("Línea eliminada.")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Borrar Registros de Perfilería")
            if not df_perf.empty:
                df_perf['Identificador'] = "Fila " + df_perf.index.astype(str) + " | " + df_perf['Equipo'].astype(str) + " | Zona: " + df_perf['Zona'].astype(str) + " | " + df_perf['Mes'].astype(str)
                reg_borrar_p = st.multiselect("Selecciona registros a borrar:", df_perf['Identificador'].tolist())
                if st.button("Borrar registros de perfilería seleccionados"):
                    idxs_p = [int(x.split(" | ")[0].replace("Fila ", "")) for x in reg_borrar_p]
                    df_perf_limpio = df_perf.drop(idxs_p).drop(columns=['Identificador'])
                    guardar_datos_perfileria(df_perf_limpio)
                    st.success("¡Registros eliminados!")
                    st.rerun()
                    
        elif pin_perf != "":
            st.error("❌ PIN incorrecto.")
        else:
            st.info("💡 Ingresa el PIN para desbloquear la gestión de Perfilería.")

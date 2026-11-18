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
CUERDA_FILE = "historial_cuerda_detallado.csv"
PERF_FILE = "historial_perfileria.csv"

ZONAS_PERF_FILE = "zonas_config.csv"
LINEAS_PERF_FILE = "lineas_perf_config.csv"
LINEAS_CUERDA_FILE = "lineas_cuerda_config.csv"
EQUIPOS_CUERDA_FILE = "equipos_cuerda_config.csv"
EMBOB_CUERDA_FILE = "embobinadoras_config.csv"
SUBSISTEMAS_CUERDA_FILE = "subsistemas_config.csv"

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
    return pd.DataFrame(columns=["Fecha", "Línea", "Extrusora", "Mes", "Sección", "Sub_Elemento", "Métrica", "Valor"])

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

lineas_cuerda = cargar_config(LINEAS_CUERDA_FILE, ["Línea 1", "Línea 2", "Línea 3", "Línea 4", "Línea 5"], "Linea")
equipos_cuerda = cargar_config(EQUIPOS_CUERDA_FILE, ["Extrusora 17", "Extrusora 04", "Extrusora 03", "Extrusora 05"], "Equipo")
embobinadoras_cuerda = cargar_config(EMBOB_CUERDA_FILE, ["Embobinadora 1", "Embobinadora 2"], "Embobinadora")
subsistemas_cuerda = cargar_config(SUBSISTEMAS_CUERDA_FILE, [
    "Motor extrusor", "Godet 1", "Godet 2", "Bomba de engranes", 
    "Extractor", "Secador", "Mezcladora", "Soplador"
], "Subsistema")

lineas_perf = cargar_config(LINEAS_PERF_FILE, ["Perfilería 1", "Perfilería 2", "Perfilería 3"], "Linea")
zonas_perf = cargar_config(ZONAS_PERF_FILE, ["Cañón 1", "Cañón 2", "Cañón 3", "Zona 1", "Zona 2", "Zona 3", "Zona 4"], "Zona")

if modo == "🧵 Cuerda":
    st.subheader("🧵 Módulo Cuerda (Detallado por Extrusora)")
    df_cuerda = cargar_datos_cuerda()

    with st.form("registro_cuerda_detallado", clear_on_submit=True):
        st.subheader("➕ Registro Completo de Línea y Extrusora")
        
        col1, col2 = st.columns(2)
        with col1:
            linea_c = st.selectbox("Línea de Cuerda", lineas_cuerda)
        with col2:
            extrusora_c = st.selectbox("Extrusora", equipos_cuerda)
            
        mes_c = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10)
        
        # --- 1. SUBSISTEMAS PRINCIPALES DINÁMICOS ---
        st.markdown("---")
        st.markdown("⚙️ **1. Subsistemas Principales de la Extrusora**")
        
        datos_subsistemas = {}
        for sub in subsistemas_cuerda:
            st.markdown(f"**🔹 {sub}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                t = st.number_input(f"Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{sub}")
            with c2:
                a = st.number_input(f"Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{sub}")
            with c3:
                v = st.number_input(f"Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{sub}")
            datos_subsistemas[sub] = {"Temp": t, "Amp": a, "Vib": v}

        # --- 2. HORNO SECADOR ---
        st.markdown("---")
        st.markdown("🔥 **2. Horno Secador**")
        
        st.markdown("🔹 *Sopladores del Horno*")
        sopladores_horno = {}
        for sop in ["Soplador 1", "Soplador 2"]:
            st.markdown(f"**🔹 {sop}**")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st_t = st.number_input(f"Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{sop}")
            with sc2:
                st_a = st.number_input(f"Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{sop}")
            with sc3:
                st_v = st.number_input(f"Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{sop}")
            sopladores_horno[sop] = {"Temp": st_t, "Amp": st_a, "Vib": st_v}

        st.markdown("🔹 *Zonas Térmicas del Horno (con Sub-líneas 1, 2 y 3)*")
        zonas_horno_datos = {}
        for z_num in ["Zona 1", "Zona 2", "Zona 3", "Zona 4"]:
            st.markdown(f"*{z_num}*")
            zc1, zc2, zc3 = st.columns(3)
            with zc1:
                l1_val = st.number_input(f"{z_num} - Línea 1 (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"{z_num}_l1")
            with zc2:
                l2_val = st.number_input(f"{z_num} - Línea 2 (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"{z_num}_l2")
            with zc3:
                l3_val = st.number_input(f"{z_num} - Línea 3 (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"{z_num}_l3")
            zonas_horno_datos[z_num] = {"Línea 1": l1_val, "Línea 2": l2_val, "Línea 3": l3_val}

        # --- 3. EMBOBINADORAS ---
        st.markdown("---")
        st.markdown("🌀 **3. Embobinadoras (11 valores de Amperaje por cada una)**")
        
        embobinadoras_datos = {}
        for emb in embobinadoras_cuerda:
            st.markdown(f"**🔹 {emb}**")
            amps_emb = []
            ec_cols = st.columns(4)
            for i in range(1, 12):
                with ec_cols[(i - 1) % 4]:
                    val_amp = st.number_input(f"Val {i} (A)", min_value=0.0, step=0.1, format="%.1f", key=f"{emb}_val_{i}")
                    amps_emb.append(val_amp)
            embobinadoras_datos[emb] = amps_emb

        submitted_c = st.form_submit_button("Guardar Registro Completo de Extrusora")
        
        if submitted_c:
            if linea_c and extrusora_c:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                registros_nuevos = []
                
                for sub, vals in datos_subsistemas.items():
                    for met, val in vals.items():
                        registros_nuevos.append({
                            "Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c,
                            "Sección": "Subsistemas", "Sub_Elemento": sub, "Métrica": met, "Valor": val
                        })
                
                for sop, vals in sopladores_horno.items():
                    for met, val in vals.items():
                        registros_nuevos.append({
                            "Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c,
                            "Sección": "Horno - Sopladores", "Sub_Elemento": sop, "Métrica": met, "Valor": val
                        })

                for zona, lineas_dict in zonas_horno_datos.items():
                    for lin_name, val in lineas_dict.items():
                        registros_nuevos.append({
                            "Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c,
                            "Sección": "Horno - Zonas Térmicas", "Sub_Elemento": f"{zona} ({lin_name})", "Métrica": "Amp", "Valor": val
                        })

                for emb, amps in embobinadoras_datos.items():
                    for idx, val in enumerate(amps, start=1):
                        registros_nuevos.append({
                            "Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c,
                            "Sección": "Embobinadoras", "Sub_Elemento": f"{emb}", "Métrica": f"Val {idx} (Amp)", "Valor": val
                        })

                df_act_c = pd.concat([df_cuerda, pd.DataFrame(registros_nuevos)], ignore_index=True)
                guardar_datos_cuerda(df_act_c)
                st.success(f"¡Registro completo guardado y congelado para **{extrusora_c}** en **{linea_c}**!")
                st.rerun()
            else:
                st.error("Por favor completa la Línea y la Extrusora.")

    st.divider()
    st.subheader("📊 Histórico de Cuerda")
    
    if not df_cuerda.empty:
        f_lin_c = st.selectbox("🔍 Filtrar por Línea de Cuerda:", ["Todas las Líneas"] + list(df_cuerda['Línea'].dropna().unique()))
        if f_lin_c != "Todas las Líneas":
            df_c_filt = df_cuerda[df_cuerda['Línea'] == f_lin_c]
        else:
            df_c_filt = df_cuerda
            
        st.dataframe(df_c_filt, use_container_width=True)

    st.divider()

    # --- ZONA DE CONFIGURACIÓN Y BORRADO (FUERA DE FORMULARIO PARA FUNCIONAR AL 100%) ---
    with st.expander("🛠️ Configurar Nombres, Líneas, Extrusoras y Borrado (Protegido con PIN)"):
        st.markdown("Ingresa tu PIN de 4 dígitos para **modificar nombres de subsistemas, agregar/quitar elementos o borrar registros**.")
        pin_c = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_c")
        
        if pin_c == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado.")
            
            # --- MODIFICAR / RENOMBRAR SUBSISTEMAS ---
            st.markdown("### ✏️ Renombrar Subsistemas Actuales")
            sub_a_editar = st.selectbox("Selecciona un subsistema a modificar", subsistemas_cuerda, key="sub_edit_sel")
            nuevo_nombre_sub = st.text_input("Escribe el nuevo nombre para este subsistema", value=sub_a_editar, key="nuevo_sub_txt")
            
            if st.button("💾 Guardar Nuevo Nombre"):
                if nuevo_nombre_sub and nuevo_nombre_sub not in subsistemas_cuerda:
                    idx = subsistemas_cuerda.index(sub_a_editar)
                    subsistemas_cuerda[idx] = nuevo_nombre_sub
                    guardar_config(SUBSISTEMAS_CUERDA_FILE, subsistemas_cuerda, "Subsistema")
                    st.success(f"¡Cambiado exitosamente a '{nuevo_nombre_sub}'!")
                    st.rerun()
                else:
                    st.warning("Escribe un nombre válido y diferente.")

            st.markdown("---")
            st.markdown("### ➕ Agregar / Quitar Subsistemas")
            nuevo_sub = st.text_input("Agregar nuevo subsistema", placeholder="Ej. Extractor 2", key="add_sub_txt")
            if st.button("➕ Agregar Subsistema"):
                if nuevo_sub and nuevo_sub not in subsistemas_cuerda:
                    subsistemas_cuerda.append(nuevo_sub)
                    guardar_config(SUBSISTEMAS_CUERDA_FILE, subsistemas_cuerda, "Subsistema")
                    st.success("¡Subsistema añadido!")
                    st.rerun()

            del_sub = st.selectbox("Eliminar Subsistema", ["Selecciona..."] + subsistemas_cuerda, key="del_sub")
            if st.button("❌ Quitar Subsistema seleccionado") and del_sub != "Selecciona...":
                subsistemas_cuerda.remove(del_sub)
                guardar_config(SUBSISTEMAS_CUERDA_FILE, subsistemas_cuerda, "Subsistema")
                st.success("Subsistema eliminado.")
                st.rerun()

            st.markdown("---")
            # --- LÍNEAS ---
            st.markdown("### 🧵 Administrar Líneas de Cuerda")
            st.write("Líneas actuales:", lineas_cuerda)
            
            linea_a_editar = st.selectbox("Selecciona una línea a modificar", lineas_cuerda, key="lin_edit_sel")
            nuevo_nombre_lin = st.text_input("Nuevo nombre de la línea", value=linea_a_editar, key="nuevo_lin_txt")
            if st.button("💾 Guardar Línea"):
                if nuevo_nombre_lin and nuevo_nombre_lin not in lineas_cuerda:
                    idx = lineas_cuerda.index(linea_a_editar)
                    lineas_cuerda[idx] = nuevo_nombre_lin
                    guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                    st.success("¡Línea actualizada!")
                    st.rerun()

            nueva_l_c = st.text_input("Agregar nueva Línea", placeholder="Ej. Línea 6", key="add_l_txt")
            if st.button("➕ Agregar Línea"):
                if nueva_l_c and nueva_l_c not in lineas_cuerda:
                    lineas_cuerda.append(nueva_l_c)
                    guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                    st.success("¡Línea añadida!")
                    st.rerun()
            
            del_l_c = st.selectbox("Eliminar Línea", ["Selecciona..."] + lineas_cuerda, key="del_lc")
            if st.button("❌ Quitar Línea seleccionada") and del_l_c != "Selecciona...":
                lineas_cuerda.remove(del_l_c)
                guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                st.success("Línea eliminada.")
                st.rerun()

            st.markdown("---")
            # --- EXTRUSORAS ---
            st.markdown("### 🏭 Administrar Extrusoras")
            st.write("Extrusoras actuales:", equipos_cuerda)
            
            ext_a_editar = st.selectbox("Selecciona una extrusora a modificar", equipos_cuerda, key="ext_edit_sel")
            nuevo_nombre_ext = st.text_input("Nuevo nombre de la extrusora", value=ext_a_editar, key="nuevo_ext_txt")
            if st.button("💾 Guardar Extrusora"):
                if nuevo_nombre_ext and nuevo_nombre_ext not in equipos_cuerda:
                    idx = equipos_cuerda.index(ext_a_editar)
                    equipos_cuerda[idx] = nuevo_nombre_ext
                    guardar_config(EQUIPOS_CUERDA_FILE, equipos_cuerda, "Equipo")
                    st.success("¡Extrusora actualizada!")
                    st.rerun()

            nuevo_eq_c = st.text_input("Agregar nueva Extrusora", placeholder="Ej. Extrusora 17", key="add_ext_txt")
            if st.button("➕ Agregar Extrusora"):
                if nuevo_eq_c and nuevo_eq_c not in equipos_cuerda:
                    equipos_cuerda.append(nuevo_eq_c)
                    guardar_config(EQUIPOS_CUERDA_FILE, equipos_cuerda, "Equipo")
                    st.success("¡Extrusora añadida!")
                    st.rerun()

            del_eq_c = st.selectbox("Eliminar Extrusora", ["Selecciona..."] + equipos_cuerda, key="del_eqc")
            if st.button("❌ Quitar Extrusora seleccionada") and del_eq_c != "Selecciona...":
                equipos_cuerda.remove(del_eq_c)
                guardar_config(EQUIPOS_CUERDA_FILE, equipos_cuerda, "Equipo")
                st.success("Extrusora eliminada.")
                st.rerun()

            st.markdown("---")
            # --- EMBOBINADORAS ---
            st.markdown("### 🌀 Administrar Embobinadoras")
            st.write("Embobinadoras actuales:", embobinadoras_cuerda)
            
            emb_a_editar = st.selectbox("Selecciona una embobinadora a modificar", embobinadoras_cuerda, key="emb_edit_sel")
            nuevo_nombre_emb = st.text_input("Nuevo nombre de la embobinadora", value=emb_a_editar, key="nuevo_emb_txt")
            if st.button("💾 Guardar Embobinadora"):
                if nuevo_nombre_emb and nuevo_nombre_emb not in embobinadoras_cuerda:
                    idx = embobinadoras_cuerda.index(emb_a_editar)
                    embobinadoras_cuerda[idx] = nuevo_nombre_emb
                    guardar_config(EMBOB_CUERDA_FILE, embobinadoras_cuerda, "Embobinadora")
                    st.success("¡Embobinadora actualizada!")
                    st.rerun()

            nueva_emb = st.text_input("Agregar nueva Embobinadora", placeholder="Ej. Embobinadora 3", key="add_emb_txt")
            if st.button("➕ Agregar Embobinadora"):
                if nueva_emb and nueva_emb not in embobinadoras_cuerda:
                    embobinadoras_cuerda.append(nueva_emb)
                    guardar_config(EMBOB_CUERDA_FILE, embobinadoras_cuerda, "Embobinadora")
                    st.success("¡Embobinadora añadida!")
                    st.rerun()

            del_emb = st.selectbox("Eliminar Embobinadora", ["Selecciona..."] + embobinadoras_cuerda, key="del_emb")
            if st.button("❌ Quitar Embobinadora seleccionada") and del_emb != "Selecciona...":
                embobinadoras_cuerda.remove(del_emb)
                guardar_config(EMBOB_CUERDA_FILE, embobinadoras_cuerda, "Embobinadora")
                st.success("Embobinadora eliminada.")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Borrar Registros de Cuerda")
            if not df_cuerda.empty:
                df_cuerda['Identificador'] = "Fila " + df_cuerda.index.astype(str) + " | " + df_cuerda['Línea'].astype(str) + " | Ext: " + df_cuerda['Extrusora'].astype(str) + " | " + df_cuerda['Mes'].astype(str)
                reg_b_c = st.multiselect("Selecciona registros a borrar:", df_cuerda['Identificador'].unique().tolist())
                if st.button("Borrar registros de Cuerda seleccionados"):
                    idxs_c = []
                    for item in reg_b_c:
                        idx_num = int(item.split(" | ")[0].replace("Fila ", ""))
                        idxs_c.append(idx_num)
                    df_c_limpio = df_cuerda.drop(df_cuerda.index[idxs_c]).drop(columns=['Identificador'])
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
            st.markdown("### 🏭 Administrar Líneas de Perfilería")
            st.write("Líneas actuales:", lineas_perf)
            nueva_linea_p = st.text_input("Escribe la nueva línea de perfilería", placeholder="Ej. Perfilería 4")
            if st.button("➕ Agregar Línea de Perfilería"):
                if nueva_linea_p and nueva_linea_p not in lineas_perf:
                    lineas_perf.append(nueva_linea_p)
                    guardar_config(LINEAS_PERF_FILE, lineas_perf, "Linea")
                    st.success("¡Línea añadida!")
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

import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Monitoreo Predictivo Integral",
    page_icon="🔒",
    layout="centered"
)

PIN_SEGURIDAD = "2026"

# Archivos de datos y configuración
CUERDA_FILE = "historial_cuerda_detallado.csv"
PERF_FILE = "historial_perfileria_detallado.csv"

# Configuración Cuerda
LINEAS_CUERDA_FILE = "lineas_cuerda_config.csv"
EQUIPOS_CUERDA_FILE = "equipos_cuerda_config.csv"
EMBOB_CUERDA_FILE = "embobinadoras_config.csv"
SUBSISTEMAS_CUERDA_FILE = "subsistemas_config.csv"

# Configuración Perfilería
LINEAS_PERF_FILE = "lineas_perf_config.csv"
EXT_PERF_FILE = "ext_perf_config.csv"
ZONAS_PERF_FILE = "zonas_perf_config.csv"
MOLDES_PERF_FILE = "moldes_perf_config.csv"
TINAS_PERF_FILE = "tinas_perf_config.csv"
GENERAL_PERF_FILE = "general_perf_config.csv"

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

def cargar_datos(file_path, cols):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def guardar_datos(file_path, df):
    df.to_csv(file_path, index=False)

# --- CARGAR CONFIGURACIONES ---
lineas_cuerda = cargar_config(LINEAS_CUERDA_FILE, ["Línea 1", "Línea 2", "Línea 3", "Línea 4", "Línea 5"], "Linea")
equipos_cuerda = cargar_config(EQUIPOS_CUERDA_FILE, ["Extrusora 17", "Extrusora 04", "Extrusora 03", "Extrusora 05"], "Equipo")
embobinadoras_cuerda = cargar_config(EMBOB_CUERDA_FILE, ["Embobinadora 1", "Embobinadora 2"], "Embobinadora")
subsistemas_cuerda = cargar_config(SUBSISTEMAS_CUERDA_FILE, ["Motor extrusor", "Godet 1", "Godet 2", "Bomba de engranes", "Extractor", "Secador", "Mezcladora", "Soplador"], "Subsistema")

# Opciones actualizadas forzadas para Perfilería
lineas_perf = cargar_config(LINEAS_PERF_FILE, ["PPR", "CPVC", "PVC", "Tubo hidráulico", "Tubo de estante"], "Linea")
ext_perf = cargar_config(EXT_PERF_FILE, ["Extrusora 43", "Extrusora 44", "Extrusora 45"], "Extrusora")
zonas_perf = cargar_config(ZONAS_PERF_FILE, ["Z1", "Z2", "Z3", "Z4"], "Zona")
moldes_perf = cargar_config(MOLDES_PERF_FILE, ["Molde 1", "Molde 2", "Molde 3", "Molde 4", "Molde 5", "Molde 6", "Molde 7", "Molde 8"], "Molde")
tinas_perf = cargar_config(TINAS_PERF_FILE, ["17 tina 34", "17 tina 33"], "Tina")
generales_perf = cargar_config(GENERAL_PERF_FILE, ["Banda 1", "Banda 2", "Cortadora 1", "Cortadora 2"], "General")

st.title("🔒 Monitoreo Predictivo Integral")
modo = st.sidebar.radio("Seleccionar Módulo:", ["🧵 Cuerda", "🏭 Perfilería"])

if modo == "🧵 Cuerda":
    st.subheader("🧵 Módulo Cuerda (Detallado por Extrusora)")
    df_cuerda = cargar_datos(CUERDA_FILE, ["Fecha", "Línea", "Extrusora", "Mes", "Sección", "Sub_Elemento", "Métrica", "Valor"])

    with st.form("registro_cuerda_detallado", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            linea_c = st.selectbox("Línea de Cuerda", lineas_cuerda)
        with col2:
            extrusora_c = st.selectbox("Extrusora", equipos_cuerda)
            
        mes_c = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10)
        
        st.markdown("---")
        st.markdown("⚙️ **1. Subsistemas Principales de la Extrusora**")
        datos_subsistemas = {}
        for sub in subsistemas_cuerda:
            st.markdown(f"**🔹 {sub}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                t = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{sub}")
            with c2:
                a = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{sub}")
            with c3:
                v = st.number_input("Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{sub}")
            datos_subsistemas[sub] = {"Temp": t, "Amp": a, "Vib": v}

        st.markdown("---")
        st.markdown("🔥 **2. Horno Secador**")
        sopladores_horno = {}
        for sop in ["Soplador 1", "Soplador 2"]:
            st.markdown(f"**🔹 {sop}**")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st_t = st.number_input("Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{sop}")
            with sc2:
                st_a = st.number_input("Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{sop}")
            with sc3:
                st_v = st.number_input("Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{sop}")
            sopladores_horno[sop] = {"Temp": st_t, "Amp": st_a, "Vib": st_v}

        st.markdown("🔹 *Zonas Térmicas del Horno (Líneas 1, 2 y 3)*")
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

        st.markdown("---")
        st.markdown("🌀 **3. Embobinadoras (11 valores de Amperaje)**")
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

        submitted_c = st.form_submit_button("Guardar Registro Completo de Cuerda")
        if submitted_c:
            if linea_c and extrusora_c:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                registros_nuevos = []
                for sub, vals in datos_subsistemas.items():
                    for met, val in vals.items():
                        registros_nuevos.append({"Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c, "Sección": "Subsistemas", "Sub_Elemento": sub, "Métrica": met, "Valor": val})
                for sop, vals in sopladores_horno.items():
                    for met, val in vals.items():
                        registros_nuevos.append({"Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c, "Sección": "Horno - Sopladores", "Sub_Elemento": sop, "Métrica": met, "Valor": val})
                for zona, lineas_dict in zonas_horno_datos.items():
                    for lin_name, val in lineas_dict.items():
                        registros_nuevos.append({"Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c, "Sección": "Horno - Zonas Térmicas", "Sub_Elemento": f"{zona} ({lin_name})", "Métrica": "Amp", "Valor": val})
                for emb, amps in embobinadoras_datos.items():
                    for idx, val in enumerate(amps, start=1):
                        registros_nuevos.append({"Fecha": fecha_actual, "Línea": linea_c, "Extrusora": extrusora_c, "Mes": mes_c, "Sección": "Embobinadoras", "Sub_Elemento": f"{emb}", "Métrica": f"Val {idx} (Amp)", "Valor": val})

                df_act_c = pd.concat([df_cuerda, pd.DataFrame(registros_nuevos)], ignore_index=True)
                guardar_datos(CUERDA_FILE, df_act_c)
                st.success(f"¡Registro guardado para **{extrusora_c}** en **{linea_c}**!")
                st.rerun()

    st.divider()
    with st.expander("🛠️ Configuración Módulo Cuerda (Protegido con PIN)"):
        pin_c = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_c")
        if pin_c == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado.")
            sub_ed = st.selectbox("Editar Subsistema", subsistemas_cuerda, key="se")
            n_sub = st.text_input("Nuevo nombre", value=sub_ed, key="nse")
            if st.button("💾 Guardar Subsistema"):
                subsistemas_cuerda[subsistemas_cuerda.index(sub_ed)] = n_sub
                guardar_config(SUBSISTEMAS_CUERDA_FILE, subsistemas_cuerda, "Subsistema")
                st.rerun()
            lin_ed = st.selectbox("Editar Línea Cuerda", lineas_cuerda, key="le")
            n_lin = st.text_input("Nuevo nombre línea", value=lin_ed, key="nle")
            if st.button("💾 Guardar Línea"):
                lineas_cuerda[lineas_cuerda.index(lin_ed)] = n_lin
                guardar_config(LINEAS_CUERDA_FILE, lineas_cuerda, "Linea")
                st.rerun()
        elif pin_c != "":
            st.error("PIN Incorrecto")

else:
    # --- MÓDULO DE PERFILERÍA ---
    st.subheader("🏭 Módulo Perfilería (Detallado)")
    df_perf = cargar_datos(PERF_FILE, ["Fecha", "Tipo_Sistema", "Extrusora/Sección", "Sub_Elemento", "Mes", "Métrica", "Valor"])

    with st.form("registro_perfileria_detallado", clear_on_submit=True):
        tipo_sistema = st.selectbox("Tipo de Sistema / Línea", lineas_perf)
        mes_p = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=10, key="mes_per")
        
        st.markdown("---")
        st.markdown("🏭 **1. Extrusoras (Zonas Z1-Z4, Brida y Conector)**")
        extrusoras_datos = {}
        for ext in ext_perf:
            st.markdown(f"**🔹 {ext}**")
            ext_vals = {}
            for z in zonas_perf:
                ext_vals[z] = st.number_input(f"{ext} - {z} (Amp/Temp)", min_value=0.0, step=0.1, format="%.1f", key=f"{ext}_{z}")
            ext_vals["Brida del cilindro"] = st.number_input(f"{ext} - Brida del cilindro (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"{ext}_brida")
            ext_vals["Conector"] = st.number_input(f"{ext} - Conector (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"{ext}_conector")
            extrusoras_datos[ext] = ext_vals

        st.markdown("---")
        st.markdown("🌀 **2. Moldes (1 al 8 - Puro Amperaje)**")
        moldes_datos = {}
        m_cols = st.columns(4)
        for idx, mol in enumerate(moldes_perf):
            with m_cols[idx % 4]:
                moldes_datos[mol] = st.number_input(f"{mol} (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"molde_{mol}")

        st.markdown("---")
        st.markdown("💨 **3. Ventiladores por Extrusora (1 al 4 - Puro Amperaje)**")
        ventiladores_datos = {}
        for ext in ext_perf:
            st.markdown(f"*Ventiladores para {ext}*")
            v_cols = st.columns(4)
            vent_ext = {}
            for i in range(1, 5):
                v_name = f"Ventilador {i}"
                with v_cols[(i - 1) % 4]:
                    vent_ext[v_name] = st.number_input(f"{ext} - {v_name} (Amp)", min_value=0.0, step=0.1, format="%.1f", key=f"vent_{ext}_{i}")
            ventiladores_datos[ext] = vent_ext

        st.markdown("---")
        st.markdown("🌊 **4. Tinas (Bombas de Vacío y Agua)**")
        tinas_datos = {}
        for tina in tinas_perf:
            st.markdown(f"**🔹 Tina: {tina}**")
            tina_subs = {}
            for bomba in ["Bomba de vacío 1", "Bomba de vacío 2", "Bomba de agua 1", "Bomba de agua 2"]:
                st.markdown(f"*{bomba}*")
                bc1, bc2, bc3 = st.columns(3)
                with bc1:
                    bt = st.number_input(f"Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{tina}_{bomba}")
                with bc2:
                    ba = st.number_input(f"Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{tina}_{bomba}")
                with bc3:
                    bv = st.number_input(f"Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{tina}_{bomba}")
                tina_subs[bomba] = {"Temp": bt, "Amp": ba, "Vib": bv}
            tinas_datos[tina] = tina_subs

        st.markdown("---")
        st.markdown("⚙️ **5. Bandas y Cortadoras**")
        generales_datos = {}
        for gen in generales_perf:
            st.markdown(f"**🔹 {gen}**")
            gc1, gc2, gc3 = st.columns(3)
            with gc1:
                gt = st.number_input(f"Temp (°C)", min_value=0.0, step=0.1, format="%.1f", key=f"t_{gen}")
            with gc2:
                ga = st.number_input(f"Amp (A)", min_value=0.0, step=0.1, format="%.1f", key=f"a_{gen}")
            with gc3:
                gv = st.number_input(f"Vib (mm/s)", min_value=0.0, step=0.1, format="%.1f", key=f"v_{gen}")
            generales_datos[gen] = {"Temp": gt, "Amp": ga, "Vib": gv}

        submitted_p = st.form_submit_button("Guardar Registro Completo de Perfilería")
        if submitted_p:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            reg_perf = []
            
            for ext, vals in extrusoras_datos.items():
                for sub_elem, val in vals.items():
                    reg_perf.append({"Fecha": fecha_actual, "Tipo_Sistema": tipo_sistema, "Extrusora/Sección": ext, "Sub_Elemento": sub_elem, "Mes": mes_p, "Métrica": "Valor", "Valor": val})
            
            for mol, val in moldes_datos.items():
                reg_perf.append({"Fecha": fecha_actual, "Tipo_Sistema": tipo_sistema, "Extrusora/Sección": "Moldes", "Sub_Elemento": mol, "Mes": mes_p, "Métrica": "Amp", "Valor": val})

            for ext, vents in ventiladores_datos.items():
                for v_name, val in vents.items():
                    reg_perf.append({"Fecha": fecha_actual, "Tipo_Sistema": tipo_sistema, "Extrusora/Sección": f"Ventiladores {ext}", "Sub_Elemento": v_name, "Mes": mes_p, "Métrica": "Amp", "Valor": val})

            for tina, bs in tinas_datos.items():
                for bomba, metrics in bs.items():
                    for met, val in metrics.items():
                        reg_perf.append({"Fecha": fecha_actual, "Tipo_Sistema": tipo_sistema, "Extrusora/Sección": f"Tina {tina}", "Sub_Elemento": bomba, "Mes": mes_p, "Métrica": met, "Valor": val})

            for gen, metrics in generales_datos.items():
                for met, val in metrics.items():
                    reg_perf.append({"Fecha": fecha_actual, "Tipo_Sistema": tipo_sistema, "Extrusora/Sección": "Equipos Generales", "Sub_Elemento": gen, "Mes": mes_p, "Métrica": met, "Valor": val})

            df_act_p = pd.concat([df_perf, pd.DataFrame(reg_perf)], ignore_index=True)
            guardar_datos(PERF_FILE, df_act_p)
            st.success(f"¡Registro completo guardado para **{tipo_sistema}**!")
            st.rerun()

    st.divider()
    with st.expander("🛠️ Configuración Módulo Perfilería (Protegido con PIN)"):
        pin_p = st.text_input("PIN de seguridad", type="password", max_chars=4, key="pin_p")
        if pin_p == PIN_SEGURIDAD:
            st.success("✅ Acceso autorizado.")
            
            # --- SECCIÓN PARA REEMPLAZAR O FORZAR LA LISTA NUEVA SI PERSISTE EL CACHÉ ---
            if st.button("🔄 Restablecer lista por defecto (PPR, CPVC, PVC, etc.)"):
                guardar_config(LINEAS_PERF_FILE, ["PPR", "CPVC", "PVC", "Tubo hidráulico", "Tubo de estante"], "Linea")
                st.success("¡Lista restablecida con éxito! Recarga la página.")
                st.rerun()

            sys_ed = st.selectbox("Editar Sistema / Línea Perf", lineas_perf, key="syse")
            n_sys = st.text_input("Nuevo nombre de sistema", value=sys_ed, key="nsyse")
            if st.button("💾 Guardar Sistema Perf"):
                lineas_perf[lineas_perf.index(sys_ed)] = n_sys
                guardar_config(LINEAS_PERF_FILE, lineas_perf, "Linea")
                st.rerun()

            nuevo_sys = st.text_input("Agregar nuevo Sistema / Línea", placeholder="Ej. Nuevo material")
            if st.button("➕ Agregar Sistema Perf"):
                if nuevo_sys and nuevo_sys not in lineas_perf:
                    lineas_perf.append(nuevo_sys)
                    guardar_config(LINEAS_PERF_FILE, lineas_perf, "Linea")
                    st.success("¡Sistema añadido!")
                    st.rerun()

            ext_ed = st.selectbox("Editar Extrusora Perfilería", ext_perf, key="exte")
            n_ext = st.text_input("Nuevo nombre extrusora", value=ext_ed, key="nexte")
            if st.button("💾 Guardar Extrusora Perf"):
                ext_perf[ext_perf.index(ext_ed)] = n_ext
                guardar_config(EXT_PERF_FILE, ext_perf, "Extrusora")
                st.rerun()
                
        elif pin_p != "":
            st.error("PIN Incorrecto")

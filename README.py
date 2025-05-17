# BLOQUE DE ENTRADA DE DATOS – APP BLABO (STREAMLIT)

import streamlit as st

def cargar_datos_entrada():
    st.sidebar.header("🔧 Datos Generales del Proceso")
    with st.sidebar.form("form_datos_generales"):
        st.subheader("🛢️ Datos del tanque y lodo")
        V_tanque = st.number_input("Capacidad del tanque [m³]", value=10000)
        H_lodo = st.number_input("Altura de lodo [m]", value=4.0)
        densidad_lodo = st.number_input("Densidad del lodo [kg/m³]", value=950)

        st.subheader("🌡️ Temperaturas del proceso")
        temp_ini = st.number_input("Temperatura inicial [°C]", value=20)
        temp_fin = st.number_input("Temperatura final objetivo [°C]", value=80)

        st.subheader("⚗️ Composición del lodo [%]")
        HC_pct = st.number_input("% Hidrocarburos", value=70)
        agua_pct = st.number_input("% Agua", value=15)
        sol_inorg_pct = st.number_input("% Sólidos inorgánicos", value=10)
        sol_org_pct = st.number_input("% Sólidos orgánicos", value=5)

        st.subheader("🔁 Recirculación")
        Q_recirc = st.number_input("Caudal de recirculación [m³/h]", value=100)

        st.markdown("---")
        st.subheader("⚙️ Parámetros técnicos por módulo")

        Cp_aceite = st.number_input("Módulo 2 - Cp del aceite [kJ/kg·K]", value=2.1)
        eficiencia_corte = st.number_input("Módulo 2 - Eficiencia de corte de ciclones [%]", value=95)

        Cp_lodo = st.number_input("Módulo 3 - Cp del lodo [kJ/kg·K]", value=2.5)
        deltaT_boquillas = st.number_input("Módulo 3 - ΔT impacto térmico [°C]", value=40)

        rpm_tornillo = st.number_input("Módulo 4 - Velocidad diferencial tornillo [rpm]", value=20)
        mu_lodo = st.number_input("Módulo 4 - Viscosidad del lodo [Pa·s]", value=0.1)
        rho_s = st.number_input("Módulo 4 - Densidad sólidos [kg/m³]", value=2650)
        rho_f = st.number_input("Módulo 4 - Densidad fluido [kg/m³]", value=900)

        rpm_centrifuga = st.number_input("Módulo 4B - RPM centrífuga", value=5000)
        radio_centrifuga = st.number_input("Módulo 4B - Radio tambor [m]", value=0.15)

        radio_gota = st.number_input("Módulo 5 - Radio de gota [m]", value=25e-6)
        mu_agua = st.number_input("Módulo 5 - Viscosidad del agua [Pa·s]", value=0.001)
        rho_agua = st.number_input("Módulo 5 - Densidad del agua [kg/m³]", value=1000)
        rho_aceite = st.number_input("Módulo 5 - Densidad del aceite [kg/m³]", value=850)

        volumen_libre = st.number_input("Módulo 6 - Volumen libre tanque [m³]", value=5000)
        C_esp = st.number_input("Módulo 6 - Consumo específico N₂ [kWh/m³]", value=0.2)
        n_renov = st.number_input("Módulo 6 - Número de renovaciones", value=2)

        tiempo_lavado = st.number_input("Módulo 7 - Tiempo de lavado [h]", value=6)
        caudal_agua = st.number_input("Módulo 7 - Caudal de lavado [m³/h]", value=5)
        volumen_ventilado = st.number_input("Módulo 7 - Volumen ventilado [m³/h]", value=100000)

        submit = st.form_submit_button("Calcular sistema completo")

    datos = {
        "V_tanque": V_tanque,
        "H_lodo": H_lodo,
        "densidad_lodo": densidad_lodo,
        "temp_ini": temp_ini,
        "temp_fin": temp_fin,
        "HC_pct": HC_pct,
        "agua_pct": agua_pct,
        "sol_inorg_pct": sol_inorg_pct,
        "sol_org_pct": sol_org_pct,
        "Q_recirc": Q_recirc,
        "Cp_aceite": Cp_aceite,
        "eficiencia_corte": eficiencia_corte,
        "Cp_lodo": Cp_lodo,
        "deltaT_boquillas": deltaT_boquillas,
        "rpm_tornillo": rpm_tornillo,
        "mu_lodo": mu_lodo,
        "rho_s": rho_s,
        "rho_f": rho_f,
        "rpm_centrifuga": rpm_centrifuga,
        "radio_centrifuga": radio_centrifuga,
        "radio_gota": radio_gota,
        "mu_agua": mu_agua,
        "rho_agua": rho_agua,
        "rho_aceite": rho_aceite,
        "volumen_libre": volumen_libre,
        "C_esp": C_esp,
        "n_renov": n_renov,
        "tiempo_lavado": tiempo_lavado,
        "caudal_agua": caudal_agua,
        "volumen_ventilado": volumen_ventilado,
        "submit": submit
    }
    return datos

# SIMULACIÓN COMPLETA DEL SISTEMA BLABO CON TODOS LOS MÓDULOS CONECTADOS

import streamlit as st
from funciones_calculo_blabo import *
from streamlit_entrada_blabo import cargar_datos_entrada

# CARGAR DATOS DE ENTRADA
entrada = cargar_datos_entrada()

if entrada["submit"]:
    st.title("📊 Resultados de Simulación del Sistema BLABO")

    # MÓDULO 1 – SUCCIÓN
    volumen_lodo = entrada["H_lodo"] * entrada["V_tanque"] / entrada["H_lodo"]
    res1 = calcular_modulo_1(volumen_lodo, entrada["densidad_lodo"])
    masa_total = res1["masa_total_lodo"]
    st.subheader("🔹 Módulo 1 – Succión")
    st.latex(r"m_{lodo} = V \cdot \rho")
    st.write(f"Masa total de lodo: {masa_total:,.0f} kg")

    # MÓDULO 2 – RECIRCULACIÓN
    masa_solidos = masa_total * (entrada["sol_inorg_pct"] + entrada["sol_org_pct"]) / 100
    res2 = calcular_modulo_2(
        entrada["Q_recirc"], 900, entrada["Cp_aceite"], entrada["temp_ini"], entrada["temp_fin"],
        masa_solidos, entrada["eficiencia_corte"]
    )
    st.subheader("🔹 Módulo 2 – Recirculación + Hidrociclones")
    st.latex(r"Q = \dot{m} \cdot C_p \cdot \Delta T")
    st.write(f"Energía térmica requerida: {res2['Q_kJ_h']/1000:,.2f} kW")
    st.write(f"Masa al decanter: {res2['m_underflow']:,.0f} kg/h")
    st.write(f"Masa a boquillas: {res2['m_overflow']:,.0f} kg/h")

    # MÓDULO 3 – BOQUILLAS
    res3 = calcular_modulo_3(res2['m_overflow'], entrada['Cp_lodo'], entrada['deltaT_boquillas'])
    st.subheader("🔹 Módulo 3 – Boquillas SNS®")
    st.latex(r"Q = m \cdot C_p \cdot \Delta T")
    st.write(f"Masa disuelta: {res3['m_disl']:,.0f} kg/h")
    st.write(f"Energía requerida: {res3['Q_kJ_h']/1000:,.2f} kW")
    st.write(f"Kerosene requerido: {res3['V_kerosene_L']:,.0f} L/h")

    # MÓDULO 4 – DECANTER
    omega = 2 * 3.1416 * entrada['rpm_tornillo'] / 60
    res4 = calcular_modulo_4(
        entrada['mu_lodo'], entrada['rho_s'], entrada['rho_f'], omega,
        0.25, 0.1, 0.18, res2['m_underflow'], 1.5  # valores típicos Ro, Ri, Rm, volumen decanter
    )
    st.subheader("🔹 Módulo 4 – Decanter")
    st.latex(r"d_{lim} = \sqrt{ \frac{18 \mu \ln(R_o / R_i)}{(\rho_s - \rho_f) \omega^2 R_m^2} }")
    st.write(f"Diámetro límite de separación: {res4['d_lim_m']*1e6:.2f} µm")
    st.write(f"Tiempo de residencia: {res4['t_res_h']:.2f} h")

    # MÓDULO 4B – CENTRÍFUGA
    res4b = calcular_modulo_4b(entrada['radio_centrifuga'], entrada['rpm_centrifuga'])
    st.subheader("🔹 Módulo 4B – Centrífuga Alta Velocidad")
    st.latex(r"a = r \cdot \left( \frac{2\pi n}{60} \right)^2")
    st.write(f"Aceleración centrífuga: {res4b['aceleracion_m_s2']:.0f} m/s²")

    # MÓDULO 5 – DESNATADO
    res5 = calcular_modulo_5(entrada['rho_agua'], entrada['rho_aceite'], 9.81, entrada['radio_gota'], entrada['mu_agua'])
    st.subheader("🔹 Módulo 5 – Desnatado")
    st.latex(r"v = \frac{2}{9} \cdot \frac{(\rho_{agua} - \rho_{aceite}) g r^2}{\mu}")
    st.write(f"Velocidad de ascenso de gota: {res5['vel_ascenso_m_s']*1000:.4f} mm/s")

    # MÓDULO 6 – INERTIZACIÓN
    res6 = calcular_modulo_6(entrada['volumen_libre'], entrada['C_esp'], entrada['n_renov'])
    st.subheader("🔹 Módulo 6 – Inertización con N₂")
    st.latex(r"V_{N2} = 2 \cdot V_{libre}")
    st.write(f"Volumen N₂ requerido: {res6['volumen_N2_m3']:,.0f} m³")
    st.write(f"Potencia estimada: {res6['potencia_kW']:,.1f} kW")

    # MÓDULO 7 – LAVADO + VENTILACIÓN
    m_agua = entrada['tiempo_lavado'] * entrada['caudal_agua'] * 1000  # kg
    res7 = calcular_modulo_7(m_agua, 4.18, entrada['temp_fin'] - entrada['temp_ini'], entrada['volumen_ventilado'], entrada['V_tanque'])
    st.subheader("🔹 Módulo 7 – Lavado y Ventilación")
    st.latex(r"Q = m \cdot C_p \cdot \Delta T")
    st.write(f"Energía de calentamiento agua: {res7['Q_kJ']/1000:,.1f} kW")
    st.write(f"Renovaciones necesarias: {res7['n_renovaciones']:.1f} veces")


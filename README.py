# app_blabo.py

import streamlit as st
from funciones_calculo_blabo import *
from streamlit_entrada_blabo import cargar_datos_entrada

# Configuración de página
st.set_page_config(page_title="Simulador BLABO®", layout="wide")
st.title("🛢️ Simulador de Limpieza de Tanques – Sistema BLABO®")
st.markdown("Este simulador calcula los balances de masa y energía módulo por módulo, según los datos operativos del sistema BLABO®.")

# Cargar datos desde el sidebar
entrada = cargar_datos_entrada()

if entrada["submit"]:
    st.header("📊 Resultados de Simulación del Sistema")

    # MÓDULO 1 – SUCCIÓN
    volumen_lodo = entrada["V_tanque"]
    res1 = calcular_modulo_1(volumen_lodo, entrada["densidad_lodo"])
    masa_total = res1["masa_total_lodo"]
    st.subheader("🔹 Módulo 1 – Succión")
    st.latex(r"m = V \cdot \rho")
    st.write(f"Masa total de lodo: **{masa_total:,.0f} kg**")

    # MÓDULO 2 – RECIRCULACIÓN
    masa_solidos = masa_total * (entrada["sol_inorg_pct"] + entrada["sol_org_pct"]) / 100
    res2 = calcular_modulo_2(
        entrada["Q_recirc"], 900, entrada["Cp_aceite"],
        entrada["temp_ini"], entrada["temp_fin"],
        masa_solidos, entrada["eficiencia_corte"]
    )
    st.subheader("🔹 Módulo 2 – Recirculación + Hidrociclones")
    st.latex(r"Q = \dot{m} \cdot C_p \cdot \Delta T")
    st.write(f"Energía térmica requerida: **{res2['Q_kJ_h'] / 1000:,.2f} kW**")
    st.write(f"Masa al decanter: **{res2['m_underflow']:,.0f} kg/h**")
    st.write(f"Masa a boquillas: **{res2['m_overflow']:,.0f} kg/h**")

    # MÓDULO 3 – BOQUILLAS
    res3 = calcular_modulo_3(res2['m_overflow'], entrada["Cp_lodo"], entrada["deltaT_boquillas"])
    st.subheader("🔹 Módulo 3 – Boquillas SNS®")
    st.latex(r"Q = m \cdot C_p \cdot \Delta T")
    st.write(f"Masa disuelta: **{res3['m_disl']:,.0f} kg/h**")
    st.write(f"Energía requerida: **{res3['Q_kJ_h'] / 1000:,.2f} kW**")
    st.write(f"Kerosene requerido: **{res3['V_kerosene_L']:,.0f} L/h**")

    # MÓDULO 4 – DECANTER
    omega = 2 * 3.1416 * entrada['rpm_tornillo'] / 60
    res4 = calcular_modulo_4(
        entrada['mu_lodo'], entrada['rho_s'], entrada['rho_f'],
        omega, 0.25, 0.1, 0.18, res2['m_underflow'], 1.5
    )
    st.subheader("🔹 Módulo 4 – Decanter")
    st.latex(r"d_{lim} = \sqrt{ \frac{18 \mu \ln(R_o / R_i)}{(\rho_s - \rho_f) \omega^2 R_m^2} }")
    st.write(f"Diámetro límite de separación: **{res4['d_lim_m']*1e6:.2f} µm**")
    st.write(f"Tiempo de residencia: **{res4['t_res_h']:.2f} h**")

    # MÓDULO 4B – CENTRÍFUGA
    res4b = calcular_modulo_4b(entrada["radio_centrifuga"], entrada["rpm_centrifuga"])
    st.subheader("🔹 Módulo 4B – Centrífuga Alta Velocidad")
    st.latex(r"a = r \cdot \left( \frac{2\pi n}{60} \right)^2")
    st.write(f"Aceleración centrífuga: **{res4b['aceleracion_m_s2']:.0f} m/s²**")

    # MÓDULO 5 – DESNATADO
    res5 = calcular_modulo_5(
        entrada["rho_agua"], entrada["rho_aceite"], 9.81,
        entrada["radio_gota"], entrada["mu_agua"]
    )
    st.subheader("🔹 Módulo 5 – Desnatado")
    st.latex(r"v = \frac{2}{9} \cdot \frac{(\rho_{agua} - \rho_{aceite}) g r^2}{\mu}")
    st.write(f"Velocidad de ascenso de gota: **{res5['vel_ascenso_m_s'] * 1000:.4f} mm/s**")

    # MÓDULO 6 – INERTIZACIÓN
    res6 = calcular_modulo_6(entrada["volumen_libre"], entrada["C_esp"], entrada["n_renov"])
    st.subheader("🔹 Módulo 6 – Inertización con N₂")
    st.latex(r"V_{N2} = n \cdot V_{libre}")
    st.write(f"Volumen requerido de N₂: **{res6['volumen_N2_m3']:,.0f} m³**")
    st.write(f"Potencia estimada: **{res6['potencia_kW']:,.1f} kW**")

    # MÓDULO 7 – LAVADO + VENTILACIÓN
    m_agua = entrada["tiempo_lavado"] * entrada["caudal_agua"] * 1000  # kg
    res7 = calcular_modulo_7(
        m_agua, 4.18, entrada["temp_fin"] - entrada["temp_ini"],
        entrada["volumen_ventilado"], entrada["V_tanque"]
    )
    st.subheader("🔹 Módulo 7 – Lavado y Ventilación")
    st.latex(r"Q = m \cdot C_p \cdot \Delta T")
    st.write(f"Energía para calentar agua: **{res7['Q_kJ'] / 1000:,.1f} kW**")
    st.write(f"Renovaciones necesarias: **{res7['n_renovaciones']:.1f} veces**")



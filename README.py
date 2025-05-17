import streamlit as st
import math
from fpdf import FPDF
from io import BytesIO

# -------------------------------
# FUNCIONES DE CÁLCULO
# -------------------------------

def calcular_modulo_1(volumen_lodo_m3, densidad_lodo_kg_m3):
    return {"masa_total_lodo": volumen_lodo_m3 * densidad_lodo_kg_m3}

def calcular_modulo_2(Q_m3h, densidad_fluido_kg_m3, Cp_kJ_kgK, T_ini, T_fin, masa_solidos_kg_h, eficiencia_corte_pct):
    deltaT = T_fin - T_ini
    m_fluido_kg_h = Q_m3h * densidad_fluido_kg_m3
    Q_kJ_h = m_fluido_kg_h * Cp_kJ_kgK * deltaT
    m_underflow = masa_solidos_kg_h * eficiencia_corte_pct / 100
    m_overflow = masa_solidos_kg_h - m_underflow
    return {"Q_kJ_h": Q_kJ_h, "m_underflow": m_underflow, "m_overflow": m_overflow}

def calcular_modulo_3(m_kg_h, Cp_kJ_kgK, deltaT_C):
    Q_kJ_h = m_kg_h * Cp_kJ_kgK * deltaT_C
    V_kerosene_L = m_kg_h * 1.2
    return {"m_disl": m_kg_h, "Q_kJ_h": Q_kJ_h, "V_kerosene_L": V_kerosene_L}

def calcular_modulo_4(mu, rho_s, rho_f, omega, Ro, Ri, Rm, m_kg_h, vol_m3):
    d_lim = math.sqrt((18 * mu * math.log(Ro / Ri)) / ((rho_s - rho_f) * omega**2 * Rm**2))
    t_res = vol_m3 / (m_kg_h / rho_f)
    return {"d_lim_m": d_lim, "t_res_h": t_res}

def calcular_modulo_4b(radio_m, rpm):
    omega = 2 * math.pi * rpm / 60
    return {"aceleracion_m_s2": radio_m * omega**2}

def calcular_modulo_5(rho_agua, rho_aceite, g, r, mu):
    v = (2 / 9) * ((rho_agua - rho_aceite) * g * r**2) / mu
    return {"vel_ascenso_m_s": v}

def calcular_modulo_6(V_libre, C_esp, n_renov):
    V = V_libre * n_renov
    P = V * C_esp
    return {"volumen_N2_m3": V, "potencia_kW": P}

def calcular_modulo_7(m_agua, Cp, deltaT, V_ventilado, V_tanque):
    Q = m_agua * Cp * deltaT
    renov = V_ventilado / V_tanque
    return {"Q_kJ": Q, "n_renovaciones": renov}

# -------------------------------
# PDF GENERATOR
# -------------------------------

def generar_pdf(resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Informe de Simulación – Sistema BLABO®", ln=True, align="C")
    pdf.ln(10)

    for modulo, datos in resultados.items():
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, modulo, ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        for key, val in datos.items():
            pdf.cell(0, 8, f"• {key}: {val}", ln=True)
        pdf.ln(4)

    buffer = BytesIO()
    pdf.output(buffer, 'S').encode('latin1')
    buffer.seek(0)
    return buffer

# -------------------------------
# INTERFAZ STREAMLIT
# -------------------------------

st.set_page_config(page_title="Simulador BLABO®", layout="wide")
st.markdown("<h1 style='text-align: center;'>🛢️ Simulador de Limpieza de Tanques – Sistema BLABO®</h1>", unsafe_allow_html=True)

with st.form("formulario"):
    st.sidebar.header("🔧 Parámetros de Entrada")
    V_tanque = st.sidebar.number_input("Capacidad del tanque [m³]", value=10000.0)
    H_lodo = st.sidebar.number_input("Altura de lodo [m]", value=4.0)
    densidad_lodo = st.sidebar.number_input("Densidad del lodo [kg/m³]", value=950.0)
    temp_ini = st.sidebar.number_input("Temperatura inicial [°C]", value=20.0)
    temp_fin = st.sidebar.number_input("Temperatura final [°C]", value=80.0)
    sol_inorg_pct = st.sidebar.number_input("Sólidos inorgánicos [%]", value=10.0)
    sol_org_pct = st.sidebar.number_input("Sólidos orgánicos [%]", value=5.0)
    Q_recirc = st.sidebar.number_input("Caudal recirculación [m³/h]", value=100.0)
    Cp_aceite = st.sidebar.number_input("Cp aceite [kJ/kg·K]", value=2.1)
    eficiencia_corte = st.sidebar.number_input("Eficiencia ciclones [%]", value=95.0)
    Cp_lodo = st.sidebar.number_input("Cp lodo [kJ/kg·K]", value=2.5)
    deltaT_boquillas = st.sidebar.number_input("ΔT boquillas [°C]", value=40.0)
    rpm_tornillo = st.sidebar.number_input("RPM tornillo", value=20)
    mu_lodo = st.sidebar.number_input("Viscosidad del lodo [Pa·s]", value=0.1)
    rho_s = st.sidebar.number_input("Densidad sólidos [kg/m³]", value=2650)
    rho_f = st.sidebar.number_input("Densidad fluido [kg/m³]", value=900)
    rpm_centrifuga = st.sidebar.number_input("RPM centrífuga", value=5000)
    radio_centrifuga = st.sidebar.number_input("Radio centrífuga [m]", value=0.15)
    radio_gota = st.sidebar.number_input("Radio de gota [m]", value=25e-6)
    mu_agua = st.sidebar.number_input("Viscosidad agua [Pa·s]", value=0.001)
    rho_agua = st.sidebar.number_input("Densidad agua [kg/m³]", value=1000)
    rho_aceite = st.sidebar.number_input("Densidad aceite [kg/m³]", value=850)
    volumen_libre = st.sidebar.number_input("Volumen libre [m³]", value=5000.0)
    C_esp = st.sidebar.number_input("Consumo específico N₂ [kWh/m³]", value=0.2)
    n_renov = st.sidebar.number_input("N° de renovaciones", value=2)
    tiempo_lavado = st.sidebar.number_input("Tiempo de lavado [h]", value=6.0)
    caudal_agua = st.sidebar.number_input("Caudal de agua [m³/h]", value=5.0)
    volumen_ventilado = st.sidebar.number_input("Volumen ventilado [m³/h]", value=100000.0)
    calcular = st.form_submit_button("🧮 Calcular y generar PDF")

if calcular:
    resultados = {}
    res1 = calcular_modulo_1(V_tanque, densidad_lodo)
    masa_total = res1["masa_total_lodo"]
    resultados["🔹 Módulo 1 – Succión"] = {"Masa total de lodo [kg]": f"{masa_total:,.0f}"}

    masa_solidos = masa_total * (sol_inorg_pct + sol_org_pct) / 100
    res2 = calcular_modulo_2(Q_recirc, 900, Cp_aceite, temp_ini, temp_fin, masa_solidos, eficiencia_corte)
    resultados["🔹 Módulo 2 – Recirculación"] = {
        "Energía requerida [kW]": f"{res2['Q_kJ_h']/1000:.2f}",
        "Underflow al decanter [kg/h]": f"{res2['m_underflow']:,.0f}",
        "Overflow a boquillas [kg/h]": f"{res2['m_overflow']:,.0f}"
    }

    res3 = calcular_modulo_3(res2["m_overflow"], Cp_lodo, deltaT_boquillas)
    resultados["🔹 Módulo 3 – Boquillas"] = {
        "Energía térmica [kW]": f"{res3['Q_kJ_h']/1000:.2f}",
        "Kerosene requerido [L/h]": f"{res3['V_kerosene_L']:,.0f}"
    }

    omega = 2 * math.pi * rpm_tornillo / 60
    res4 = calcular_modulo_4(mu_lodo, rho_s, rho_f, omega, 0.25, 0.1, 0.18, res2["m_underflow"], 1.5)
    resultados["🔹 Módulo 4 – Decanter"] = {
        "Diámetro límite [µm]": f"{res4['d_lim_m']*1e6:.2f}",
        "Tiempo de residencia [h]": f"{res4['t_res_h']:.2f}"
    }

    res4b = calcular_modulo_4b(radio_centrifuga, rpm_centrifuga)
    resultados["🔹 Módulo 4B – Centrífuga"] = {
        "Aceleración [m/s²]": f"{res4b['aceleracion_m_s2']:.0f}"
    }

    res5 = calcular_modulo_5(rho_agua, rho_aceite, 9.81, radio_gota, mu_agua)
    resultados["🔹 Módulo 5 – Desnatado"] = {
        "Velocidad de ascenso [mm/s]": f"{res5['vel_ascenso_m_s']*1000:.4f}"
    }

    res6 = calcular_modulo_6(volumen_libre, C_esp, n_renov)
    resultados["🔹 Módulo 6 – Inertización"] = {
        "Volumen N₂ [m³]": f"{res6['volumen_N2_m3']:,.0f}",
        "Potencia estimada [kW]": f"{res6['potencia_kW']:.2f}"
    }

    m_agua = tiempo_lavado * caudal_agua * 1000
    deltaT = temp_fin - temp_ini
    res7 = calcular_modulo_7(m_agua, 4.18, deltaT, volumen_ventilado, V_tanque)
    resultados["🔹 Módulo 7 – Lavado y Ventilación"] = {
        "Energía para calentar agua [kW]": f"{res7['Q_kJ']/1000:.1f}",
        "Renovaciones necesarias": f"{res7['n_renovaciones']:.1f}"
    }

    # Mostrar resultados en pantalla
    for mod, datos in resultados.items():
        st.subheader(mod)
        for k, v in datos.items():
            st.write(f"• {k}: **{v}**")

    # Generar y descargar PDF
    pdf = generar_pdf(resultados)
    st.download_button("📥 Descargar informe PDF", data=pdf, file_name="informe_blabo.pdf", mime="application/pdf")






# Simulador Profesional de Limpieza de Tanques - Sistema BLABO®
# Autor: Federico Catereniuc | UTN-FRN
# Desarrollado para tesis de Ingeniería Química

import streamlit as st
import math
from io import BytesIO
from fpdf import FPDF

# -------------------------------
# CONFIGURACIÓN VISUAL Y ESTILO
# -------------------------------
st.set_page_config(page_title="Simulador Profesional BLABO", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #1e1e1e; color: white; font-family: 'Arial'; }
.stSidebar .sidebar-content { background-color: #111827; }
h1, h2, h3, .stMarkdown, .stCaption { color: #ffffff; }
.stButton > button {
    background-color: #4f46e5;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}
hr {
    margin-top: 1em;
    margin-bottom: 1em;
    border-color: #4f46e5;
}
</style>
""", unsafe_allow_html=True)

st.image("diagramadeflujo.png", caption="Diagrama del sistema de limpieza automatizada BLABO®", use_column_width=True)

st.markdown("""
<h1 style='text-align: center;'>🚓 Simulador Profesional de Limpieza de Tanques - Sistema BLABO®</h1>
<p style='text-align: center;'>Aplicación interactiva para balance de masa y energía con fines pedagógicos</p>
<p style='text-align: justify;'>Este simulador fue desarrollado como herramienta académica para comprender el funcionamiento físico y térmico del sistema BLABO®, empleado en la limpieza automatizada de tanques de crudo. Cada módulo representa una etapa del proceso industrial, con parámetros configurables, fórmulas reales y resultados explicados en términos técnicos. El objetivo es que tanto estudiantes como profesionales puedan interpretar la operación y balance de cada equipo involucrado.</p>
<hr>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCIONES DE CÁLCULO
# -------------------------------
def calcular_masa_total_lodo(V_tanque, H_lodo, densidad):
    return V_tanque * (H_lodo / 20), V_tanque * (H_lodo / 20) * densidad

def calcular_energia_calentamiento(m, Cp, Ti, Tf):
    return m * Cp * (Tf - Ti)

def calcular_separacion(m_solidos, eficiencia):
    under = m_solidos * eficiencia / 100
    return under, m_solidos - under

def calcular_diametro_corte_hidrociclon(mu, rhop, rhof, deltaP, d):
    K = 18 * mu / ((rhop - rhof) * deltaP)
    return math.sqrt(K) * d

def calcular_flujo_vapor(Q_kJ, lambda_v):
    return Q_kJ / lambda_v

def calcular_residencia_decanter(V, Q):
    return V / Q if Q else float('inf')

def calcular_RCF(r, rpm):
    omega = 2 * math.pi * rpm / 60
    a = r * omega**2
    return a / 9.81, a

def calcular_stokes(rho_f, rho_p, g, r, mu):
    return (2 / 9) * ((rho_p - rho_f) * g * r**2) / mu

# -------------------------------
# PARÁMETROS DE ENTRADA
# -------------------------------
st.sidebar.header("🔧 Parámetros de Entrada")

V_tanque = st.sidebar.number_input("Volumen del tanque [m³]", value=10000.0)
H_lodo = st.sidebar.slider("Altura de lodo [m]", 0.0, 20.0, 4.0)
densidad_lodo = st.sidebar.number_input("Densidad del lodo [kg/m³]", value=950.0)

Ti = st.sidebar.number_input("Temperatura inicial [°C]", value=20.0)
Tf = st.sidebar.number_input("Temperatura final [°C]", value=80.0)
Cp_lodo = st.sidebar.number_input("Cp del lodo [kJ/kg·K]", value=2.1)

sol_inorg = st.sidebar.number_input("Sólidos inorgánicos [%]", value=10.0)
sol_org = st.sidebar.number_input("Sólidos orgánicos [%]", value=5.0)
eficiencia_corte = st.sidebar.number_input("Eficiencia ciclones [%]", value=95.0)

mu = st.sidebar.number_input("Viscosidad lodo [Pa·s]", value=0.1)
rhop = st.sidebar.number_input("Densidad partículas [kg/m³]", value=2650.0)
rhof = st.sidebar.number_input("Densidad fluido [kg/m³]", value=900.0)
deltaP = st.sidebar.number_input("ΔP ciclón [Pa]", value=150000.0)
D_ciclon = st.sidebar.number_input("Diámetro ciclón [m]", value=0.1)

lambda_v = st.sidebar.number_input("Calor latente vapor [kJ/kg]", value=2257.0)
Q_decanter = st.sidebar.number_input("Caudal al decanter [m³/h]", value=15.0)
V_decanter = st.sidebar.number_input("Volumen útil decanter [m³]", value=8.0)

rpm = st.sidebar.number_input("RPM centrífuga", value=5000)
r = st.sidebar.number_input("Radio centrífuga [m]", value=0.15)

r_gota = st.sidebar.number_input("Radio gota aceite [m]", value=30e-6)
rho_agua = st.sidebar.number_input("Densidad agua [kg/m³]", value=1000.0)
rho_aceite = st.sidebar.number_input("Densidad aceite [kg/m³]", value=850.0)
mu_agua = st.sidebar.number_input("Viscosidad agua [Pa·s]", value=0.001)

# -------------------------------
# CÁLCULOS
# -------------------------------
if st.sidebar.button("📊 Ejecutar simulación"):
    resultados = {}
    explicaciones = {}

    V_lodo, m_lodo = calcular_masa_total_lodo(V_tanque, H_lodo, densidad_lodo)
    resultados["Masa total de lodo"] = f"{m_lodo:,.0f} kg"
    explicaciones["Masa total de lodo"] = "Cálculo por volumen y densidad."

    Q = calcular_energia_calentamiento(m_lodo, Cp_lodo, Ti, Tf)
    resultados["Energía de calentamiento"] = f"{Q / 1000:.2f} kW"
    explicaciones["Energía de calentamiento"] = "Energía para calentar el lodo (Q = m·Cp·ΔT)."

    Fv = calcular_flujo_vapor(Q, lambda_v)
    resultados["Flujo de vapor"] = f"{Fv:,.1f} kg/h"
    explicaciones["Flujo de vapor"] = "Vapor necesario en H-01 / H-02 para calefacción."

    m_solidos = m_lodo * (sol_inorg + sol_org) / 100
    under, over = calcular_separacion(m_solidos, eficiencia_corte)
    resultados["Underflow (decanter)"] = f"{under:,.0f} kg"
    resultados["Overflow (boquillas)"] = f"{over:,.0f} kg"
    explicaciones["Separación por ciclones"] = "Corte de sólidos entre under y overflow."

    d50 = calcular_diametro_corte_hidrociclon(mu, rhop, rhof, deltaP, D_ciclon)
    resultados["d₅₀ ciclón"] = f"{d50 * 1e6:.2f} µm"
    explicaciones["d₅₀ ciclón"] = "Diámetro de partícula separable (hidrociclón)."

    t_res = calcular_residencia_decanter(V_decanter, Q_decanter)
    resultados["Residencia decanter"] = f"{t_res:.2f} h"
    explicaciones["Residencia decanter"] = "Tiempo necesario para sedimentación efectiva."

    rcf, a = calcular_RCF(r, rpm)
    resultados["RCF centrífuga"] = f"{rcf:.1f} g"
    resultados["Aceleración centrífuga"] = f"{a:.0f} m/s²"
    explicaciones["Centrífuga"] = "Separación por fuerza centrífuga."

    v_stokes = calcular_stokes(rho_agua, rho_aceite, 9.81, r_gota, mu_agua)
    resultados["Velocidad de ascenso aceite"] = f"{v_stokes*1000:.4f} mm/s"
    explicaciones["Skimming"] = "Velocidad de separación por flotación (ley de Stokes)."

    st.subheader("📈 Resultados de simulación")
    for k, v in resultados.items():
        st.write(f"**{k}:** {v}")

    with st.expander("📘 Explicaciones por módulo"):
        for k, v in explicaciones.items():
            st.markdown(f"**{k}:** {v}")

    # -------------------------------
    # EXPORTACIÓN A PDF
    # -------------------------------
    def generar_pdf(resultados, explicaciones):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Informe de Simulación - Sistema BLABO®", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, "Este informe presenta los resultados obtenidos de la simulación del sistema BLABO®, incluyendo análisis energéticos, mecánicos y separativos para cada módulo del proceso.")

        for k, v in resultados.items():
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, k, ln=True)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Resultado: {v}", ln=True)
            if k in explicaciones:
                pdf.multi_cell(0, 8, f"Explicación: {explicaciones[k]}")
            pdf.ln(2)

        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Simulador BLABO - UTN-FRN", 0, 0, "C")

        return BytesIO(pdf.output(dest="S").encode("latin1", "ignore"))

    st.download_button(
        label="📥 Descargar informe PDF",
        data=generar_pdf(resultados, explicaciones),
        file_name="informe_blabo.pdf",
        mime="application/pdf"
    )




       

            




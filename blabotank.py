# Simulador Profesional de Limpieza de Tanques - Sistema BLABO®
# Autor: Federico Catereniuc | UTN-FRN

import streamlit as st
import math
from PIL import Image

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

# -------------------------------
# CABECERA CON LOGO Y TÍTULO
# -------------------------------
col1, col2 = st.columns([1, 6])
with col1:
    try:
        st.image(Image.open("logoutn.png"), width=100)
    except:
        st.warning("⚠️ Logo 'logoutn.png' no encontrado.")
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Simulador Profesional de Limpieza de Tanques - BLABO®</h1>", unsafe_allow_html=True)
    st.markdown("<p>Aplicación interactiva para balance de masa y energía con fines pedagógicos.</p>", unsafe_allow_html=True)

try:
    st.image(Image.open("diagrama de flujo.png"), caption="Diagrama del sistema de limpieza automatizada BLABO®", use_column_width=True)
except:
    st.warning("⚠️ Imagen 'diagrama de flujo.png' no encontrada.")

st.markdown("""<hr>
<p style='text-align: justify;'>Este simulador fue desarrollado como herramienta académica para comprender el funcionamiento físico y térmico del sistema BLABO®, empleado en la limpieza automatizada de tanques de crudo. Cada módulo representa una etapa del proceso industrial, con parámetros configurables, fórmulas reales y resultados explicados en términos técnicos.</p>
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
# INTERFAZ - PARÁMETROS DE ENTRADA
# -------------------------------
st.sidebar.header("🔧 Parámetros de Entrada")

with st.sidebar.expander("🛢️ Tanque y características del lodo"):
    V_tanque = st.number_input("Volumen del tanque [m³]", value=10000.0, help="Volumen total del tanque de crudo")
    H_lodo = st.slider("Altura de lodo [m]", 0.0, 20.0, 4.0, help="Altura que ocupa el lodo dentro del tanque")
    densidad_lodo = st.number_input("Densidad del lodo [kg/m³]", value=950.0)
    Cp_lodo = st.number_input("Cp del lodo [kJ/kg·K]", value=2.1, help="Calor específico promedio del lodo")

with st.sidebar.expander("🌡️ Condiciones térmicas"):
    Ti = st.number_input("Temperatura inicial [°C]", value=20.0)
    Tf = st.number_input("Temperatura final [°C]", value=80.0)
    lambda_v = st.number_input("Calor latente del vapor [kJ/kg]", value=2257.0)

with st.sidebar.expander("🧪 Composición del lodo"):
    sol_inorg = st.number_input("Sólidos inorgánicos [%]", value=10.0)
    sol_org = st.number_input("Sólidos orgánicos [%]", value=5.0)

with st.sidebar.expander("🌀 Ciclones / Hidrociclón"):
    eficiencia_corte = st.number_input("Eficiencia de corte [%]", value=95.0)
    mu = st.number_input("Viscosidad del lodo [Pa·s]", value=0.1)
    rhof = st.number_input("Densidad del fluido [kg/m³]", value=900.0)
    rhop = st.number_input("Densidad de partículas [kg/m³]", value=2650.0)
    deltaP = st.number_input("ΔP ciclón [Pa]", value=150000.0)
    D_ciclon = st.number_input("Diámetro del ciclón [m]", value=0.1)

with st.sidebar.expander("🧭 Decanter"):
    Q_decanter = st.number_input("Caudal al decanter [m³/h]", value=15.0)
    V_decanter = st.number_input("Volumen útil del decanter [m³]", value=8.0)

with st.sidebar.expander("🧲 Centrífuga"):
    rpm = st.number_input("RPM centrífuga", value=5000)
    r = st.number_input("Radio centrífuga [m]", value=0.15)

with st.sidebar.expander("🌊 Skimming"):
    rho_agua = st.number_input("Densidad del agua [kg/m³]", value=1000.0)
    rho_aceite = st.number_input("Densidad del aceite [kg/m³]", value=850.0)
    mu_agua = st.number_input("Viscosidad del agua [Pa·s]", value=0.001)
    r_gota = st.number_input("Radio de gota de aceite [m]", value=30e-6)

# -------------------------------
# SIMULACIÓN Y RESULTADOS
# -------------------------------
if V_tanque <= 0 or H_lodo <= 0 or densidad_lodo <= 0:
    st.error("⚠️ El volumen del tanque, la altura del lodo y la densidad deben ser mayores a cero para ejecutar la simulación.")
else:
    if st.button("📊 Ejecutar simulación"):
        st.subheader("📈 Resultados de la Simulación")
        with st.spinner("Calculando resultados..."):

            resultados = {}
            observaciones = []

            V_lodo, m_lodo = calcular_masa_total_lodo(V_tanque, H_lodo, densidad_lodo)
            Q = calcular_energia_calentamiento(m_lodo, Cp_lodo, Ti, Tf)
            Fv = calcular_flujo_vapor(Q, lambda_v)
            m_solidos = m_lodo * (sol_inorg + sol_org) / 100
            under, over = calcular_separacion(m_solidos, eficiencia_corte)
            d50 = calcular_diametro_corte_hidrociclon(mu, rhop, rhof, deltaP, D_ciclon)
            t_res = calcular_residencia_decanter(V_decanter, Q_decanter)
            rcf, a = calcular_RCF(r, rpm)
            v_stokes = calcular_stokes(rho_agua, rho_aceite, 9.81, r_gota, mu_agua)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Masa total de lodo", f"{m_lodo:,.0f} kg")
                st.metric("Energía de calentamiento", f"{Q/3600:.2f} kW·h")
                st.metric("Flujo de vapor requerido", f"{Fv:,.1f} kg/h")
                st.metric("Underflow (decanter)", f"{under:,.0f} kg")
            with col2:
                st.metric("Overflow (boquillas)", f"{over:,.0f} kg")
                st.metric("d₅₀ ciclón", f"{d50*1e6:.2f} µm")
                st.metric("Tiempo de residencia decanter", f"{t_res:.2f} h")
                st.metric("Velocidad de ascenso (Stokes)", f"{v_stokes*1000:.4f} mm/s")

            if t_res > 2:
                observaciones.append("🔍 Tiempo de residencia elevado en el decanter: revisar eficiencia de sedimentación.")
            if v_stokes < 0.5e-3:
                observaciones.append("🔍 Baja velocidad de ascenso: posible emulsión o gotas muy pequeñas.")

            if observaciones:
                st.warning("\n".join(observaciones))

            st.markdown("---")
            st.markdown("### 📘 Explicaciones técnicas")
            st.latex(r"Q = m \cdot C_p \cdot \Delta T")
            st.markdown("Energía térmica necesaria para calentar el lodo.")
            st.latex(r"d_{50} = \sqrt{\frac{18 \mu}{(\rho_p - \rho_f) \Delta P}} \cdot D")
            st.markdown("Tamaño de corte de partícula en ciclón.")
            st.latex(r"v = \frac{2}{9} \cdot \frac{(\rho_p - \rho_f) g r^2}{\mu}")
            st.markdown("Velocidad de ascenso de gotas de aceite (ley de Stokes).")

st.markdown("<hr><p style='text-align: center;'>Simulador desarrollado por <b>Federico Catereniuc</b> | UTN-FRN | Proyecto Final de Ingeniería Química</p>", unsafe_allow_html=True)




       

            




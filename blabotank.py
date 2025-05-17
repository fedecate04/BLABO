import streamlit as st
import math
from fpdf import FPDF
from io import BytesIO
import unicodedata  


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
# LIMPIEZA DE TEXTO
# -------------------------------

def limpiar_texto(texto):
    if isinstance(texto, str):
        texto = texto.replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"')
        texto = texto.replace("•", "-").replace("🔹", "-").replace("🧮", "").replace("°", " grados")
        return unicodedata.normalize("NFKD", texto).encode("latin-1", "ignore").decode("latin-1")
    return texto

# -------------------------------
# GENERADOR DE PDF PEDAGÓGICO
# -------------------------------

def generar_pdf_pedagogico(resultados, ecuaciones, explicaciones):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Informe de Simulación – Sistema BLABO®", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, limpiar_texto("Este informe presenta los resultados obtenidos de la simulación del sistema de limpieza de tanques BLABO®, incluyendo las ecuaciones utilizadas y una explicación pedagógica para cada módulo del proceso."))
    pdf.ln(5)

    for modulo, datos in resultados.items():
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, limpiar_texto(modulo), ln=True, fill=True)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 8, limpiar_texto(explicaciones.get(modulo, "Sin explicación disponible.")))
        pdf.ln(1)
        pdf.set_font("Arial", "", 11)
        for eq in ecuaciones.get(modulo, []):
            pdf.multi_cell(0, 8, limpiar_texto(eq))
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        for key, val in datos.items():
            pdf.cell(0, 8, limpiar_texto(f"- {key}: {val}"), ln=True)
        pdf.ln(3)

    pdf_bytes = pdf.output(dest="S").encode("latin1", "ignore")
    return pdf_bytes

# -------------------------------
# EXPLICACIONES PEDAGÓGICAS POR MÓDULO
# -------------------------------

explicaciones = {
    "🔹 Módulo 1 – Succión": (
        "Se calcula la masa total de lodo que hay en el tanque, multiplicando el volumen ocupado por el lodo por su densidad. "
        "Este valor representa la cantidad total de residuos a tratar en el proceso."
    ),
    "🔹 Módulo 2 – Recirculación": (
        "Se realiza un balance energético para calentar el fluido de recirculación. Además, se calcula el reparto de sólidos "
        "entre el flujo underflow (hacia decanter) y el overflow (hacia boquillas), en función de la eficiencia de corte del sistema."
    ),
    "🔹 Módulo 3 – Boquillas": (
        "Se estima la energía requerida para calentar el lodo a través de boquillas. También se calcula el volumen de kerosene necesario "
        "para la disolución de hidrocarburos pesados en función de la masa de lodo procesada."
    ),
    "🔹 Módulo 4 – Decanter": (
        "Se determina el diámetro mínimo de partículas que pueden ser separadas por el decanter utilizando una fórmula basada en la "
        "sedimentación centrífuga. También se calcula el tiempo de residencia necesario para una separación efectiva."
    ),
    "🔹 Módulo 4B – Centrífuga": (
        "Se calcula la aceleración centrífuga generada en la centrífuga, valor fundamental para evaluar la eficiencia de separación."
    ),
    "🔹 Módulo 5 – Desnatado": (
        "Se estima la velocidad de ascenso de gotas de aceite en agua utilizando la ley de Stokes, lo cual permite evaluar la eficiencia "
        "del módulo de separación por gravedad (skimming)."
    ),
    "🔹 Módulo 6 – Inertización": (
        "Se calcula el volumen total de nitrógeno requerido para inertizar el tanque en función del volumen libre y la cantidad de renovaciones deseadas. "
        "También se estima la potencia requerida para dicha operación."
    ),
    "🔹 Módulo 7 – Lavado y Ventilación": (
        "Se realiza un balance energético para calentar el agua de lavado desde la temperatura inicial hasta la final. Además, se calcula "
        "el número de renovaciones necesarias para ventilar completamente el volumen del tanque."
    )
}

# -------------------------------
# ECUACIONES UTILIZADAS POR MÓDULO
# -------------------------------

ecuaciones = {
    "🔹 Módulo 1 – Succión": [
        r"M_{lodo} = V_{lodo} \times \rho_{lodo}"
    ],
    "🔹 Módulo 2 – Recirculación": [
        r"Q = \dot{m}_{fluido} \cdot C_p \cdot \Delta T",
        r"\dot{m}_{fluido} = Q_{recirc} \cdot \rho_{fluido}",
        r"\dot{m}_{underflow} = \dot{m}_{s\u00f3lidos} \cdot \frac{\eta}{100}",
        r"\dot{m}_{overflow} = \dot{m}_{s\u00f3lidos} - \dot{m}_{underflow}"
    ],
    "🔹 Módulo 3 – Boquillas": [
        r"Q = \dot{m}_{lodo} \cdot C_p \cdot \Delta T",
        r"V_{kerosene} = \dot{m}_{lodo} \cdot \alpha",
        r"(donde\ \alpha = 1.2\ L/kg)"
    ],
    "🔹 Módulo 4 – Decanter": [
        r"d_{lim} = \sqrt{ \frac{18 \mu \ln(R_o / R_i)}{(\rho_s - \rho_f) \cdot \omega^2 \cdot R_m^2} }",
        r"t_{res} = \frac{V}{\dot{m} / \rho_f}"
    ],
    "🔹 Módulo 4B – Centrífuga": [
        r"\omega = \frac{2\pi \cdot RPM}{60}",
        r"a = R \cdot \omega^2"
    ],
    "🔹 Módulo 5 – Desnatado": [
        r"v = \frac{2}{9} \cdot \frac{(\rho_{agua} - \rho_{aceite}) \cdot g \cdot r^2}{\mu}"
    ],
    "🔹 Módulo 6 – Inertización": [
        r"V_{total} = V_{libre} \cdot n_{renovaciones}",
        r"P = V_{total} \cdot C_{esp}"
    ],
    "🔹 Módulo 7 – Lavado y Ventilación": [
        r"Q = m_{agua} \cdot C_p \cdot \Delta T",
        r"n_{renovaciones} = \frac{V_{ventilado}}{V_{tanque}}"
    ]
}


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

            for mod, datos in resultados.items():
        st.subheader(mod)
        with st.expander("📘 Explicación y fórmulas"):
            st.markdown(explicaciones.get(mod, "Sin explicación disponible."))
            for formula in ecuaciones.get(mod, []):
                st.latex(formula)
        for k, v in datos.items():
            st.write(f"• {k}: **{v}**")

    pdf_bytes = BytesIO()
    pdf_bytes.write(generar_pdf_pedagogico(resultados, ecuaciones, explicaciones))
    pdf_bytes.seek(0)
            




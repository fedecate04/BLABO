# FUNCIONES DE CÁLCULO POR MÓDULO – SISTEMA BLABO

import numpy as np

# ----------------------
# MÓDULO 1 – SUCCIÓN
# ----------------------
def calcular_modulo_1(volumen_lodo_m3, densidad_lodo):
    masa_total = volumen_lodo_m3 * densidad_lodo
    return {"masa_total_lodo": masa_total}

# ----------------------
# MÓDULO 2 – RECIRCULACIÓN
# ----------------------
def calcular_modulo_2(caudal_m3h, densidad_fluido, cp, temp_ini, temp_fin, masa_solidos, eficiencia_corte):
    m_dot = caudal_m3h * densidad_fluido  # kg/h
    Q = m_dot * cp * (temp_fin - temp_ini)
    m_s_gruesos = masa_solidos * eficiencia_corte / 100
    m_to_boquillas = m_dot - m_s_gruesos
    return {
        "m_dot": m_dot,
        "Q_kJ_h": Q,
        "m_underflow": m_s_gruesos,
        "m_overflow": m_to_boquillas
    }

# ----------------------
# MÓDULO 3 – BOQUILLAS
# ----------------------
def calcular_modulo_3(m_lodo_disl, cp_lodo, delta_T):
    Q = m_lodo_disl * cp_lodo * delta_T
    V_kerosene_L = m_lodo_disl  # 1 L/kg
    return {
        "Q_kJ_h": Q,
        "m_disl": m_lodo_disl,
        "V_kerosene_L": V_kerosene_L
    }

# ----------------------
# MÓDULO 4 – DECANTER
# ----------------------
def calcular_modulo_4(mu, rho_s, rho_f, omega, Ro, Ri, Rm, Q_in, V_decanter):
    ln_term = np.log(Ro / Ri)
    numerator = 18 * mu * ln_term
    denominator = (rho_s - rho_f) * (omega**2) * Rm**2
    d_lim = np.sqrt(numerator / denominator)
    tiempo_residencia = V_decanter / Q_in  # h
    return {
        "d_lim_m": d_lim,
        "t_res_h": tiempo_residencia
    }

# ----------------------
# MÓDULO 4B – CENTRÍFUGA
# ----------------------
def calcular_modulo_4b(r, rpm):
    omega = 2 * np.pi * rpm / 60
    a = r * omega**2
    return {"aceleracion_m_s2": a}

# ----------------------
# MÓDULO 5 – DESNATADO
# ----------------------
def calcular_modulo_5(rho_agua, rho_aceite, g, r, mu):
    v = (2/9) * ((rho_agua - rho_aceite) * g * r**2) / mu
    return {"vel_ascenso_m_s": v}

# ----------------------
# MÓDULO 6 – INERTIZACIÓN
# ----------------------
def calcular_modulo_6(volumen_libre, C_esp, n_renov):
    V_N2 = 2 * volumen_libre
    P = volumen_libre * C_esp * n_renov
    return {"volumen_N2_m3": V_N2, "potencia_kW": P}

# ----------------------
# MÓDULO 7 – LAVADO Y VENTILACIÓN
# ----------------------
def calcular_modulo_7(m_agua, cp_agua, delta_T, Q_vent, V_tanque):
    Q = m_agua * cp_agua * delta_T
    N = Q_vent / V_tanque
    return {"Q_kJ": Q, "n_renovaciones": N}

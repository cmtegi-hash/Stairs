import streamlit as st

# Configuración iPhone - Interfaz Profesional y Visible
st.set_page_config(page_title="Stair Master Pro", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .resumen-box {
        background-color: #1e1e1e; 
        color: #28a745; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #28a745;
        text-align: center;
        margin-bottom: 20px;
    }
    .total-label { font-size: 14px; color: #ffffff; opacity: 0.8; }
    .total-value { font-size: 22px; font-weight: bold; display: block; }
    
    .stButton > button { width: 100%; height: 3.8em; font-weight: bold; border-radius: 12px; }
    .btn-save > button { background-color: #28a745 !important; color: white !important; }
    .btn-finish > button { background-color: #dc3545 !important; color: white !important; }
    .btn-edit > button { background-color: #ffc107 !important; color: black !important; height: 2.5em !important; }
    .btn-del > button { background-color: #ff4b4b !important; color: white !important; height: 2.5em !important; }
    
    .copy-area { 
        background-color: #f0f0f0; padding: 15px; border: 1px dashed #999; 
        font-family: monospace; white-space: pre-wrap; color: #000; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA ---
if "all_data" not in st.session_state: st.session_state.all_data = []
if "limit_f" not in st.session_state: st.session_state.limit_f = 4
if "current_f" not in st.session_state: st.session_state.current_f = None
if "st_id" not in st.session_state: st.session_state.st_id = "Escalera A"
if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
if "dir" not in st.session_state: st.session_state.dir = "UP"
if "tab_select" not in st.session_state: st.session_state.tab_select = 0

# --- CÁLCULOS ACUMULATIVOS ---
total_pasos = sum(x['steps'] for x in st.session_state.all_data)
total_landings = sum(x['area'] for x in st.session_state.all_data)

# --- CABECERA DE TOTALES ---
st.markdown(f"""
    <div class="resumen-box">
        <span class="total-label">ACUMULADO TOTAL</span>
        <span class="total-value">📐 {total_landings:.2f} sf</span>
        <span class="total-value">🪜 {total_pasos} steps</span>
    </div>
    """, unsafe_allow_html=True)

# Manejo de pestañas manual para poder saltar al reporte al finalizar
tabs = ["📝 REGISTRO", "📊 REPORTE FINAL"]
tab_active = st.radio("Navegación", tabs, label_visibility="collapsed", horizontal=True, index=st.session_state.tab_select)

if tab_active == "📝 REGISTRO":
    st.session_state.tab_select = 0
    if st.session_state.current_f is None:
        st.subheader("Nueva Escalera")
        st_name = st.text_input("ID Escalera:", st.session_state.st_id)
        limit = st.number_input("Piso Máximo:", min_value=1, value=st.session_state.limit_f)
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("P1"): st.session_state.update({"current_f":"1","limit_f":limit,"st_id":st_name,"dir":"UP"}); st.rerun()
        if c2.button(f"P{limit}"): st.session_state.update({"current_f":str(limit),"limit_f":limit,"st_id":st_name,"dir":"DOWN"}); st.rerun()
        if c3.button("BSM"): st.session_state.update({"current_f":"Basement","limit_f":limit,"st_id":st_name,"dir":"UP"}); st.rerun()
        if c4.button("RF"): st.session_state.update({"current_f":"Roof","limit_f":limit,"st_id":st_name,"dir":"DOWN"}); st.rerun()
    else:
        # Sugerencia de pisos
        p_act = st.session_state.current_f
        max_f = st.session_state.limit_f
        sug_dest = ""
        if p_act == "Basement": sug_dest = "1"
        elif p_act == "Roof": sug_dest = str(max_f)
        else:
            try:
                v = int(p_act)
                if st.session_state.dir == "UP": sug_dest = str(v + 1) if v < max_f else "Roof"
                else: sug_dest = str(v - 1) if v > 1 else "Basement"
            except: sug_dest = ""

        # MODO EDICIÓN
        e_idx = st.session_state.edit_idx
        if e_idx is not None:
            val = st.session_state.all_data[e_idx]
            st.warning(f"✏️ EDITANDO: {val['piso']}")
            t_orig, t_dest_val = val["piso"].split(" a ")
        else:
            val = {"steps": 0, "w1": 0.0, "l1": 0.0, "w2": 0.0, "l2": 0.0}
            t_orig, t_dest_val = p_act, sug_dest

        with st.form("f_registro", clear_on_submit=True):
            c_f1, c_f2 = st.columns(2)
            f_from = c_f1.text_input("Desde:", t_orig)
            f_to = c_f2.text_input("Hacia:", t_dest_val)
            t_steps = st.number_input("Steps:", value=val["steps"])
            st.write("**Landings**")
            c_a, c_b = st.columns(2)
            mw = c_a.number_input("Mid W", value=val["w1"]); ml = c_b.number_input("Mid L", value=val["l1"])
            fw = c_a.number_input("Floor W", value=val["w2"]); fl = c_b.number_input("Floor L", value=val["l2"])
            
            st.markdown('<div class="btn-save">', unsafe_allow_html=True)
            if st.form_submit_button("✅ ACTUALIZAR" if e_idx is not None else "💾 GUARDAR TRAMO"):
                nuevo = {"stair": st.session_state.st_id, "piso": f"{f_from} a {f_to}", "steps": t_steps, "area": (mw*ml)+(fw*fl), "w1": mw, "l1": ml, "w2": fw, "l2": fl}
                if e_idx is not None:
                    st.session_state.all_data[e_idx] = nuevo
                    st.session_state.edit_idx = None
                else:
                    st.session_state.all_data.append(nuevo)
                    st.session_state.current_f = f_to
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # BOTONES DE CONTROL AL LÍMITE (SOLO APARECEN AL FINALIZAR RECORRIDO)
        es_limite = (st.session_state.dir == "UP" and f_to in ["Roof", str(max_f)]) or (st.session_state.dir == "DOWN" and f_to in ["Basement", "1"])
        if es_limite:
            st.write("---")
            c_next, c_end = st.columns(2)
            if c_next.button("➕ OTRA ESCALERA"):
                num = len(set(x['stair'] for x in st.session_state.all_data)) + 1
                st.session_state.update({"current_f": None, "st_id": f"Escalera {chr(64+num)}", "edit_idx": None}); st.rerun()
            
            st.markdown('<div class="btn-finish">', unsafe_allow_html=True)
            if c_end.button("🛑 FINALIZAR EDIFICIO"):
                st.session_state.tab_select = 1 # Salta al reporte
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- HISTORIAL ---
    if st.session_state.all_data:
        st.write("---")
        for i, t in enumerate(reversed(st.session_state.all_data)):
            real_idx = len(st.session_state.all_data) - 1 - i
            col_info, col_ed, col_de = st.columns([0.7, 0.15, 0.15])
            col_info.markdown(f"**{t['piso']}** | {t['steps']} st | {t['area']:.2f} sf")
            st.markdown('<div class="btn-edit">', unsafe_allow_html=True)
            if col_ed.button("✏️", key=f"e_{real_idx}"):
                st.session_state.edit_idx = real_idx; st.rerun()
            st.markdown('</div><div class="btn-del">', unsafe_allow_html=True)
            if col_de.button("X", key=f"d_{real_idx}"):
                st.session_state.all_data.pop(real_idx); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.session_state.tab_select = 1
    # REPORTE DE DOS LÍNEAS
    reporte_txt = f"landing: {total_landings:.2f} sf\nsteps: {total_pasos}\n\ndetails\n"
    for esc in sorted(list(set(x['stair'] for x in st.session_state.all_data))):
        reporte_txt += f"\n- {esc}:\n"
        for tr in [x for x in st.session_state.all_data if x['stair'] == esc]:
            reporte_txt += f"  • {tr['piso']}: {tr['steps']} steps / {tr['area']:.2f} sf\n"
    
    st.markdown(f'<div class="copy-area">{reporte_txt}</div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🗑️ NUEVO PROYECTO (LIMPIAR TODO)"):
        st.session_state.clear(); st.rerun()
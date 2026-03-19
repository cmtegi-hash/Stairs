import streamlit as st

# Configuración iPhone - Interfaz "Apretada" Quirúrgica
st.set_page_config(page_title="Stair Master Pro", layout="wide")

# --- CSS AGRESIVO PARA IPHONE ---
st.markdown("""
    <style>
    /* Forzar que las columnas NO se apilen en vertical */
    [data-testid="column"] {
        display: inline-block !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
        padding: 0 2px !important;
    }
    
    /* Botones minúsculos y horizontales */
    .stButton > button {
        width: 100% !important;
        height: 2.2em !important; 
        font-size: 12px !important;
        padding: 0px !important;
        margin: 0px !important;
        line-height: 1 !important;
        border-radius: 6px !important;
    }
    
    /* Caja de totales compacta */
    .resumen-box {
        background-color: #1e1e1e; color: #28a745; 
        padding: 8px; border-radius: 6px; 
        border: 1px solid #28a745; text-align: center; margin-bottom: 5px;
    }
    .total-val { font-size: 16px; font-weight: bold; margin: 0 8px; }

    /* Inputs más apretados */
    .stNumberInput, .stTextInput { margin-bottom: -15px !important; }
    
    /* Colores específicos */
    .btn-save > div > div > button { background-color: #28a745 !important; color: white !important; }
    .btn-finish > div > div > button { background-color: #dc3545 !important; color: white !important; }
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

# --- CÁLCULOS ---
total_pasos = sum(x['steps'] for x in st.session_state.all_data)
total_landings = sum(x['area'] for x in st.session_state.all_data)

# --- TOTALES ARRIBA ---
st.markdown(f'<div class="resumen-box"><span class="total-val">📐 {total_landings:.2f} sf</span> <span class="total-val">🪜 {total_pasos} steps</span></div>', unsafe_allow_html=True)

tabs = ["📝 REGISTRO", "📊 REPORTE"]
tab_active = st.radio("Nav", tabs, label_visibility="collapsed", horizontal=True, index=st.session_state.tab_select)

if tab_active == "📝 REGISTRO":
    st.session_state.tab_select = 0
    if st.session_state.current_f is None:
        st_name = st.text_input("ID:", st.session_state.st_id)
        limit = st.number_input("Max:", min_value=1, value=st.session_state.limit_f)
        # BOTONES PEQUEÑOS EN FILA
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("P1"): st.session_state.update({"current_f":"1","limit_f":limit,"st_id":st_name,"dir":"UP"}); st.rerun()
        if c2.button(f"P{limit}"): st.session_state.update({"current_f":str(limit),"limit_f":limit,"st_id":st_name,"dir":"DOWN"}); st.rerun()
        if c3.button("BSM"): st.session_state.update({"current_f":"Basement","limit_f":limit,"st_id":st_name,"dir":"UP"}); st.rerun()
        if c4.button("RF"): st.session_state.update({"current_f":"Roof","limit_f":limit,"st_id":st_name,"dir":"DOWN"}); st.rerun()
    else:
        p_act, max_f = st.session_state.current_f, st.session_state.limit_f
        sug_dest = ""
        if p_act == "Basement": sug_dest = "1"
        elif p_act == "Roof": sug_dest = str(max_f)
        else:
            try:
                v = int(p_act)
                if st.session_state.dir == "UP": sug_dest = str(v + 1) if v < max_f else "Roof"
                else: sug_dest = str(v - 1) if v > 1 else "Basement"
            except: sug_dest = ""

        # EDICIÓN
        e_idx = st.session_state.edit_idx
        v = st.session_state.all_data[e_idx] if e_idx is not None else {"steps":None, "w1":None, "l1":None, "w2":None, "l2":None}
        t_orig, t_dest = (v["piso"].split(" a ") if e_idx is not None else (p_act, sug_dest))

        with st.form("f_reg", clear_on_submit=True):
            c_f1, c_f2 = st.columns(2)
            f_from = c_f1.text_input("De:", t_orig)
            f_to = c_f2.text_input("A:", t_dest)
            t_steps = st.number_input("Steps:", value=v["steps"], placeholder="Steps")
            
            st.write("Landings (W/L)")
            ca, cb, cc, cd = st.columns(4) # 4 columnas reales
            mw = ca.number_input("W1", value=v["w1"], placeholder="W")
            ml = cb.number_input("L1", value=v["l1"], placeholder="L")
            fw = cc.number_input("W2", value=v["w2"], placeholder="W")
            fl = cd.number_input("L2", value=v["l2"], placeholder="L")
            
            st.markdown('<div class="btn-save">', unsafe_allow_html=True)
            if st.form_submit_button("✅ GUARDAR"):
                s = t_steps if t_steps else 0
                area = ((mw if mw else 0)*(ml if ml else 0)) + ((fw if fw else 0)*(fl if fl else 0))
                nuevo = {"stair": st.session_state.st_id, "piso": f"{f_from} a {f_to}", "steps": s, "area": area, "w1": mw, "l1": ml, "w2": fw, "l2": fl}
                if e_idx is not None: st.session_state.all_data[e_idx] = nuevo; st.session_state.edit_idx = None
                else: st.session_state.all_data.append(nuevo); st.session_state.current_f = f_to
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        es_limite = (st.session_state.dir == "UP" and f_to in ["Roof", str(max_f)]) or (st.session_state.dir == "DOWN" and f_to in ["Basement", "1"])
        if es_limite:
            c_nxt, c_fin = st.columns(2)
            if c_nxt.button("➕ OTRA"):
                n = len(set(x['stair'] for x in st.session_state.all_data)) + 1
                st.session_state.update({"current_f": None, "st_id": f"Escalera {chr(64+n)}", "edit_idx": None}); st.rerun()
            st.markdown('<div class="btn-finish">', unsafe_allow_html=True)
            if c_fin.button("🛑 FIN"): st.session_state.tab_select = 1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # HISTORIAL SUPER APRETADO
    if st.session_state.all_data:
        for i, t in enumerate(reversed(st.session_state.all_data)):
            ridx = len(st.session_state.all_data) - 1 - i
            ci, ce, cd = st.columns([0.7, 0.15, 0.15])
            ci.write(f"**{t['piso']}**: {t['steps']}st|{t['area']:.1f}sf")
            if ce.button("✏️", key=f"e{ridx}"): st.session_state.edit_idx = ridx; st.rerun()
            if cd.button("X", key=f"d{ridx}"): st.session_state.all_data.pop(ridx); st.rerun()

else:
    st.session_state.tab_select = 1
    rep = f"landing: {total_landings:.2f} sf\nsteps: {total_pasos}\n\ndetails\n"
    for esc in sorted(list(set(x['stair'] for x in st.session_state.all_data))):
        rep += f"\n- {esc}:\n"
        for tr in [x for x in st.session_state.all_data if x['stair'] == esc]:
            rep += f"  • {tr['piso']}: {tr['steps']} steps / {tr['area']:.2f} sf\n"
    st.markdown(f'<div class="copy-area">{rep}</div>', unsafe_allow_html=True)
    if st.button("🗑️ NUEVO"): st.session_state.clear(); st.rerun()

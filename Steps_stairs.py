import streamlit as st

# Configuración iPhone - Interfaz "Apretada" Quirúrgica
st.set_page_config(page_title="Stair Master Pro", layout="wide")

# --- CSS DEFINITIVO PARA MATAR LOS BOTONES +/- ---
st.markdown("""
    <style>
    /* Forzar filas horizontales en columnas */
    [data-testid="column"] {
        display: inline-block !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
        padding: 0 2px !important;
    }
    
    /* ELIMINAR BOTONES +/- POR CSS (Chrome, Safari, iOS) */
    button[step="up"], button[step="down"] {
        display: none !important;
    }
    input[type=number] {
        -moz-appearance: textfield !important;
    }
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none !important; 
        margin: 0 !important; 
    }

    /* Caja de totales compacta */
    .resumen-box {
        background-color: #1e1e1e; color: #28a745; 
        padding: 8px; border-radius: 6px; 
        border: 1px solid #28a745; text-align: center; margin-bottom: 5px;
    }
    .total-val { font-size: 16px; font-weight: bold; margin: 0 8px; }

    /* Estilo para los botones seleccionables (Segmented Control) */
    div[data-testid="stHorizontalBlock"] { gap: 0px !important; }
    
    /* Colores botones de acción */
    .btn-save > div > div > button { background-color: #28a745 !important; color: white !important; width: 100%; }
    .btn-finish > div > div > button { background-color: #dc3545 !important; color: white !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA (SESSION STATE) ---
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

# --- HEADER DE TOTALES ---
st.markdown(f'<div class="resumen-box"><span class="total-val">📐 {total_landings:.2f} sf</span> <span class="total-val">🪜 {int(total_pasos)} steps</span></div>', unsafe_allow_html=True)

tabs = ["📝 REGISTRO", "📊 REPORTE"]
tab_active = st.radio("Nav", tabs, label_visibility="collapsed", horizontal=True, index=st.session_state.tab_select)

if tab_active == "📝 REGISTRO":
    st.session_state.tab_select = 0
    if st.session_state.current_f is None:
        st_name = st.text_input("ID Escalera:", st.session_state.st_id)
        limit = st.number_input("Piso Máximo:", min_value=1, value=st.session_state.limit_f, step=1)
        
        st.write("Selecciona Inicio (Seleccionable):")
        # BOTONES SELECCIONABLES QUE SE QUEDAN MARCADOS
        sel = st.segmented_control(
            "Inicio",
            options=["P1", f"P{limit}", "BSM", "RF"],
            selection_mode="single",
            label_visibility="collapsed"
        )
        
        if sel:
            d = "DOWN" if sel in [f"P{limit}", "RF"] else "UP"
            val = sel.replace("P", "") if "P" in sel else sel
            if val == "BSM": val = "Basement"
            if val == "RF": val = "Roof"
            st.session_state.update({"current_f": val, "limit_f": limit, "st_id": st_name, "dir": d})
            st.rerun()
            
    else:
        p_act, max_f = st.session_state.current_f, st.session_state.limit_f
        sug_dest = ""
        if p_act == "Basement": sug_dest = "1"
        elif p_act == "Roof": sug_dest = str(max_f)
        else:
            try:
                v_num = int(p_act)
                if st.session_state.dir == "UP": sug_dest = str(v_num + 1) if v_num < max_f else "Roof"
                else: sug_dest = str(v_num - 1) if v_num > 1 else "Basement"
            except: sug_dest = ""

        # Datos para edición o nuevo
        e_idx = st.session_state.edit_idx
        v = st.session_state.all_data[e_idx] if e_idx is not None else {"steps":0, "w1":0.0, "l1":0.0, "w2":0.0, "l2":0.0}
        t_orig, t_dest = (v["piso"].split(" a ") if e_idx is not None else (p_act, sug_dest))

        with st.form("f_reg", clear_on_submit=True):
            c_f1, c_f2 = st.columns(2)
            f_from = c_f1.text_input("De:", t_orig)
            f_to = c_f2.text_input("A:", t_dest)
            
            # Pasos sin botones +/-
            steps_val = st.number_input("Steps:", value=int(v["steps"]), step=0)
            
            st.write("Landings (W1 L1 | W2 L2)")
            ca, cb, cc, cd = st.columns(4)
            # CASILLAS INDIVIDUALES EN FILA, SIN BOTONES +/-
            mw = ca.number_input("W1", value=float(v["w1"]), step=0.0, format="%.1f", label_visibility="collapsed")
            ml = cb.number_input("L1", value=float(v["l1"]), step=0.0, format="%.1f", label_visibility="collapsed")
            fw = cc.number_input("W2", value=float(v["w2"]), step=0.0, format="%.1f", label_visibility="collapsed")
            fl = cd.number_input("L2", value=float(v["l2"]), step=0.0, format="%.1f", label_visibility="collapsed")
            
            st.markdown('<div class="btn-save">', unsafe_allow_html=True)
            if st.form_submit_button("✅ GUARDAR TRAMO"):
                area = (mw * ml) + (fw * fl)
                nuevo = {"stair": st.session_state.st_id, "piso": f"{f_from} a {f_to}", "steps": steps_val, "area": area, "w1": mw, "l1": ml, "w2": fw, "l2": fl}
                if e_idx is not None: 
                    st.session_state.all_data[e_idx] = nuevo
                    st.session_state.edit_idx = None
                else: 
                    st.session_state.all_data.append(nuevo)
                    st.session_state.current_f = f_to
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("⬅️ Volver a Selección de Piso"):
            st.session_state.current_f = None
            st.rerun()

    # HISTORIAL COMPACTO
    if st.session_state.all_data:
        st.divider()
        for i, t in enumerate(reversed(st.session_state.all_data)):
            ridx = len(st.session_state.all_data) - 1 - i
            ci, ce, cd = st.columns([0.7, 0.15, 0.15])
            ci.write(f"**{t['piso']}**: {int(t['steps'])}st|{t['area']:.1f}sf")
            if ce.button("✏️", key=f"e{ridx}"): 
                st.session_state.edit_idx = ridx
                st.rerun()
            if cd.button("X", key=f"d{ridx}"): 
                st.session_state.all_data.pop(ridx)
                st.rerun()

else:
    st.session_state.tab_select = 1
    rep = f"REPORT:\nTotal Landings: {total_landings:.2f} sf\nTotal Steps: {int(total_pasos)}\n"
    for esc in sorted(list(set(x['stair'] for x in st.session_state.all_data))):
        rep += f"\n- {esc}:\n"
        for tr in [x for x in st.session_state.all_data if x['stair'] == esc]:
            rep += f"  • {tr['piso']}: {int(tr['steps'])} steps | {tr['area']:.2f} sf\n"
    st.code(rep)
    if st.button("🗑️ BORRAR TODO"): 
        st.session_state.clear()
        st.rerun()

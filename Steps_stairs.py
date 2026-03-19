import streamlit as st

st.set_page_config(page_title="Stair Master Pro", layout="wide")

# --- CSS ---
st.markdown("""
<style>
[data-testid="column"] {
    display: inline-block !important;
    flex: 1 1 0% !important;
    min-width: 0px !important;
    padding: 0 2px !important;
}
.resumen-box {
    background-color: #1e1e1e; color: #28a745;
    padding: 8px; border-radius: 6px;
    border: 1px solid #28a745; text-align: center; margin-bottom: 5px;
}
.total-val { font-size: 16px; font-weight: bold; margin: 0 8px; }
.btn-save > div > div > button { background-color: #28a745 !important; color: white !important; width: 100%; }
.btn-finish > div > div > button { background-color: #dc3545 !important; color: white !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "all_data" not in st.session_state: st.session_state.all_data = []
if "limit_f" not in st.session_state: st.session_state.limit_f = 4
if "current_f" not in st.session_state: st.session_state.current_f = None
if "st_id" not in st.session_state: st.session_state.st_id = "Escalera A"
if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
if "dir" not in st.session_state: st.session_state.dir = "UP"
if "tab_select" not in st.session_state: st.session_state.tab_select = 0

# --- TOTALS ---
total_pasos = sum(x['steps'] for x in st.session_state.all_data)
total_landings = sum(x['area'] for x in st.session_state.all_data)

# --- HEADER ---
st.markdown(f'<div class="resumen-box"><span class="total-val">📐 {total_landings:.2f} sf</span> <span class="total-val">🪜 {int(total_pasos)} steps</span></div>', unsafe_allow_html=True)

tabs = ["📝 REGISTRO", "📊 REPORTE"]
tab_active = st.radio("Nav", tabs, label_visibility="collapsed", horizontal=True, index=st.session_state.tab_select)

# ======================================================
# REGISTRO
# ======================================================
if tab_active == "📝 REGISTRO":
    st.session_state.tab_select = 0

    if st.session_state.current_f is None:
        st_name = st.text_input("ID Escalera:", st.session_state.st_id)
        limit = st.number_input("Piso Máximo:", min_value=1, value=st.session_state.limit_f)

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

            st.session_state.update({
                "current_f": val,
                "limit_f": limit,
                "st_id": st_name,
                "dir": d
            })
            st.rerun()

    else:
        p_act = st.session_state.current_f
        max_f = st.session_state.limit_f

        # --- DETECTAR EXTREMO (NO BLOQUEA FORM) ---
        is_edge = False
        if st.session_state.dir == "UP":
            if str(p_act) == str(max_f) or p_act == "Roof":
                is_edge = True
        else:
            if str(p_act) == "1" or p_act == "Basement":
                is_edge = True

        # --- SUGERENCIA DESTINO ---
        sug_dest = ""
        try:
            v_num = int(p_act)
            if st.session_state.dir == "UP":
                sug_dest = str(v_num + 1) if v_num < max_f else "Roof"
            else:
                sug_dest = str(v_num - 1) if v_num > 1 else "Basement"
        except:
            if p_act == "Basement": sug_dest = "1"
            elif p_act == "Roof": sug_dest = str(max_f)

        e_idx = st.session_state.edit_idx
        v = st.session_state.all_data[e_idx] if e_idx is not None else {
            "steps": 0, "w1": 0, "l1": 0, "w2": 0, "l2": 0
        }

        t_orig, t_dest = (v["piso"].split(" a ") if e_idx is not None else (p_act, sug_dest))

        # --- FORM ---
        with st.form("f_reg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_from = c1.text_input("De:", t_orig)
            f_to = c2.text_input("A:", t_dest)

            steps_txt = st.text_input("Steps:", value="" if v["steps"] == 0 else str(v["steps"]))

            st.write("Landings (W1 L1 | W2 L2)")
            ca, cb, cc, cd = st.columns(4)

            w1_txt = ca.text_input("W1", value="" if v["w1"] == 0 else str(v["w1"]), label_visibility="collapsed")
            l1_txt = cb.text_input("L1", value="" if v["l1"] == 0 else str(v["l1"]), label_visibility="collapsed")
            w2_txt = cc.text_input("W2", value="" if v["w2"] == 0 else str(v["w2"]), label_visibility="collapsed")
            l2_txt = cd.text_input("L2", value="" if v["l2"] == 0 else str(v["l2"]), label_visibility="collapsed")

            st.markdown('<div class="btn-save">', unsafe_allow_html=True)

            if st.form_submit_button("✅ GUARDAR TRAMO"):

                def to_int(x):
                    try: return int(x)
                    except: return 0

                def to_float(x):
                    try: return float(x)
                    except: return 0.0

                s = to_int(steps_txt)
                w1, l1 = to_float(w1_txt), to_float(l1_txt)
                w2, l2 = to_float(w2_txt), to_float(l2_txt)

                area = (w1 * l1) + (w2 * l2)

                nuevo = {
                    "stair": st.session_state.st_id,
                    "piso": f"{f_from} a {f_to}",
                    "steps": s,
                    "area": area,
                    "w1": w1, "l1": l1,
                    "w2": w2, "l2": l2
                }

                if e_idx is not None:
                    st.session_state.all_data[e_idx] = nuevo
                    st.session_state.edit_idx = None
                else:
                    st.session_state.all_data.append(nuevo)
                    st.session_state.current_f = f_to

                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # --- BOTONES EXTRA SOLO EN EXTREMO ---
        if is_edge:
            st.divider()
            c1, c2 = st.columns(2)

            if c1.button("🔄 Nuevo Bloque"):
                st.session_state.current_f = None
                st.session_state.edit_idx = None
                st.rerun()

            if c2.button("📊 Finalizar"):
                st.session_state.tab_select = 1
                st.rerun()

        if st.button("⬅️ Cambiar Piso"):
            st.session_state.current_f = None
            st.rerun()

    # ======================================================
    # LISTADO AGRUPADO
    # ======================================================
    if st.session_state.all_data:
        st.divider()

        stairs = sorted(set(x['stair'] for x in st.session_state.all_data))

        for esc in stairs:
            is_active = esc == st.session_state.st_id

            st.markdown(
                f"### {'🟢' if is_active else '⚪'} {esc}" +
                (" (ACTIVA)" if is_active else "")
            )

            tramos = [x for x in st.session_state.all_data if x['stair'] == esc]

            for t in reversed(tramos):
                ridx = st.session_state.all_data.index(t)

                ci, ce, cd = st.columns([0.7, 0.15, 0.15])

                ci.write(f"**{t['piso']}**: {int(t['steps'])}st | {t['area']:.1f}sf")

                if ce.button("✏️", key=f"e{ridx}"):
                    st.session_state.edit_idx = ridx
                    st.session_state.st_id = esc
                    st.rerun()

                if cd.button("X", key=f"d{ridx}"):
                    st.session_state.all_data.pop(ridx)
                    st.rerun()

# ======================================================
# REPORTE
# ======================================================
else:
    st.session_state.tab_select = 1

    rep = f"REPORT:\nTotal Landings: {total_landings:.2f} sf\nTotal Steps: {int(total_pasos)}\n"

    for esc in sorted(set(x['stair'] for x in st.session_state.all_data)):
        rep += f"\n- {esc}:\n"
        for tr in [x for x in st.session_state.all_data if x['stair'] == esc]:
            rep += f"  • {tr['piso']}: {int(tr['steps'])} steps | {tr['area']:.2f} sf\n"

    st.code(rep)

    if st.button("🗑️ BORRAR TODO"):
        st.session_state.clear()
        st.rerun()

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="BIPÉA Analyzer Pro", page_icon="🍞", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffeeba;
        margin-bottom: 20px;
        font-weight: 500;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #ececf1 !important;
    }
    [data-testid="stMetricLabel"] { color: #4b5563 !important; font-weight: 700 !important; font-size: 1rem !important; }
    [data-testid="stMetricValue"] { color: #1f2937 !important; font-size: 1.8rem !important; }
    div[data-testid="stTextarea"] textarea { 
        font-size: 1.2rem !important; 
        border-radius: 12px; 
        border: 1px solid #d1d1d6; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DICTIONNAIRES ---
tr = {
    "Français": {
        "header_warn": "⚠️ Ce commentaire est une base de travail. Veuillez relire les paramètres et modifier l'hydratation si nécessaire avant validation.",
        "h_good": "Bonne hydratation", "h_med": "Assez bonne hydratation",
        "l_good": "bon lissage", "l_fast": "lissage un peu rapide", "l_slow": "lissage un peu lent",
        "p_fin": "En fin de pétrissage, pâte", "f_fac": "Au façonnage, pâte", "equi": "équilibrée",
        "same": "gardant le même profil tout au long du processus",
        "t_good": "Bonne tenue aux deux enfournements", "t_1": "au premier enfournement", "t_2": "au second",
        "t_ok": "bonne tenue", "t_miss": "un manque de tenue", "t_miss_imp": "un manque important de tenue",
        "a_very": "Très bel aspect des pains", "a_good": "Bel aspect des pains", "a_med": "Assez bel aspect des pains", "a_cor": "Aspect correct des pains", "a_poor": "Aspect médiocre des pains",
        "with": "avec", "sec": "section", "dev": "développement", "reg": "régularité", "grigne": "du coup de lame", "dec": "un déchirement du coup de lame",
        "col": "coloration de la croûte", "v_very": "Très bon volume", "v_good": "Bon volume", "v_sat": "Volume satisfaisant",
        "cons": "consistance", "ext": "extensibilité", "ela": "élasticité", "rel": "relâchante", "collant": "collante",
        "and": "et", "copy_btn": "📋 Copier le commentaire", "p_direct": "Pâte"
    },
    "English": {
        "header_warn": "⚠️ This comment is a working draft. Please review parameters and adjust hydration if needed before validation.",
        "h_good": "Good hydration", "h_med": "Fairly good hydration",
        "l_good": "good smoothing", "l_fast": "slightly fast smoothing", "l_slow": "slightly slow smoothing",
        "p_fin": "At the end of kneading, dough", "f_fac": "During shaping, dough", "equi": "balanced",
        "same": "keeping the same profile throughout the process",
        "t_good": "Good stability at both loadings", "t_1": "at the first loading", "t_2": "at the second",
        "t_ok": "good stability", "t_miss": "lack of stability", "t_miss_imp": "significant lack of stability",
        "a_very": "Very beautiful appearance", "a_good": "Beautiful appearance", "a_med": "Fairly beautiful appearance", "a_cor": "Correct appearance", "a_poor": "Poor appearance",
        "with": "with", "sec": "cross-section", "dev": "development", "reg": "regularity", "grigne": "of the blade cut", "dec": "tearing of the blade cut",
        "col": "crust coloration", "v_very": "Very good volume", "v_good": "Good volume", "v_sat": "Satisfactory volume",
        "cons": "consistency", "ext": "extensibility", "ela": "elasticity", "rel": "slackening", "collant": "sticky",
        "and": "and", "copy_btn": "📋 Copy comment", "p_direct": "Dough"
    }
}

# --- 3. FONCTIONS LOGIQUES ---
def get_score(df, idx, col_map):
    for col, sc in col_map.items():
        try:
            val = str(df.iloc[idx, col]).strip().upper()
            if val == 'X': return sc
        except: continue
    return 10

def find_label_score(df, label, col_map):
    for i in range(len(df)):
        vals = [str(v).strip().lower() for v in df.iloc[i].values]
        if any(label.lower() in s for s in vals): return get_score(df, i, col_map)
    return 10

def format_params_grouped(data_dict, lang_dict, lang_name):
    groups = {}
    for k, v in data_dict.items():
        if v != 10: groups.setdefault(v, []).append(lang_dict[k])
    res = []
    ints = {7: "en excès de", 4: "en excès important de", -7: "en manque de", -4: "en manque important de"} if lang_name == "Français" else {7: "excessive", 4: "highly excessive", -7: "lacking", -4: "highly lacking"}
    for score, labels in groups.items():
        prefix = ints.get(score, "")
        if lang_name == "Français":
            fmt = [f"d'{l}" if l[0] in "aeiouéèAEIOUÉÈ" else f"de {l}" for l in labels]
            clean_p = prefix.rsplit(' ', 1)[0]
            l_str = f" {lang_dict['and']} ".join([", ".join(fmt[:-1]), fmt[-1]]) if len(fmt) > 2 else f" {lang_dict['and']} ".join(fmt)
            res.append(f"{clean_p} {l_str}")
        else:
            l_str = f" {lang_dict['and']} ".join([", ".join(labels[:-1]), labels[-1]]) if len(labels) > 2 else f" {lang_dict['and']} ".join(labels)
            res.append(f"{prefix} {l_str}")
    return res

def join_final(lst, lang_dict):
    return f", ".join(lst[:-1]) + f" {lang_dict['and']} " + lst[-1] if len(lst) > 1 else (lst[0] if lst else lang_dict["equi"])

def safe_float(df, row, col):
    try:
        val = df.iloc[row, col]
        return float(val)
    except:
        return 0.0

# --- 4. INTERFACE ---
st.title("🍞 BIPÉA Analyzer Pro")

st.sidebar.header("⚙️ Configuration")
sample_type = st.sidebar.selectbox("1. Type d'échantillon", ["Farine de base", "Blé de force", "Farine corrigée"])
sel_lang = st.sidebar.selectbox("2. Langue", ["Français", "English"])
t = tr[sel_lang]
uploaded_file = st.sidebar.file_uploader("3. Charger l'Excel BIPÉA", type="xlsx")

st.markdown(f'<div class="warning-box">{t["header_warn"]}</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        c_map = {11: -1, 12: -4, 13: -7, 14: 10, 15: 7, 16: 4, 17: 1}
        
        # --- LECTURE NOTES ---
        n_hydra_score = safe_float(df, 30, 1) # B31
        hydra_pct = safe_float(df, 30, 1)
        n_pate = safe_float(df, 30, 5)
        n_asp = safe_float(df, 33, 5)
        vol = safe_float(df, 33, 1)
        n_tot = safe_float(df, 35, 5)

        m0, m1, m2, m3, m4 = st.columns(5)
        m0.metric("NOTE HYDRA.", f"{n_hydra_score:.1f}")
        m1.metric("NOTE TOTALE", f"{n_tot:.1f}/100")
        m2.metric("NOTE PÂTE", f"{n_pate:.1f}/30")
        m3.metric("NOTE ASPECT", f"{n_asp:.1f}/70")
        m4.metric("VOLUME", f"{int(vol)} cm³")

        # --- ANALYSE PÂTE ---
        lis = find_label_score(df, "Lissage", c_map)
        p_data = {"cons": find_label_score(df, "Consistance", c_map), "ext": find_label_score(df, "Extensibilité", c_map), "ela": find_label_score(df, "Elasticité", c_map)}
        cp, rp = find_label_score(df, "Collant", c_map), find_label_score(df, "Relâchement", c_map)
        f_data = {"ext": get_score(df, 21, c_map), "ela": get_score(df, 23, c_map)}
        cf = get_score(df, 20, c_map)

        def build_list(coll, data, rel=10, is_p=True):
            l = []
            if coll == 7: l.append(t["collant"])
            elif coll == 4: l.append("très collante" if sel_lang == "Français" else "very sticky")
            l.extend(format_params_grouped(data, t, sel_lang))
            if is_p and rel != 10: l.append(t["rel"])
            return l

        pl, fl = build_list(cp, p_data, rp, True), build_list(cf, f_data, is_p=False)
        pate_txt = f"{t['p_direct']} {join_final(pl, t)} {t['same']}." if pl == fl else f"{t['p_fin']} {join_final(pl, t)}. {t['f_fac']} {join_final(fl, t)}."

        # --- TENUE ---
        t1, t2 = get_score(df, 30, c_map), get_score(df, 31, c_map)
        def fmt_tenue(score):
            if score == 10: return t["t_ok"]
            if score == -4: return t["t_miss_imp"]
            return t["t_miss"]
        ten_txt = f" {t['t_good']}." if t1 == 10 and t2 == 10 else f" {fmt_tenue(t1).capitalize()} {t['t_1']} {t['and']} {fmt_tenue(t2)} {t['t_2']}."

        # --- SEUILS ASPECT ---
        if n_asp >= 65: a_base = t["a_very"]
        elif n_asp >= 60: a_base = t["a_good"]
        elif n_asp >= 50: a_base = t["a_med"]
        elif n_asp >= 30: a_base = t["a_cor"]
        else: a_base = t["a_poor"]

        # --- ANALYSE DÉTAILLÉE ASPECT (Coup de lame, Croûte, Section) ---
        # On récupère les scores des lignes spécifiques d'aspect
        sec_v = get_score(df, 33, c_map) # Section
        col_v = get_score(df, 34, c_map) # Coloration
        dev_v = get_score(df, 37, c_map) # Développement grigne
        reg_v = get_score(df, 38, c_map) # Régularité grigne
        dec_v = get_score(df, 39, c_map) # Déchirement

        s_asp = []
        if sec_v != 10: s_asp.append(f"{'un excès' if sec_v > 10 else 'un manque'} de {t['sec']}")
        
        # Logique pour la grigne (développement et régularité)
        if dev_v != 10 or reg_v != 10:
            if dev_v == reg_v:
                s_asp.append(f"{'un excès' if dev_v > 10 else 'un manque'} de {t['dev']} {t['and']} de {t['reg']} {t['grigne']}")
            else:
                g_tmp = [f"{'un excès' if v > 10 else 'un manque'} de {t[k]}" for v, k in [(dev_v, 'dev'), (reg_v, 'reg')] if v != 10]
                s_asp.append(f"{' '.join(g_tmp)} {t['grigne']}")
        
        if dec_v in [7, 4]: s_asp.append(t["dec"]) # Déchirement
        
        asp_f = a_base + (f" {t['with']} " + join_final(s_asp, t) if s_asp else "")
        col_txt = f"Un manque de {t['col']}." if col_v < 10 else ""

        # --- VOLUME ET FINAL ---
        h_limit = 63 if "force" in sample_type.lower() else 61
        h_txt = t["h_good"] if hydra_pct >= h_limit else t["h_med"]
        l_txt = {10: t["l_good"], 7: t["l_fast"], -7: t["l_slow"]}.get(lis, "correct")
        v_limit_very, v_limit_good = (1850, 1650) if "farine" in sample_type.lower() else (1750, 1550)
        v_txt = t["v_very"] if vol > v_limit_very else t["v_good"] if vol > v_limit_good else t["v_sat"]

        res = f"{h_txt}, {l_txt}. {pate_txt}{ten_txt}\n\n{asp_f}. {col_txt} {v_txt}."
        
        st.subheader(f"📝 Commentaire - {sample_type}")
        st.text_area("", value=res, height=260)
        components.html(f"<button onclick=\"navigator.clipboard.writeText(`{res}`);alert('Copié !')\" style=\"width:100%; background:#007bff; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;\">{t['copy_btn']}</button>", height=80)

    except Exception as e: 
        st.error(f"Erreur lors de l'analyse : {e}")

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="BIPÉA Analyzer Pro", page_icon="🍞", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #ececf1 !important;
    }
    [data-testid="stMetricLabel"] { color: #4b5563 !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] { color: #1f2937 !important; }
    div[data-testid="stTextarea"] textarea { 
        font-size: 1.1rem !important; 
        border-radius: 12px; 
        border: 1px solid #d1d1d6; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DICTIONNAIRE MULTILINGUE ---
tr = {
    "Français": {
        "h_good": "Bonne hydratation", "h_med": "Assez bonne hydratation", "h_sat": "Hydratation satisfaisante",
        "l_good": "bon lissage", "l_fast": "lissage un peu rapide", "l_slow": "lissage un peu lent",
        "p_fin": "En fin de pétrissage, pâte", "f_fac": "Au façonnage, pâte", "equi": "équilibrée",
        "same": "gardant le même profil tout au long du processus",
        "t_good": "Bonne tenue aux deux enfournements", "t_miss": "manque de tenue", "t_1": "au premier enfournement", "t_2": "au second",
        "a_very": "Très bel aspect des pains", "a_good": "Bel aspect des pains", "a_med": "Assez bel aspect des pains", "a_cor": "Aspect correct des pains", "a_poor": "Aspect médiocre des pains",
        "with": "avec", "sec": "de section", "dev": "développement", "reg": "régularité", "grigne": "du coup de lame", "dec": "un déchirement du coup de lame",
        "col": "coloration de la croûte", "v_very": "Très bon volume", "v_good": "Bon volume", "v_sat": "Volume satisfaisant",
        "collant": "collante", "collant_imp": "très collante", "cons": "de consistance", "ext": "d'extensibilité", "ela": "d'élasticité", "rel": "relâchante",
        "and": "et", "copy_btn": "📋 Copier le commentaire", "copy_ok": "Copié !", "p_direct": "Pâte"
    },
    "English": {
        "h_good": "Good hydration", "h_med": "Fairly good hydration", "h_sat": "Satisfactory hydration",
        "l_good": "good smoothing", "l_fast": "slightly fast smoothing", "l_slow": "slightly slow smoothing",
        "p_fin": "At the end of kneading, dough", "f_fac": "During shaping, dough", "equi": "balanced",
        "same": "keeping the same profile throughout the process",
        "t_good": "Good stability at both loadings", "t_miss": "lack of stability", "t_1": "at the first loading", "t_2": "at the second",
        "a_very": "Very beautiful appearance of the loaves", "a_good": "Beautiful appearance of the loaves", "a_med": "Fairly beautiful appearance of the loaves", "a_cor": "Correct appearance of the loaves", "a_poor": "Poor appearance of the loaves",
        "with": "with", "sec": "cross-section", "dev": "development", "reg": "regularity", "grigne": "of the blade cut", "dec": "tearing of the blade cut",
        "col": "crust coloration", "v_very": "Very good volume", "v_good": "Good volume", "v_sat": "Satisfactory volume",
        "collant": "sticky", "collant_imp": "very sticky", "cons": "consistency", "ext": "extensibility", "ela": "elasticity", "rel": "slackening",
        "and": "and", "copy_btn": "📋 Copy comment", "copy_ok": "Copied!", "p_direct": "Dough"
    }
}

# --- 3. FONCTIONS LOGIQUES ---
def get_intensity(score, lang_code, mode="pate"):
    prefixes = {"Français": ("en", "un"), "English": ("in", "a")}
    p_in, p_a = prefixes.get(lang_code, ("en", "un"))
    prefix = p_in if mode == "pate" else p_a
    ix = {"Français": {"e": "excès", "m": "manque", "i": "important"}, "English": {"e": "excess", "m": "lack", "i": "significant"}}.get(lang_code)
    
    if score == 7: return f"{prefix} {ix['e']}"
    if score == 4: return f"{prefix} {ix['e']} {ix['i']}"
    if score == -7: return f"{prefix} {ix['m']}"
    if score == -4: return f"{prefix} {ix['m']} {ix['i']}"
    return ""

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

# --- 4. INTERFACE ---
sel_lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])
t = tr[sel_lang]
uploaded_file = st.sidebar.file_uploader("📥 Charger l'Excel BIPÉA", type="xlsx")
type_p = st.sidebar.selectbox("Type de produit", ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"])

st.title(f"🍞 BIPÉA Analyzer - {sel_lang}")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        c_map = {11: -1, 12: -4, 13: -7, 14: 10, 15: 7, 16: 4, 17: 1}
        
        # Données de synthèse
        hydra, n_pate, n_asp, vol = float(df.iloc[30, 1]), float(df.iloc[30, 5]), float(df.iloc[33, 5]), float(df.iloc[33, 1])

        # Affichage Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Pâte /100", f"{n_pate:.1f}")
        m2.metric("Aspect /70", f"{n_asp:.1f}")
        m3.metric("Volume (cm³)", f"{int(vol)}")

        # Extraction Pâte
        lis = find_label_score(df, "Lissage", c_map)
        cp, conp, extp, elap, relp = find_label_score(df, "Collant", c_map), find_label_score(df, "Consistance", c_map), find_label_score(df, "Extensibilité", c_map), find_label_score(df, "Elasticité", c_map), find_label_score(df, "Relâchement", c_map)
        cf, conf, extf, elaf = get_score(df, 20, c_map), get_score(df, 19, c_map), get_score(df, 21, c_map), get_score(df, 23, c_map)

        # Extraction Tenue & Aspect
        t1, t2 = get_score(df, 30, c_map), get_score(df, 31, c_map)
        sec_v, col_v, dev_v, reg_v, dec_v = get_score(df, 33, c_map), get_score(df, 34, c_map), get_score(df, 37, c_map), get_score(df, 38, c_map), get_score(df, 39, c_map)

        # 1. Hydratation & Lissage
        h_lim = 63 if "force" in type_p.lower() else 61
        h_txt = t["h_good"] if hydra >= h_lim else t["h_med"]
        l_txt = {10: t["l_good"], 7: t["l_fast"], -7: t["l_slow"]}.get(lis, "correct")

        # 2. Logique Pâte
        def fmt_p(c, co, ex, el, r=10):
            res = []
            if c == 7: res.append(t["collant"])
            elif c == 4: res.append(t["collant_imp"])
            if co != 10: res.append(f"{get_intensity(co, sel_lang, 'pate')} {t['cons']}")
            if ex != 10: res.append(f"{get_intensity(ex, sel_lang, 'pate')} {t['ext']}")
            if el != 10: res.append(f"{get_intensity(el, sel_lang, 'pate')} {t['ela']}")
            if r != 10: res.append(t["rel"]) # Uniquement si r est passé (pétrissage)
            return res
        
        def join_l(lst): return f", ".join(lst[:-1]) + f" {t['and']} " + lst[-1] if len(lst) > 1 else (lst[0] if lst else t["equi"])

        pl, fl = fmt_p(cp, conp, extp, elap, relp), fmt_p(cf, conf, extf, elaf)
        
        # Comparaison stricte : si pl et fl diffèrent (ex: relâchante), on sépare.
        pate_txt = f"{t['p_direct']} {join_l(pl)} {t['same']}." if pl == fl else f"{t['p_fin']} {join_l(pl)}. {t['f_fac']} {join_l(fl)}."

        # 3. Tenue
        if t1==10 and t2==10: ten_txt = f" {t['t_good']}."
        else:
            txt_t1 = "Bonne tenue" if t1==10 else f"{get_intensity(t1, sel_lang, 'pate').capitalize()} de tenue"
            txt_t2 = "bonne tenue" if t2==10 else f"{get_intensity(t2, sel_lang, 'pate')} de tenue"
            ten_txt = f" {txt_t1} {t['t_1']} {t['and']} {txt_t2} {t['t_2']}."

        # 4. Aspect (Échelle Marion + Regroupement Grigne)
        if n_asp >= 65: a_base = t["a_very"]
        elif n_asp >= 60: a_base = t["a_good"]
        elif n_asp >= 50: a_base = t["a_med"]
        elif n_asp >= 30: a_base = t["a_cor"]
        else: a_base = t["a_poor"]
        
        s_asp = []
        if sec_v != 10: s_asp.append(f"{get_intensity(sec_v, sel_lang, 'aspect')} {t['sec']}")
        
        if dev_v != 10 or reg_v != 10:
            if dev_v == reg_v:
                s_asp.append(f"{get_intensity(dev_v, sel_lang, 'aspect')} de {t['dev']} {t['and']} de {t['reg']} {t['grigne']}")
            else:
                tmp = [f"{get_intensity(v, sel_lang, 'aspect')} de {lbl}" for v, lbl in [(dev_v, t['dev']), (reg_v, t['reg'])] if v != 10]
                s_asp.append(f"{join_l(tmp)} {t['grigne']}")
                
        if dec_v in [7,4]: s_asp.append(t["dec"])
        
        final_asp = a_base + (f" {t['with']} " + join_l(s_asp) if s_asp else "")
        col_txt = f"{get_intensity(col_v, sel_lang, 'aspect').capitalize()} {t['col']}." if col_v != 10 else ""
        v_txt = t["v_very"] if vol > 1850 else t["v_good"] if vol > 1650 else t["v_sat"]

        # 5. ASSEMBLAGE ET AFFICHAGE
        res_final = f"{h_txt}, {l_txt}. {pate_txt}{ten_txt}\n\n{final_asp}. {col_txt} {v_txt}."
        
        st.subheader("📝 Commentaire généré")
        st.text_area("", value=res_final, height=250)

        # Bouton Copie JS
        copy_js = f"""
        <button onclick="navigator.clipboard.writeText(`{res_final}`);alert('{t['copy_ok']}')" 
        style="width:100%; background:#007bff; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">
            {t['copy_btn']}
        </button>
        """
        components.html(copy_js, height=70)

    except Exception as e:
        st.error(f"Erreur d'analyse : {e}")

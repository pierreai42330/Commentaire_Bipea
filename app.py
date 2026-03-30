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
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #ececf1 !important;
    }
    div[data-testid="stTextarea"] textarea { 
        font-size: 1.1rem !important; 
        border-radius: 12px; 
        border: 1px solid #d1d1d6; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DICTIONNAIRE ---
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
        "collant": "collante", "collant_imp": "très collante", "cons": "consistance", "ext": "extensibilité", "ela": "élasticité", "rel": "relâchante",
        "and": "et", "copy_btn": "📋 Copier le commentaire", "copy_ok": "Copié !", "p_direct": "Pâte"
    }
}
t = tr["Français"]

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

def format_grouped_params(params_dict):
    """Regroupe les caractéristiques par score (ex: en excès de consistance et d'extensibilité)"""
    if not params_dict: return []
    groups = {}
    for label, score in params_dict.items():
        if score == 10: continue
        groups.setdefault(score, []).append(t[label])
    
    result_parts = []
    intensities = {
        7: "en excès de", 
        4: "en excès important de", 
        -7: "en manque de", 
        -4: "en manque important de"
    }
    
    for score, labels in groups.items():
        prefix = intensities.get(score, "")
        if len(labels) > 1:
            # Gestion de l'élision (d') pour l'extensibilité et l'élasticité
            formatted_labels = []
            for lbl in labels:
                if lbl[0] in 'aeiouéè': formatted_labels.append(f"d'{lbl}")
                else: formatted_labels.append(lbl)
            
            labels_str = f" {t['and']} ".join([", ".join(formatted_labels[:-1]), formatted_labels[-1]]) if len(labels) > 2 else f" {t['and']} ".join(formatted_labels)
            result_parts.append(f"{prefix} {labels_str}")
        else:
            result_parts.append(f"{prefix} {labels[0]}")
    return result_parts

def join_final(lst):
    return f", ".join(lst[:-1]) + f" {t['and']} " + lst[-1] if len(lst) > 1 else (lst[0] if lst else t["equi"])

# --- 4. INTERFACE ---
uploaded_file = st.sidebar.file_uploader("📥 Charger l'Excel BIPÉA", type="xlsx")
type_p = st.sidebar.selectbox("Type", ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        c_map = {11: -1, 12: -4, 13: -7, 14: 10, 15: 7, 16: 4, 17: 1}
        
        hydra, vol, n_asp = float(df.iloc[30, 1]), float(df.iloc[33, 1]), float(df.iloc[33, 5])
        lis = find_label_score(df, "Lissage", c_map)

        # Extraction Pétrissage
        p_params = {
            "cons": find_label_score(df, "Consistance", c_map),
            "ext": find_label_score(df, "Extensibilité", c_map),
            "ela": find_label_score(df, "Elasticité", c_map)
        }
        collant_p = find_label_score(df, "Collant", c_map)
        rel_p = find_label_score(df, "Relâchement", c_map)

        # Extraction Façonnage (On ignore Consistance et Relâchement ici)
        f_params = {
            "ext": get_score(df, 21, c_map),
            "ela": get_score(df, 23, c_map)
        }
        collant_f = get_score(df, 20, c_map)

        # Construction des listes
        def build_pate_list(coll_score, data_dict, is_pétrissage=True, r_score=10):
            l = []
            if coll_score == 7: l.append(t["collant"])
            elif coll_score == 4: l.append(t["collant_imp"])
            l.extend(format_grouped_params(data_dict))
            if is_pétrissage and r_score != 10: l.append(t["rel"])
            return l

        pl = build_pate_list(collant_p, p_params, True, rel_p)
        fl = build_pate_list(collant_f, f_params, False)
        
        pate_txt = f"{t['p_direct']} {join_final(pl)} {t['same']}." if pl == fl else f"{t['p_fin']} {join_final(pl)}. {t['f_fac']} {join_final(fl)}."

        # Tenue, Aspect et Volume
        t1, t2 = get_score(df, 30, c_map), get_score(df, 31, c_map)
        sec_v, col_v, dev_v, reg_v, dec_v = get_score(df, 33, c_map), get_score(df, 34, c_map), get_score(df, 37, c_map), get_score(df, 38, c_map), get_score(df, 39, c_map)

        h_txt = t["h_good"] if hydra >= (63 if "force" in type_p.lower() else 61) else t["h_med"]
        l_txt = {10: t["l_good"], 7: t["l_fast"], -7: t["l_slow"]}.get(lis, "correct")
        
        ten_txt = f" {t['t_good']}." if t1==10 and t2==10 else f" {('Bonne tenue' if t1==10 else 'Un manque de tenue')} {t['t_1']} {t['and']} {('bonne tenue' if t2==10 else 'un manque de tenue')} {t['t_2']}."

        a_base = t["a_very"] if n_asp >= 65 else t["a_good"] if n_asp >= 60 else t["a_med"] if n_asp >= 50 else t["a_cor"] if n_asp >= 30 else t["a_poor"]
        
        # Grigne regroupée
        s_asp = []
        if sec_v != 10: s_asp.append(f"{'un excès' if sec_v > 10 else 'un manque'} {t['sec']}")
        if dev_v != 10 or reg_v != 10:
            if dev_v == reg_v: s_asp.append(f"{'un excès' if dev_v > 10 else 'un manque'} de {t['dev']} {t['and']} de {t['reg']} {t['grigne']}")
            else:
                g_tmp = [f"{'un excès' if v > 10 else 'un manque'} de {t[k]}" for v, k in [(dev_v, 'dev'), (reg_v, 'reg')] if v != 10]
                s_asp.append(f"{' '.join(g_tmp)} {t['grigne']}")
        if dec_v in [7,4]: s_asp.append(t["dec"])
        
        asp_final = a_base + (f" {t['with']} " + join_final(s_asp) if s_asp else "")
        v_txt = t["v_very"] if vol > 1850 else t["v_good"] if vol > 1650 else t["v_sat"]
        col_txt = f"Un manque de {t['col']}." if col_v < 10 else ""

        res_final = f"{h_txt}, {l_txt}. {pate_txt}{ten_txt}\n\n{asp_final}. {col_txt} {v_txt}."
        
        st.subheader("Rapport de panification")
        st.text_area("", value=res_final, height=250)
        
        m1, m2 = st.columns(2)
        m1.metric("Volume", f"{int(vol)} cm³")
        m2.metric("Note Aspect", f"{n_asp:.1f}/70")

        components.html(f"<button onclick=\"navigator.clipboard.writeText(`{res_final}`);alert('Copié !')\" style=\"width:100%; background:#007bff; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;\">{t['copy_btn']}</button>", height=70)

    except Exception as e: st.error(f"Erreur d'analyse : {e}")

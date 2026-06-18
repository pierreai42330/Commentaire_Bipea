import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="BIPÉA Analyzer", page_icon="🍞", layout="wide")

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
        "p_fin": "En fin de pétrissage, pâte", "f_fac": "Au façonnage, pâte", "equi": "équilibrée",
        "same": "gardant le même profil tout au long du processus",
        "t_good": "Bonne tenue aux deux enfournements", "t_1": "au premier enfournement", "t_2": "au second",
        "t_ok": "bonne tenue",
        "a_very": "Très bel aspect des pains", "a_good": "Bel aspect des pains", "a_med": "Assez bel aspect des pains", "a_cor": "Aspect correct des pains", "a_poor": "Aspect médiocre des pains",
        "with": "avec", "dec": "un déchirement du coup de lame",
        "col": "coloration de la croûte", 
        "and": "et", "copy_btn": "📋 Copier le commentaire", "p_direct": "Pâte"
    },
    "English": {
        "header_warn": "⚠️ This comment is a working draft. Please review parameters and adjust hydration if needed before validation.",
        "h_good": "Good hydration", "h_med": "Fairly good hydration",
        "p_fin": "At the end of kneading, dough", "f_fac": "During shaping, dough", "equi": "balanced",
        "same": "keeping the same profile throughout the process",
        "t_good": "Good stability at both loadings", "t_1": "at the first loading", "t_2": "at the second",
        "t_ok": "good stability",
        "a_very": "Very beautiful appearance", "a_good": "Beautiful appearance", "a_med": "Fairly beautiful appearance", "a_cor": "Correct appearance", "a_poor": "Poor appearance",
        "with": "with", "dec": "tearing of the blade cut",
        "col": "crust coloration", 
        "and": "and", "copy_btn": "📋 Copy comment", "p_direct": "Dough"
    }
}

libelles_intensite = {
    "Français": {
        "L": "en manque très important", "M": "en manque important", "N": "en manque",
        "O": "", "P": "en excès", "Q": "en excès important", "R": "en excès très important"
    },
    "English": {
        "L": "with a very significant lack", "M": "with a significant lack", "N": "lacking",
        "O": "", "P": "with excessive", "Q": "with highly excessive", "R": "with a very high excess"
    }
}

parametres_mapping = {
    "Lissage": {
        "Français": {"L": "Lissage très lent", "M": "Lissage lent", "N": "Lissage un peu lent", "O": "Bon lissage", "P": "Lissage un peu rapide"},
        "English": {"L": "Very slow smoothing", "M": "Slow smoothing", "N": "Slightly slow smoothing", "O": "Good smoothing", "P": "Slightly fast smoothing"}
    },
    "Collant": {
        "Français": {"O": "", "P": "collante", "Q": "très collante", "R": "très collante"},
        "English": {"O": "", "P": "sticky", "Q": "very sticky", "R": "very sticky"}
    },
    "Consistance": {
        "Français": {"L": "en manque très important de consistance", "M": "en manque important de consistance", "N": "en manque de consistance", "O": "", "P": "en excès de consistance", "Q": "en excès important de consistance", "R": "en excès très important de consistance"},
        "English": {"L": "with a very significant lack of consistency", "M": "with a significant lack of consistency", "N": "lacking consistency", "O": "", "P": "with excessive consistency", "Q": "with highly excessive consistency", "R": "with a very high excess of consistency"}
    },
    "Relâchement": {
        "Français": {"L": "", "M": "", "N": "", "O": "", "P": "relachante", "Q": "très relachante", "R": "très relachante"},
        "English": {"L": "", "M": "", "N": "", "O": "", "P": "slackening", "Q": "highly slackening", "R": "highly slackening"}
    },
    "Tenue": {
        "Français": {"L": "une absence de tenue", "M": "un manque important de tenue", "N": "un manque de tenue", "O": "", "P": "", "Q": "", "R": ""},
        "English": {"L": "an absence of stability", "M": "a significant lack of stability", "N": "a lack of stability", "O": "", "P": "", "Q": "", "R": ""}
    }
}

# --- 3. FONCTIONS LOGIQUES ---
def get_column_letter(df, row_idx):
    col_letter_to_idx = {"L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17}
    for letter, col_idx in col_letter_to_idx.items():
        try:
            val = str(df.iloc[row_idx, col_idx]).strip().upper()
            if val == 'X':
                return letter
        except:
            continue
    return "O"

def get_description_by_column(df, row_idx, mapping_lang, default_value=""):
    letter = get_column_letter(df, row_idx)
    return mapping_lang.get(letter, default_value)

def get_grouped_ext_ela(df, ext_row, ela_row, lang):
    ext_letter = get_column_letter(df, ext_row)
    ela_letter = get_column_letter(df, ela_row)
    
    label_ext = "extensibilité" if lang == "Français" else "extensibility"
    label_ela = "élasticité" if lang == "Français" else "elasticity"
    conj = "et" if lang == "Français" else "and"

    if ext_letter == "O" and ela_letter == "O":
        return []

    if ext_letter == ela_letter:
        prefixe = libelles_intensite[lang][ext_letter]
        if lang == "Français":
            return [f"{prefixe} d'{label_ext} {conj} d'{label_ela}"]
        else:
            return [f"{prefixe} {label_ext} {conj} {label_ela}"]
            
    res = []
    if ext_letter != "O":
        prefixe_ext = libelles_intensite[lang][ext_letter]
        res.append(f"{prefixe_ext} d'{label_ext}" if lang == "Français" else f"{prefixe_ext} {label_ext}")
    if ela_letter != "O":
        prefixe_ela = libelles_intensite[lang][ela_letter]
        res.append(f"{prefixe_ela} d'{label_ela}" if lang == "Français" else f"{prefixe_ela} {label_ela}")
        
    return res

def get_score(df, idx, col_map):
    for col, sc in col_map.items():
        try:
            val = str(df.iloc[idx, col]).strip().upper()
            if val == 'X': return sc
        except: continue
    return 10

def join_final(lst, lang_dict):
    return f", ".join(lst[:-1]) + f" {lang_dict['and']} " + lst[-1] if len(lst) > 1 else (lst[0] if lst else lang_dict["equi"])

def safe_float(df, row, col):
    try:
        val = df.iloc[row, col]
        return float(val)
    except:
        return 0.0

# --- 4. INTERFACE ---
st.title("🍞 BIPÉA Analyzer")

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
        n_hydra_score = safe_float(df, 30, 1)
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

        # --- ANALYSE LISSAGE ---
        l_txt = get_description_by_column(df, 12, parametres_mapping["Lissage"][sel_lang], default_value="Lissage correct")
        
        # --- ANALYSE PÂTE COMPLÉMENTAIRE ---
        collant_txt = get_description_by_column(df, 13, parametres_mapping["Collant"][sel_lang], default_value="")
        consistance_txt = get_description_by_column(df, 14, parametres_mapping["Consistance"][sel_lang], default_value="")
        ext_ela_pétrissage = get_grouped_ext_ela(df, 15, 16, sel_lang)
        relachement_txt = get_description_by_column(df, 17, parametres_mapping["Relâchement"][sel_lang], default_value="")

        # Extraction dynamique des données du Façonnage
        ext_ela_façonnage = get_grouped_ext_ela(df, 21, 23, sel_lang)

        # Construction des listes finales de pâte
        def build_list(is_p=True):
            l = []
            if is_p:
                if collant_txt: l.append(collant_txt)
                if consistance_txt: l.append(consistance_txt)
                if ext_ela_pétrissage: l.extend(ext_ela_pétrissage)
                if relachement_txt: l.append(relachement_txt)
            else:
                if ext_ela_façonnage: l.extend(ext_ela_façonnage)
            return l

        pl, fl = build_list(is_p=True), build_list(is_p=False)
        pate_txt = f"{t['p_direct']} {join_final(pl, t)} {t['same']}." if pl == fl else f"{t['p_fin']} {join_final(pl, t)}. {t['f_fac']} {join_final(fl, t)}."

        # --- ANALYSE TENUE (Lignes 31 et 32 -> index 30 et 31) ---
        t1_txt = get_description_by_column(df, 30, parametres_mapping["Tenue"][sel_lang], default_value="")
        t2_txt = get_description_by_column(df, 31, parametres_mapping["Tenue"][sel_lang], default_value="")

        if not t1_txt and not t2_txt:
            ten_txt = f" {t['t_good']}."
        else:
            part_1 = f"{t1_txt if t1_txt else t['t_ok']} {t['t_1']}"
            part_2 = f"{t2_txt if t2_txt else t['t_ok']} {t['t_2']}"
            ten_txt = f" {part_1.capitalize()} {t['and']} {part_2}."

        # --- SEUILS ASPECT ---
        if n_asp >= 65: a_base = t["a_very"]
        elif n_asp >= 60: a_base = t["a_good"]
        elif n_asp >= 50: a_base = t["a_med"]
        elif n_asp >= 30: a_base = t["a_cor"]
        else: a_base = t["a_poor"]

        # --- ANALYSE EN PROFONDEUR DE L'ASPECT ---
        sec_lettre = get_column_letter(df, 33)   # Ligne 34
        gri_lettre = get_column_letter(df, 37)   # Ligne 38
        col_v = get_score(df, 34, c_map)          # Ligne 35
        dec_v = get_score(df, 39, c_map)          # Ligne 40

        mots_intensite = {
            "Français": {"L": "absence de ", "M": "manque important de ", "N": "manque de ", "O": "", "P": "excès de "},
            "English": {"L": "absence of ", "M": "significant lack of ", "N": "lack of ", "O": "", "P": "excess of "}
        }
        labels_aspect = {
            "Français": {"sec": "section", "gri": "développement du coup de lame"},
            "English": {"sec": "cross-section", "gri": "blade cut development"}
        }

        aspect_elements = []

        if sec_lettre == gri_lettre and sec_lettre in ["L", "M", "N", "P"]:
            qualif = mots_intensite[sel_lang][sec_lettre]
            lbl_sec = labels_aspect[sel_lang]["sec"]
            lbl_gri = labels_aspect[sel_lang]["gri"]
            aspect_elements.append(f"un {qualif}{lbl_sec}, de {lbl_gri}" if sel_lang == "Français" else f"a {qualif}{lbl_sec}, and {lbl_gri}")
        else:
            if sec_lettre in ["L", "M", "N", "P"]:
                qualif = mots_intensite[sel_lang][sec_lettre]
                lbl = labels_aspect[sel_lang]["sec"]
                aspect_elements.append(f"un {qualif}{lbl}" if sel_lang == "Français" else f"a {qualif}{lbl}")
            if gri_lettre in ["L", "M", "N", "P"]:
                qualif = mots_intensite[sel_lang][gri_lettre]
                lbl = labels_aspect[sel_lang]["gri"]
                aspect_elements.append(f"un {qualif}{lbl}" if sel_lang == "Français" else f"a {qualif}{lbl}")

        if dec_v in [7, 4]:
            if aspect_elements and sel_lang == "Français":
                phrase_prev = ", ".join(aspect_elements[:-1]) + f" {t['and']} " + aspect_elements[-1] if len(aspect_elements) > 1 else aspect_elements[0]
                asp_f = f"{a_base} {t['with']} {phrase_prev} {t['and']} avec {t['dec']}"
            else:
                aspect_elements.append(t["dec"])
                asp_f = f"{a_base} {t['with']} " + join_final(aspect_elements, t)
        else:
            asp_f = a_base + (f" {t['with']} " + join_final(aspect_elements, t) if aspect_elements else "")

        col_txt = f"Un manque de {t['col']}." if col_v < 10 else ""

        # --- DYNAMISATION DU BARÈME DE VOLUME ---
        is_ble_de_force = "force" in sample_type.lower()
        
        # Configuration des libellés selon la langue
        if sel_lang == "Français":
            v_labels = {
                "mediocre": "Volume médiocre", "correct": "Volume correct", 
                "satisfaisant": "Volume satisfaisant", "assez_bon": "Assez bon volume", 
                "bon": "Bon volume", "tres_bon": "Très bon volume"
            }
        else:
            v_labels = {
                "mediocre": "Poor volume", "correct": "Correct volume", 
                "satisfaisant": "Satisfactory volume", "assez_bon": "Fairly good volume", 
                "bon": "Good volume", "tres_bon": "Very good volume"
            }

        if is_ble_de_force:
            if vol > 1800: v_txt = v_labels["bon"]
            elif vol > 1600: v_txt = v_labels["assez_bon"]
            elif vol > 1500: v_txt = v_labels["satisfaisant"]
            elif vol > 1350: v_txt = v_labels["correct"]
            else: v_txt = v_labels["mediocre"]
        else:  # Farine de base et Farine corrigée
            if vol > 1800: v_txt = v_labels["tres_bon"]
            elif vol > 1600: v_txt = v_labels["bon"]
            elif vol > 1500: v_txt = v_labels["assez_bon"]
            elif vol > 1350: v_txt = v_labels["satisfaisant"]
            else: v_txt = v_labels["correct"]

        # --- HYDRATATION FACTOR ---
        h_limit = 63 if is_ble_de_force else 61
        h_txt = t["h_good"] if hydra_pct >= h_limit else t["h_med"]

        # Construction finale du texte
        res = f"{h_txt}, {l_txt.lower() if sel_lang == 'Français' else l_txt}. {pate_txt}{ten_txt}\n\n{asp_f}. {col_txt} {v_txt}."
        
        st.subheader(f"📝 Commentaire - {sample_type}")
        st.text_area("", value=res, height=260)
        components.html(f"<button onclick=\"navigator.clipboard.writeText(`{res}`);alert('Copié !')\" style=\"width:100%; background:#007bff; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;\">{t['copy_btn']}</button>", height=80)

    except Exception as e: 
        st.error(f"Erreur lors de l'analyse : {e}")

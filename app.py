import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="BIPÉA Analyzer Pro", page_icon="🍞", layout="wide")

# CSS pour améliorer le design
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stTextarea"] textarea { font-size: 1.1rem !important; font-family: 'Segoe UI', sans-serif; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIQUE DE TRADUCTION ---
lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English", "Español"])
tr = {
    "Français": {
        "h_good": "Bonne hydratation", "h_med": "Assez bonne hydratation", "h_sat": "Hydratation satisfaisante",
        "l_good": "bon lissage", "l_fast": "lissage un peu rapide", "l_slow": "lissage un peu lent",
        "p_fin": "En fin de pétrissage, pâte", "f_fac": "Au façonnage, pâte", "equi": "équilibrée",
        "same": "gardant le même profil tout au long du processus", "rel": "et relâchante après détente",
        "t_good": "Bonne tenue aux deux enfournements.", "t_miss": "manque de tenue", "t_miss_imp": "manque important de tenue",
        "t_1": "au 1er", "t_2": "au 2nd",
        "a_very": "Très bel aspect", "a_good": "Bel aspect", "a_med": "Assez bel aspect", "a_cor": "Aspect correct", "a_poor": "Aspect médiocre",
        "with": "avec", "sec": "de section", "dev": "de développement", "reg": "de régularité", "grigne": "du coup de lame", "dec": "un déchirement du coup de lame",
        "col": "de coloration de la croûte", "v_very": "Très bon volume", "v_good": "Bon volume", "v_sat": "Volume satisfaisant",
        "exc": "excès", "exc_imp": "excès important", "manq": "manque", "manq_imp": "manque important",
        "collant": "collante", "collant_imp": "très collante", "cons": "de consistance", "ext": "d'extensibilité", "ela": "d'élasticité",
        "and": "et", "copy_btn": "📋 Copier le commentaire", "copy_ok": "Copié !"
    },
    "English": {
        "h_good": "Good hydration", "h_med": "Fairly good hydration", "h_sat": "Satisfactory hydration",
        "l_good": "good smoothing", "l_fast": "slightly fast smoothing", "l_slow": "slightly slow smoothing",
        "p_fin": "At the end of mixing, dough was", "f_fac": "During shaping, dough was", "equi": "balanced",
        "same": "maintaining the same profile throughout the process", "rel": "and slackening after resting",
        "t_good": "Good stability during both bakes.", "t_miss": "lack of stability", "t_miss_imp": "significant lack of stability",
        "t_1": "at the 1st", "t_2": "at the 2nd",
        "a_very": "Very beautiful appearance", "a_good": "Beautiful appearance", "a_med": "Fairly beautiful appearance", "a_cor": "Correct appearance", "a_poor": "Poor appearance",
        "with": "with", "sec": "section", "dev": "development", "reg": "regularity", "grigne": "of the scoring", "dec": "a tearing of the scoring",
        "col": "crust coloring", "v_very": "Very good volume", "v_good": "Good volume", "v_sat": "Satisfactory volume",
        "exc": "excess", "exc_imp": "significant excess", "manq": "lack", "manq_imp": "significant lack",
        "collant": "sticky", "collant_imp": "very sticky", "cons": "consistency", "ext": "extensibility", "ela": "elasticity",
        "and": "and", "copy_btn": "📋 Copy Comment", "copy_ok": "Copied!"
    },
    "Español": {
        "h_good": "Buena hidratación", "h_med": "Bastante buena hidratación", "h_sat": "Hidratación satisfactoria",
        "l_good": "buen alisado", "l_fast": "alisado un poco rápido", "l_slow": "alisado un poco lento",
        "p_fin": "Al final del amasado, la masa estaba", "f_fac": "Durante el formado, la masa estaba", "equi": "equilibrada",
        "same": "manteniendo el mismo perfil durante todo el proceso", "rel": "y relajándose tras el reposo",
        "t_good": "Buena estabilidad en ambas hornadas.", "t_miss": "falta de estabilidad", "t_miss_imp": "falta importante de estabilidad",
        "t_1": "en la 1ª", "t_2": "en la 2ª",
        "a_very": "Muy buen aspecto", "a_good": "Buen aspecto", "a_med": "Bastante buen aspecto", "a_cor": "Aspecto correcto", "a_poor": "Aspecto mediocre",
        "with": "con", "sec": "de sección", "dev": "de desarrollo", "reg": "de regularidad", "grigne": "del corte", "dec": "un desgarro del corte",
        "col": "de coloración de la corteza", "v_very": "Muy buen volumen", "v_good": "Buen volumen", "v_sat": "Volumen satisfactorio",
        "exc": "exceso", "exc_imp": "exceso importante", "manq": "falta", "manq_imp": "falta importante",
        "collant": "pegajosa", "collant_imp": "muy pegajosa", "cons": "de consistencia", "ext": "de extensibilidad", "ela": "de elasticidad",
        "and": "y", "copy_btn": "📋 Copiar comentario", "copy_ok": "¡Copiado!"
    }
}
t = tr[lang]

# --- 3. INTERFACE PRINCIPALE ---
col_head1, col_head2 = st.columns([1, 4])
with col_head1:
    st.image("https://cdn-icons-png.flaticon.com/512/992/992743.png", width=80) # Icône pain
with col_head2:
    st.title("BIPÉA Analyzer Pro")
    st.caption("Génération automatique de rapports qualité Marion")

st.sidebar.divider()
type_p = st.sidebar.selectbox("Type de produit", ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"])
uploaded_file = st.sidebar.file_uploader("📥 Charger l'Excel BIPÉA", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        
        # --- LOGIQUE D'EXTRACTION ---
        c_scores = {11: -1, 12: -4, 13: -7, 14: 10, 15: 7, 16: 4, 17: 1}
        def ex_s(idx):
            for col, sc in c_scores.items():
                try:
                    if str(df.iloc[idx, col]).strip().upper() == 'X': return sc
                except: continue
            return 10
        def ex_l(label):
            for i in range(len(df)):
                txt = [str(v).strip().lower() for v in df.iloc[i].values]
                if any(label.lower() in s for s in txt): return ex_s(i)
            return 10
        def d_def(s):
            return {7: t["exc"], 4: t["exc_imp"], -7: t["manq"], -4: t["manq_imp"]}.get(s, "")

        # Extraction Data
        hydra, note_pate, note_aspect, vol, note_tot = float(df.iloc[30,1]), float(df.iloc[30,5]), float(df.iloc[33,5]), float(df.iloc[33,1]), float(df.iloc[35,5])
        lis = ex_l("Lissage")
        cp, conp, extp, elap, relp = ex_l("Collant"), ex_l("Consistance"), ex_l("Extensibilité"), ex_l("Elasticité"), ex_l("Relâchement")
        cf, conf, extf, elaf = ex_s(20), ex_s(19), ex_s(21), ex_s(23)
        t1, t2 = ex_s(30), ex_s(31)
        sec_v, col_v, dev_v, reg_v, dec_v = ex_s(33), ex_s(34), ex_s(37), ex_s(38), ex_s(39)

        # --- KPI CARDS ---
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Note Totale", f"{note_tot}/100")
        m2.metric("Pâte", f"{note_pate}/20")
        m3.metric("Aspect", f"{note_aspect}/20")
        m4.metric("Volume", f"{int(vol)} cm³")

        # --- GÉNÉRATION DU TEXTE ---
        h_lim = 63 if "force" in type_p.lower() else 61
        h_txt = t["h_good"] if hydra >= h_lim else t["h_med"] if hydra >= (h_lim-2) else t["h_sat"]
        l_txt = {10: t["l_good"], 7: t["l_fast"], -7: t["l_slow"]}.get(lis, "correct")

        def get_d(c, co, ex, el):
            res = []
            if c in [7,4]: res.append(t["collant"] if c==7 else t["collant_imp"])
            if co != 10: res.append(f"{d_def(co)} {t['cons']}")
            if ex != 10: res.append(f"{d_def(ex)} {t['ext']}")
            if el != 10: res.append(f"{d_def(el)} {t['ela']}")
            return res

        def f_lst(lst):
            return f", ".join(lst[:-1]) + f" {t['and']} " + lst[-1] if len(lst) > 1 else (lst[0] if lst else t["equi"])

        pl, fl = get_d(cp, conp, extp, elap), get_d(cf, conf, extf, elaf)
        rel_m = f" {t['rel']}" if relp == 7 else ""
        
        if (extf==extp and elaf==elap and cf==cp and conf==conp):
            comp_txt = f"{t['p_fin']} {f_lst(pl)}{rel_m} {t['same']}."
        else:
            comp_txt = f"{t['p_fin']} {f_lst(pl)}. {t['f_fac']} {f_lst(fl)}{rel_m}."

        def d_ten(s): return {10: t["t_good"], -7: t["t_miss"], -4: t["t_miss_imp"]}.get(s, t["t_miss"])
        if t1==10 and t2==10: ten_txt = f" {t['t_good']}"
        else: ten_txt = f" {d_ten(t1).capitalize()} {t['t_1']} {t['and']} {d_ten(t2)} {t['t_2']}."

        a_txt = t["a_very"] if note_aspect > 65 else t["a_good"] if note_aspect > 60 else t["a_med"] if note_aspect > 50 else t["a_cor"] if note_aspect > 30 else t["a_poor"]
        s_asp = []
        if sec_v != 10: s_asp.append(f"{d_def(sec_v)} {t['sec']}")
        g_l = []
        if dev_v != 10: g_l.append(f"{d_def(dev_v)} {t['dev']}")
        if reg_v != 10: g_l.append(f"{d_def(reg_v)} {t['reg']}")
        if g_l: s_asp.append(f"{f_lst(g_l)} {t['grigne']}")
        if dec_v in [7,4]: s_asp.append(t["dec"])
        
        final_asp = a_txt
        if s_asp: final_asp += f" {t['with']} " + f_lst(s_asp)
        col_txt = f"{d_def(col_v).capitalize()} {t['col']}." if col_v != 10 else ""
        v_txt = t["v_very"] if vol > 1850 else t["v_good"] if vol > 1650 else t["v_sat"]

        res_final = f"{h_txt}, {l_txt}. {comp_txt}{ten_txt}\n\n{final_asp}. {col_txt} {v_txt}."

        # --- AFFICHAGE DU RÉSULTAT ---
        st.subheader("📝 Rapport de panification")
        st.text_area("", value=res_final, height=220, key="report")

        # BOUTON COPIE STYLISÉ
        copy_js = f"""
        <div style="text-align: center;">
            <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold; width: 100%; transition: 0.3s;">
                {t['copy_btn']}
            </button>
        </div>
        <script>
        function copyToClipboard() {{
            const text = `{res_final}`;
            navigator.clipboard.writeText(text).then(() => {{
                alert("{t['copy_ok']}");
            }});
        }}
        </script>
        """
        components.html(copy_js, height=100)

    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse : {e}")
        st.info("Vérifiez que le format du fichier correspond bien au protocole BIPÉA.")

else:
    st.info("👋 Bienvenue ! Veuillez charger un fichier Excel dans la barre latérale pour commencer.")

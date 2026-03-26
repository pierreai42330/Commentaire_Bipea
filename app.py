import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Commentaire de Bipéa", page_icon="🍞")

st.title("🍞 Générateur de Commentaires")

# 2. BARRE LATÉRALE (LANGUE & TYPE)
st.sidebar.header("Configuration")
lang = st.sidebar.selectbox("Langue / Language / Idioma :", ["Français", "English", "Español"])

# Libellés selon la langue
label_type = "Type de produit" if lang == "Français" else "Product Type" if lang == "English" else "Tipo de producto"
type_p = st.sidebar.selectbox(label_type, ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"])

# 3. DICTIONNAIRE DE TRADUCTION TECHNIQUE
tr = {
    "Français": {
        "h_good": "Bonne hydratation", "h_med": "Assez bonne hydratation", "h_sat": "Hydratation satisfaisante",
        "l_good": "bon lissage", "l_fast": "lissage un peu rapide", "l_slow": "lissage un peu lent",
        "p_fin": "En fin de pétrissage, pâte", "f_fac": "Au façonnage, pâte", "equi": "équilibrée",
        "same": "gardant le même profil tout au long du processus", "rel": "et relâchante après détente",
        "t_good": "Bonne tenue aux deux enfournements.", "t_miss": "manque de tenue", "t_miss_imp": "manque important de tenue",
        "t_1": "au premier enfournement", "t_2": "au second",
        "a_very": "Très bel aspect du pain", "a_good": "Bel aspect du pain", "a_med": "Assez bel aspect du pain", "a_cor": "Aspect correct du pain", "a_poor": "Aspect médiocre du pain",
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
        "t_1": "at the first bake", "t_2": "at the second",
        "a_very": "Very beautiful bread appearance", "a_good": "Beautiful bread appearance", "a_med": "Fairly beautiful bread appearance", "a_cor": "Correct bread appearance", "a_poor": "Poor bread appearance",
        "with": "with", "sec": "section", "dev": "development", "reg": "regularity", "grigne": "of the scoring", "dec": "a tearing of the scoring",
        "col": "crust coloring", "v_very": "Very good volume", "v_good": "Good volume", "v_sat": "Satisfactory volume",
        "exc": "excess", "exc_imp": "significant excess", "manq": "lack", "manq_imp": "significant lack",
        "collant": "sticky", "collant_imp": "very sticky", "cons": "consistency", "ext": "extensibility", "ela": "elasticity",
        "and": "and", "copy_btn": "📋 Copy Comment", "copy_ok": "Copied!"
    },
    "Español": {
        "h_good": "Buena hidratación", "h_med": "Bastante buena hidratación", "h_sat": "Hidratación satisfactoria",
        "l_good": "buen alisado", "l_fast": "alisado un poco rápido", "l_slow": "alisado un peu lento",
        "p_fin": "Al final del amasado, la masa estaba", "f_fac": "Durante el formado, la masa estaba", "equi": "equilibrada",
        "same": "manteniendo el mismo perfil durante todo el proceso", "rel": "y relajándose tras el reposo",
        "t_good": "Buena estabilidad en ambas hornadas.", "t_miss": "falta de estabilidad", "t_miss_imp": "falta importante de estabilidad",
        "t_1": "en la primera hornada", "t_2": "en la segunda",
        "a_very": "Muy buen aspecto del pan", "a_good": "Buen aspecto del pan", "a_med": "Bastante buen aspecto del pan", "a_cor": "Aspecto correcto del pan", "a_poor": "Aspecto mediocre del pan",
        "with": "con", "sec": "de sección", "dev": "de desarrollo", "reg": "de regularidad", "grigne": "del corte", "dec": "un desgarro del corte",
        "col": "de coloración de la corteza", "v_very": "Muy buen volumen", "v_good": "Buen volumen", "v_sat": "Volumen satisfactorio",
        "exc": "exceso", "exc_imp": "exceso importante", "manq": "falta", "manq_imp": "falta importante",
        "collant": "pegajosa", "collant_imp": "muy pegajosa", "cons": "de consistance", "ext": "de extensibilidad", "ela": "de elasticidad",
        "and": "y", "copy_btn": "📋 Copiar comentario", "copy_ok": "¡Copiado!"
    }
}

t = tr[lang]

# 4. CHARGEMENT EXCEL
uploaded_file = st.file_uploader("Fichier Excel BIPÉA (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)

        # Logique d'extraction des scores
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

        # Extraction des données clés
        hydra = float(df.iloc[30, 1])      
        note_pate = float(df.iloc[30, 5])   
        note_aspect = float(df.iloc[33, 5]) 
        vol = float(df.iloc[33, 1])  
        note_tot = float(df.iloc[35, 5]) 

        # Paramètres
        lis = ex_l("Lissage")
        cp, conp, extp, elap, relp = ex_l("Collant"), ex_l("Consistance"), ex_l("Extensibilité"), ex_l("Elasticité"), ex_l("Relâchement")
        cf, conf, extf, elaf = ex_s(20), ex_s(19), ex_s(21), ex_s(23)
        t1, t2 = ex_s(30), ex_s(31)
        sec_v, col_v, dev_v, reg_v, dec_v = ex_s(33), ex_s(34), ex_s(37), ex_s(38), ex_s(39)

        # 5. RÉDACTION DU COMMENTAIRE
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

        # Aspect
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

        # Final String
        res_final = f"{h_txt}, {l_txt}. {comp_txt}{ten_txt}\n\n{final_asp}. {col_txt} {v_txt}."

        # 6. AFFICHAGE ET COPIE
        st.divider()
        st.subheader("Résultat / Result / Resultado")
        st.text_area("", value=res_final, height=200, key="output_text")

        # Bouton Bleu de Copie
        copy_js = f"""
        <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
            {t['copy_btn']}
        </button>
        <script>
        function copyToClipboard() {{
            const text = `{res_final}`;
            navigator.clipboard.writeText(text).then(() => {{
                alert("{t['copy_ok']}");
            }});
        }}
        </script>
        """
        components.html(copy_js, height=80)
        
        st.info(f"Notes: Total {note_tot} | Pâte {note_pate} | Aspect {note_aspect} | Vol {vol}")

    except Exception as e:
        st.error(f"Erreur d'analyse : {e}")

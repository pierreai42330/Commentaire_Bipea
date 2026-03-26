import streamlit as st
import pandas as pd
import io

# Configuration de la page
st.set_page_config(page_title="Commentaire Bipéa", page_icon="🍞")

st.title("🍞 Commentaire Bipéa")
st.write("Analyse automatique selon les protocoles BIPÉA.")

# 1. Barre latérale pour le choix du produit
st.sidebar.header("Configuration")
type_p = st.sidebar.selectbox(
    "Type de produit :",
    ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"]
)

# 2. Zone de chargement
uploaded_file = st.file_uploader("Charger le fichier Excel BIPÉA (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)

        # --- LOGIQUE D'EXTRACTION V20 ---
        colonnes_scores = {11: -1, 12: -4, 13: -7, 14: 10, 15: 7, 16: 4, 17: 1}

        def ex_score(idx):
            for col, sc in colonnes_scores.items():
                try:
                    if str(df.iloc[idx, col]).strip().upper() == 'X': return sc
                except: continue
            return 10

        def ex_label(label):
            for i in range(len(df)):
                txt = [str(v).strip().lower() for v in df.iloc[i].values]
                if any(label.lower() in s for s in txt): return ex_score(i)
            return 10

        def desc_defaut(s):
            return {7: "excès", 4: "excès important", 1: "excès très important", 
                    -7: "manque", -4: "manque important", -1: "manque très important"}.get(s, "")

        # --- EXTRACTION DES DONNÉES ---
        hydra = float(df.iloc[30, 1])      # B31
        note_pate = float(df.iloc[30, 5])   # F31
        note_aspect = float(df.iloc[33, 5]) # F34
        volume_val = float(df.iloc[33, 1])  # B34
        note_totale = float(df.iloc[35, 5]) # F36

        # Données techniques
        lis = ex_label("Lissage")
        col_p = ex_label("Collant de la pâte")
        con_p = ex_label("Consistance")
        ext_p = ex_label("Extensibilité")
        ela_p = ex_label("Elasticité")
        rel_p = ex_label("Relâchement")
        ext_f = ex_score(21) 
        ela_f = ex_score(23)
        t1 = ex_score(30)
        t2 = ex_score(31)
        sec_v = ex_score(33) 
        col_v = ex_score(34) 
        dev_v = ex_score(37) 
        reg_v = ex_score(38) 
        dec_v = ex_score(39) 

        # --- RÉDACTION DU COMMENTAIRE ---
        
        # 1. Hydratation & Lissage
        if type_p == "Blé de force":
            h_txt = "Bonne hydratation" if hydra >= 63 else "Assez bonne hydratation" if hydra >= 61 else "Hydratation satisfaisante" if hydra >= 60 else "Hydratation un peu faible"
        else:
            h_txt = "Bonne hydratation" if hydra >= 61 else "Assez bonne hydratation" if hydra >= 60 else "Hydratation satisfaisante" if hydra >= 58 else "Hydratation un peu faible"
        
        l_txt = {10: "bon lissage", 7: "lissage un peu rapide", -7: "lissage un peu lent", -4: "lissage lent"}.get(lis, "lissage correct")

        # 2. Pétrissage / Façonnage / Tenue
        p_details = []
        if col_p in [7, 4]: p_details.append("pâte collante" if col_p==7 else "pâte très collante")
        if con_p != 10: p_details.append(f"pâte en {desc_defaut(con_p)} de consistance")
        if ext_p != 10: p_details.append(f"pâte en {desc_defaut(ext_p)} d'extensibilité")
        if ela_p != 10: p_details.append(f"pâte en {desc_defaut(ela_p)} d'élasticité")
        if rel_p == 7: p_details.append("pâte relâchante après détente")
        p_txt = "En fin de pétrissage, " + ("pâte équilibrée." if not p_details else p_details[0] + ".")

        f_txt = "Au façonnage, pâte gardant le même profil tout au long du processus." if (ext_f == ext_p and ela_f == ela_p) else f"Au façonnage, pâte {desc_defaut(ext_f)} d'extensibilité et {desc_defaut(ela_f)} d'élasticité."
        
        def desc_t(score): return {-7: "manque de tenue", -4: "manque important de tenue", -1: "absence de tenue"}.get(score, "bonne tenue")
        t_txt = "Bonne tenue aux deux enfournements." if (t1 == 10 and t2 == 10) else f"{desc_t(t1).capitalize()} au premier enfournement et {desc_t(t2)} au second."

        # 3. Aspect & Coup de lame (Regroupement)
        if note_aspect > 65: a_base = "Très bel aspect du pain"
        elif note_aspect > 60: a_base = "Bel aspect du pain"
        elif note_aspect > 50: a_base = "Assez bel aspect du pain"
        elif note_aspect > 30: a_base = "Aspect correct du pain"
        else: a_base = "Aspect médiocre du pain"

        suite_aspect = []
        if sec_v != 10: suite_aspect.append(f"un {desc_defaut(sec_v)} de section")
        
        gr_el = []
        if dev_v != 10: gr_el.append(f"{desc_defaut(dev_v)} de développement")
        if reg_v != 10: gr_el.append(f"{desc_defaut(reg_v)} de régularité")
        if gr_el: suite_aspect.append(f"un {' et '.join(gr_el)} du coup de lame")
        
        if dec_v == 7: suite_aspect.append("un déchirement du coup de lame")
        elif dec_v == 4: suite_aspect.append("un déchirement important du coup de lame")

        final_aspect = a_base
        if suite_aspect:
            final_aspect += " avec " + (", ".join(suite_aspect[:-1]) + " et " + suite_aspect[-1] if len(suite_aspect) > 1 else suite_aspect[0])
        
        color_txt = f" {desc_defaut(col_v).capitalize()} de coloration de la croûte." if col_v != 10 else ""

        # 4. Volume
        if type_p == "Farine corrigée":
            v_lib = "Très bon volume" if volume_val > 2000 else "Bon volume" if volume_val > 1900 else "Assez bon volume" if volume_val > 1800 else "Volume satisfaisant"
        elif type_p == "Blé de force":
            v_lib = "Bon volume" if volume_val > 1800 else "Assez bon volume" if volume_val > 1700 else "Volume satisfaisant" if volume_val > 1600 else "Volume correct"
        else:
            v_lib = "Bon volume" if volume_val > 1600 else "Assez bon volume" if volume_val > 1500 else "Volume satisfaisant" if volume_val > 1450 else "Volume correct"

        # --- AFFICHAGE ---
        st.divider()
        st.subheader(f"📝 Résultat pour : {type_p}")
        
        # Le commentaire rédigé
        st.success(f"{h_txt}, {l_txt}. {p_txt} {f_txt} {t_txt}\n\n{final_aspect}.{color_txt} {v_lib}.")

        # Le bloc données chiffrées
        st.info(f"**Données chiffrées :** \n"
                f"Note Totale : **{note_totale}** | Note Pâte : **{note_pate}** | Note Aspect : **{note_aspect}** \n"
                f"Volume : **{volume_val} cm³** | Hydratation : **{hydra}%**")

    except Exception as e:
        st.error(f"Erreur d'analyse : {e}")

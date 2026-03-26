import streamlit as st
import pandas as pd
import io

# Configuration de la page
st.set_page_config(page_title="Générateur BIPÉA Marion", page_icon="🍞")

st.title("🍞 Générateur de Commentaires Marion")
st.write("Analyse automatique selon les protocoles BIPÉA.")

# 1. Barre latérale
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

        # --- LOGIQUE D'EXTRACTION ---
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

        # --- DONNÉES NUMÉRIQUES ---
        hydra = float(df.iloc[30, 1])      # B31
        note_pate = float(df.iloc[30, 5])   # F31
        note_aspect = float(df.iloc[33, 5]) # F34
        volume_val = float(df.iloc[33, 1])  # B34
        note_totale = float(df.iloc[35, 5]) # F36

        # --- PARAMÈTRES TECHNIQUES ---
        # Pétrissage (P)
        lis = ex_label("Lissage")
        col_p = ex_label("Collant de la pâte")
        con_p = ex_label("Consistance")
        ext_p = ex_label("Extensibilité")
        ela_p = ex_label("Elasticité")
        rel_p = ex_label("Relâchement")
        
        # Façonnage (F)
        col_f = ex_score(20) # Ligne 21, colonne Collant (index 20 souvent selon ton Excel)
        con_f = ex_score(19) # Ligne 20
        ext_f = ex_score(21) # Ligne 22
        ela_f = ex_score(23) # Ligne 24

        # Pain
        t1 = ex_score(30)
        t2 = ex_score(31)
        sec_v = ex_score(33) 
        col_v = ex_score(34) 
        dev_v = ex_score(37) 
        reg_v = ex_score(38) 
        dec_v = ex_score(39) 

        # --- RÉDACTION ---
        
        # 1. Hydratation & Lissage
        if type_p == "Blé de force":
            h_txt = "Bonne hydratation" if hydra >= 63 else "Assez bonne hydratation" if hydra >= 61 else "Hydratation satisfaisante" if hydra >= 60 else "Hydratation un peu faible"
        else:
            h_txt = "Bonne hydratation" if hydra >= 61 else "Assez bonne hydratation" if hydra >= 60 else "Hydratation satisfaisante" if hydra >= 58 else "Hydratation un peu faible"
        
        l_txt = {10: "bon lissage", 7: "lissage un peu rapide", -7: "lissage un peu lent"}.get(lis, "lissage correct")

        # 2. Comportement Pâte (Synthèse Pétrissage + Façonnage)
        # On vérifie si TOUT est identique entre P et F
        identique = (ext_f == ext_p and ela_f == ela_p and col_f == col_p and con_f == con_p)

        p_details = []
        if col_p in [7, 4]: p_details.append("pâte collante" if col_p==7 else "pâte très collante")
        if con_p != 10: p_details.append(f"pâte en {desc_defaut(con_p)} de consistance")
        if ext_p != 10: p_details.append(f"pâte en {desc_defaut(ext_p)} d'extensibilité")
        if ela_p != 10: p_details.append(f"pâte en {desc_defaut(ela_p)} d'élasticité")
        
        if identique:
            comportement_txt = "Pâte " + (", ".join(p_details) if p_details else "équilibrée") + " gardant le même profil tout au long du processus."
        else:
            # On détaille les deux étapes si ça change
            debut = "En fin de pétrissage, pâte " + (", ".join(p_details) if p_details else "équilibrée") + "."
            f_details = []
            if col_f in [7, 4]: f_details.append("collante" if col_f==7 else "très collante")
            if con_f != 10: f_details.append(f"{desc_defaut(con_f)} de consistance")
            if ext_f != 10: f_details.append(f"{desc_defaut(ext_f)} d'extensibilité")
            if ela_f != 10: f_details.append(f"{desc_defaut(ela_f)} d'élasticité")
            fin = " Au façonnage, pâte " + (", ".join(f_details) if f_details else "équilibrée") + "."
            comportement_txt = debut + fin

        # Relâchement & Tenue
        rel_txt = " Pâte relâchante après détente." if rel_p == 7 else ""
        def desc_t(score): return {-7: "manque de tenue", -4: "manque important de tenue"}.get(score, "bonne tenue")
        t_txt = f" {desc_t(t1).capitalize()} au premier enfournement et {desc_t(t2)} au second." if (t1 != 10 or t2 != 10) else " Bonne tenue aux deux enfournements."

        # 3. Aspect
        a_base = "Très bel aspect du pain" if note_aspect > 65 else "Bel aspect du pain" if note_aspect > 60 else "Assez bel aspect du pain" if note_aspect > 50 else "Aspect correct du pain"
        suite_aspect = []
        if sec_v != 10: suite_aspect.append(f"un {desc_defaut(sec_v)} de section")
        gr_el = []
        if dev_v != 10: gr_el.append(f"{desc_defaut(dev_v)} de développement")
        if reg_v != 10: gr_el.append(f"{desc_defaut(reg_v)} de régularité")
        if gr_el: suite_aspect.append(f"un {' et '.join(gr_el)} du coup de lame")
        if dec_v in [7, 4]: suite_aspect.append("un déchirement du coup de lame")
        
        final_aspect = a_base
        if suite_aspect:
            final_aspect += " avec " + (", ".join(suite_aspect[:-1]) + " et " + suite_aspect[-1] if len(suite_aspect) > 1 else suite_aspect[0])
        color_txt = f" {desc_defaut(col_v).capitalize()} de coloration de la croûte." if col_v != 10 else ""

        # 4. Volume
        if type_p == "Farine corrigée":
            v_lib = "Très bon volume" if volume_val > 2000 else "Bon volume" if volume_val > 1900 else "Assez bon volume"
        else:
            v_lib = "Bon volume" if volume_val > 1600 else "Assez bon volume" if volume_val > 1500 else "Volume satisfaisant"

        # --- AFFICHAGE ---
        st.divider()
        st.success(f"{h_txt}, {l_txt}. {comportement_txt}{rel_txt}{t_txt}\n\n{final_aspect}.{color_txt} {v_lib}.")
        
        st.info(f"**Données :** Note Totale: **{note_totale}** | Pâte: **{note_pate}** | Aspect: **{note_aspect}** | Volume: **{volume_val}** | Hydra: **{hydra}%**")

    except Exception as e:
        st.error(f"Erreur : {e}")

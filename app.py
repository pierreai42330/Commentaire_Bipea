import streamlit as st
import pandas as pd
import io

# Configuration de la page
st.set_page_config(page_title="Générateur BIPÉA Marion", page_icon="🍞")

st.title("🍞 Générateur de Commentaires Marion")

# 1. Barre latérale
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
        hydra = float(df.iloc[30, 1])      
        note_pate = float(df.iloc[30, 5])   
        note_aspect = float(df.iloc[33, 5]) 
        volume_val = float(df.iloc[33, 1])  
        note_totale = float(df.iloc[35, 5]) 

        # --- PARAMÈTRES TECHNIQUES ---
        lis = ex_label("Lissage")
        col_p, con_p, ext_p, ela_p, rel_p = ex_label("Collant de la pâte"), ex_label("Consistance"), ex_label("Extensibilité"), ex_label("Elasticité"), ex_label("Relâchement")
        col_f, con_f, ext_f, ela_f = ex_score(20), ex_score(19), ex_score(21), ex_score(23)
        t1, t2 = ex_score(30), ex_score(31)
        sec_v, col_v = ex_score(33), ex_score(34) 
        dev_v, reg_v, dec_v = ex_score(37), ex_score(38), ex_score(39) 

        # --- RÉDACTION ---
        
        # 1. Hydratation & Lissage
        h_lim = 63 if type_p == "Blé de force" else 61
        h_txt = "Bonne hydratation" if hydra >= h_lim else "Assez bonne hydratation" if hydra >= (h_lim-2) else "Hydratation satisfaisante"
        l_txt = {10: "bon lissage", 7: "lissage un peu rapide", -7: "lissage un peu lent"}.get(lis, "lissage correct")

        # 2. Pâte (Pétrissage & Façonnage)
        def format_list(lst):
            return ", ".join(lst[:-1]) + " et " + lst[-1] if len(lst) > 1 else (lst[0] if lst else "équilibrée")

        def get_details(c, co, ex, el):
            d = []
            if c in [7, 4]: d.append("collante" if c==7 else "très collante")
            if co != 10: d.append(f"en {desc_defaut(co)} de consistance")
            if ex != 10: d.append(f"en {desc_defaut(ex)} d'extensibilité")
            if el != 10: d.append(f"en {desc_defaut(el)} d'élasticité")
            return d

        p_list = get_details(col_p, con_p, ext_p, ela_p)
        f_list = get_details(col_f, con_f, ext_f, ela_f)
        rel_msg = " et relâchante après détente" if rel_p == 7 else ""
        
        if (ext_f == ext_p and ela_f == ela_p and col_f == col_p and con_f == con_p):
            comportement_txt = f"Pâte {format_list(p_list)}{rel_msg} gardant le même profil tout au long du processus."
        else:
            comportement_txt = f"En fin de pétrissage, pâte {format_list(p_list)}. Au façonnage, pâte {format_list(f_list)}{rel_msg}."

        # Tenue
        def desc_t(score): return {-7: "manque de tenue", -4: "manque important de tenue"}.get(score, "bonne tenue")
        t_txt = f" {desc_t(t1).capitalize()} au premier enfournement et {desc_t(t2)} au second." if (t1 != 10 or t2 != 10) else " Bonne tenue aux deux enfournements."

        # 3. Aspect & Grigne
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
        if dec_v in [7, 4]: suite_aspect.append("un déchirement du coup de lame")
        
        final_aspect = a_base
        if suite_aspect:
            final_aspect += " avec " + format_list(suite_aspect)
        
        # 4. Coloration (Simplifiée)
        color_txt = f" {desc_defaut(col_v).capitalize()} de coloration de la croûte." if col_v != 10 else ""

        # 5. Volume
        if type_p == "Farine corrigée":
            v_lib = "Très bon volume" if volume_val > 2000 else "Bon volume" if volume_val > 1900 else "Assez bon volume"
        else:
            v_lib = "Bon volume" if volume_val > 1600 else "Assez bon volume" if volume_val > 1500 else "Volume satisfaisant"

        # --- AFFICHAGE ---
        st.divider()
        # Structure : Aspect. Coloration (si existe). Volume.
        resultat_final = f"{h_txt}, {l_txt}. {comportement_txt}{t_txt}\n\n{final_aspect}.{color_txt} {v_lib}."
        
        st.success(resultat_final)
        
        st.info(f"**Données :** Note Totale: **{note_totale}** | Pâte: **{note_pate}** | Aspect: **{note_aspect}** | Volume: **{volume_val}** | Hydra: **{hydra}%**")

    except Exception as e:
        st.error(f"Erreur : {e}")

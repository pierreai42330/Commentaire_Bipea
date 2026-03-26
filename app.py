import streamlit as st
import pandas as pd
import io

# Configuration de l'onglet du navigateur
st.set_page_config(page_title="Générateur BIPÉA Marion", page_icon="🍞")

st.title("🍞 Générateur de Commentaires Marion")
st.write("Analyse automatique des essais de panification BIPÉA.")

# 1. Barre latérale de configuration
st.sidebar.header("Configuration")
type_p = st.sidebar.selectbox(
    "Type de produit :",
    ["Blé BPMF", "Blé de force", "Farine de base", "Farine corrigée"]
)

# 2. Zone de chargement du fichier
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

        # Extraction des données numériques
        hydra = float(df.iloc[30, 1])      # B31
        note_pate = float(df.iloc[30, 5])   # F31
        note_aspect = float(df.iloc[33, 5]) # F34
        volume_val = float(df.iloc[33, 1])  # B34
        note_totale = float(df.iloc[35, 5]) # F36

        # Données techniques pour la rédaction
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

        # --- RÉDACTION (Logique V20) ---
        # 1. Hydratation
        if type_p == "Blé de force":
            h_txt = "Bonne hydratation" if hydra >= 63 else "Assez bonne hydratation" if hydra >= 61 else "Hydratation satisfaisante" if hydra >= 60 else "Hydratation un peu faible"
        else:
            h_txt = "Bonne hydratation" if hydra >= 61 else "Assez bonne hydratation" if hydra >= 60 else "Hydratation satisfaisante" if hydra >= 58 else "Hydratation un peu faible"
        
        l_txt = {10: "bon lissage", 7: "lissage un peu rapide", -7: "lissage un peu lent"}.get(lis, "lissage correct")

        # 2. Pétrissage / Façonnage / Tenue
        p_details = []
        if col_p in [7, 4]: p_details.append("pâte collante")
        if con_p != 10: p_details.append(f"pâte en {desc_defaut(con_p)} de consistance")
        p_txt = "En fin de pétrissage, " + ("pâte équilibrée." if not p_details else p_details[0] + ".")
        
        def desc_t(score): return {-7: "manque de tenue", -4: "manque important de tenue"}.get(score, "bonne tenue")
        t_txt = "Bonne tenue aux deux enfournements." if (t1 == 10 and t2 == 10) else f"{desc_t(t1).capitalize()} au premier enfournement et {desc_t(t2)} au second."

        # 3. Aspect
        if note_aspect > 65: a_base = "Très bel aspect du pain"
        elif note_aspect > 60: a_base = "Bel aspect du pain"
        elif note_aspect > 50: a_base = "Assez bel aspect du pain"
        else: a_base = "Aspect correct du pain"

        suite_aspect = []
        if sec_v != 10: suite_aspect.append(f"un {desc_defaut(sec_v)} de section")
        gr_el = []
        if dev_v != 10: gr_el.append(f"{desc_defaut(dev_v)} de développement")
        if reg_v != 10: gr_el.append(f"{desc_defaut(reg_v)} de régularité")
        if gr_el: suite_aspect.append(f"un {' et '.join(gr_el)} du coup de lame")
        if dec_v in [7, 4]: suite_aspect.append("un déchirement du coup de lame")

        final_aspect = a_base
        if suite_aspect:
            final_aspect += " avec " + ", ".join(suite_aspect)
        
        # 4. Volume
        if type_p == "Farine corrigée":
            v_lib = "Très bon volume" if volume_val > 2000 else "Bon volume" if volume_val > 1900 else "Assez bon volume"
        elif type_p == "Blé de force":
            v_lib = "Bon volume" if volume_val > 1800 else "Assez bon volume" if volume_val > 1700 else "Volume satisfaisant"
        else:
            v_lib = "Bon volume" if volume_val > 1600 else "Assez bon volume" if volume_val > 1500 else "Volume satisfaisant"

        # --- AFFICHAGE ---
        st.divider()
        st.subheader("📝 Commentaire généré")
        
        commentaire_final = f"{h_txt}, {l_txt}. {p_txt} {t_txt}\n\n{final_aspect}. {v_lib}."
        st.success(commentaire_final)
        
        # Bouton pour copier le texte
        st.button("Copier le texte", on_click=lambda: st.write("Texte copié ! (Simulé)"))

        st.subheader("📊 Informations chiffrées")
        col1, col2, col3 = st.columns(3)
        col1.metric("Note Totale", f"{note_totale}/300")
        col2.metric("Volume", f"{volume_val} cm³")
        col3.metric("Hydratation", f"{hydra}%")

    except Exception as e:
        st.error(f"Erreur d'analyse : {e}. Vérifiez que le fichier Excel est au bon format.")

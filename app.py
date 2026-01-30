# app.py - Dimensionnement Palettes/Conteneur
import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Dimensionnement", layout="wide")
st.title("📦 Dimensionnement Palettes/Conteneur")

# Sidebar
with st.sidebar:
    st.header("🚢 Conteneur")
    cont_l = st.number_input("Longueur (cm)", 589)
    cont_w = st.number_input("Largeur (cm)", 235)
    cont_h = st.number_input("Hauteur (cm)", 239)
    
    st.header("📦 Palette")
    pal_l = st.number_input("Long. palette (cm)", 120)
    pal_w = st.number_input("Larg. palette (cm)", 80)
    pal_h = st.number_input("Haut. palette (cm)", 15)
    
    margin = st.slider("Marge (cm)", 0, 20, 5)
    
    if st.button("🚀 Calculer", type="primary"):
        # Calcul
        n_l = int((cont_l - margin*2) / pal_l)
        n_w = int((cont_w - margin*2) / pal_w)
        n_h = int(cont_h / pal_h)
        
        total = n_l * n_w * n_h
        st.session_state.result = {
            'total': total,
            'layout': f"{n_l} × {n_w} × {n_h}",
            'utilization': (n_l*pal_l * n_w*pal_w * n_h*pal_h) / (cont_l*cont_w*cont_h) * 100
        }

# Afficher résultat
if 'result' in st.session_state:
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total", f"{st.session_state.result['total']}")
    col2.metric("📐 Disposition", st.session_state.result['layout'])
    col3.metric("📈 Utilisation", f"{st.session_state.result['utilization']:.1f}%")
    
    # Export
    df = pd.DataFrame([{
        'Date': pd.Timestamp.now(),
        'Conteneur': f"{cont_l}x{cont_w}x{cont_h}",
        'Palette': f"{pal_l}x{pal_w}x{pal_h}",
        'Total_Palettes': st.session_state.result['total'],
        'Utilisation_%': st.session_state.result['utilization']
    }])
    
    csv = df.to_csv(index=False)
    st.download_button("📥 Télécharger CSV", csv, "resultat.csv", "text/csv")

st.info("Configurez les paramètres dans la barre latérale et cliquez sur Calculer")
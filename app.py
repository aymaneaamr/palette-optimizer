import streamlit as st
import pandas as pd
import numpy as np
from itertools import product

st.set_page_config(
    page_title="Palette Optimizer",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Palette Optimizer")
st.markdown("### Optimisez le chargement de vos palettes et conteneurs")

with st.sidebar:
    st.header("Paramètres d'entrée")
    
    st.subheader("Dimensions de la palette/conteneur")
    pal_length = st.number_input("Longueur (cm)", min_value=1, value=120)
    pal_width = st.number_input("Largeur (cm)", min_value=1, value=80)
    pal_height = st.number_input("Hauteur (cm)", min_value=1, value=150)
    
    st.subheader("Dimensions du colis")
    box_length = st.number_input("Longueur colis (cm)", min_value=1, value=30)
    box_width = st.number_input("Largeur colis (cm)", min_value=1, value=20)
    box_height = st.number_input("Hauteur colis (cm)", min_value=1, value=15)
    
    st.subheader("Options de chargement")
    allow_rotation = st.checkbox("Permettre la rotation des colis", value=True)
    max_weight = st.number_input("Poids max palette (kg)", min_value=0.0, value=1000.0, step=50.0)
    box_weight = st.number_input("Poids par colis (kg)", min_value=0.1, value=5.0, step=0.5)

# Fonction d'optimisation
def optimize_packing(pal_dims, box_dims, allow_rotation=True):
    """Calcule le nombre maximum de colis pouvant tenir sur une palette"""
    pal_l, pal_w, pal_h = pal_dims
    box_l, box_w, box_h = box_dims
    
    orientations = []
    if allow_rotation:
        # Générer toutes les orientations possibles
        orientations = [
            (box_l, box_w, box_h),
            (box_l, box_h, box_w),
            (box_w, box_l, box_h),
            (box_w, box_h, box_l),
            (box_h, box_l, box_w),
            (box_h, box_w, box_l)
        ]
        # Supprimer les doublons
        orientations = list(set(orientations))
    else:
        orientations = [(box_l, box_w, box_h)]
    
    best_count = 0
    best_orientation = None
    best_arrangement = None
    
    for l, w, h in orientations:
        # Nombre de colis dans chaque dimension
        count_x = pal_l // l
        count_y = pal_w // w
        count_z = pal_h // h
        
        total_count = count_x * count_y * count_z
        
        if total_count > best_count:
            best_count = total_count
            best_orientation = (l, w, h)
            best_arrangement = (count_x, count_y, count_z)
    
    return best_count, best_orientation, best_arrangement

# Fonction pour calculer les statistiques
def calculate_stats(pal_dims, box_dims, box_count, box_weight):
    pal_l, pal_w, pal_h = pal_dims
    box_l, box_w, box_h = box_dims
    
    # Volume
    pal_volume = pal_l * pal_w * pal_h / 1000000  # en m³
    box_volume = box_l * box_w * box_h / 1000000  # en m³
    total_volume = box_count * box_volume
    
    # Poids
    total_weight = box_count * box_weight
    
    # Occupation
    volume_occupation = (total_volume / pal_volume) * 100 if pal_volume > 0 else 0
    
    return {
        'pal_volume_m3': pal_volume,
        'box_volume_m3': box_volume,
        'total_volume_m3': total_volume,
        'total_weight_kg': total_weight,
        'volume_occupation_percent': volume_occupation
    }

# Interface principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Résultats d'optimisation")
    
    if st.button("Lancer l'optimisation", type="primary"):
        pal_dims = (pal_length, pal_width, pal_height)
        box_dims = (box_length, box_width, box_height)
        
        best_count, best_orientation, best_arrangement = optimize_packing(
            pal_dims, box_dims, allow_rotation
        )
        
        stats = calculate_stats(pal_dims, best_orientation, best_count, box_weight)
        
        # Vérification du poids
        weight_warning = ""
        if stats['total_weight_kg'] > max_weight:
            weight_warning = "⚠️ **DÉPASSEMENT DE POIDS MAXIMAL**"
            max_boxes_by_weight = int(max_weight // box_weight)
            if max_boxes_by_weight < best_count:
                best_count = max_boxes_by_weight
                stats = calculate_stats(pal_dims, best_orientation, best_count, box_weight)
                weight_warning += f" - Limité à {best_count} colis pour respecter le poids max"
        
        st.success(f"**Résultat optimal : {best_count} colis**")
        
        if weight_warning:
            st.warning(weight_warning)
        
        st.subheader("Configuration recommandée")
        st.write(f"**Orientation des colis :** {best_orientation[0]} × {best_orientation[1]} × {best_orientation[2]} cm")
        st.write(f"**Arrangement :** {best_arrangement[0]} × {best_arrangement[1]} × {best_arrangement[2]} colis")
        
        st.subheader("Statistiques")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.metric("Volume palette", f"{stats['pal_volume_m3']:.3f} m³")
            st.metric("Volume total colis", f"{stats['total_volume_m3']:.3f} m³")
        
        with stats_col2:
            st.metric("Poids total", f"{stats['total_weight_kg']:.1f} kg")
            st.metric("Poids max", f"{max_weight:.1f} kg")
        
        with stats_col3:
            st.metric("Taux d'occupation", f"{stats['volume_occupation_percent']:.1f}%")
            st.metric("Volume par colis", f"{stats['box_volume_m3']:.3f} m³")
        
        # Visualisation
        st.subheader("Visualisation de l'arrangement")
        
        # Création d'un graphique simple
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Palette
        fig.add_trace(go.Mesh3d(
            x=[0, pal_length, pal_length, 0, 0, pal_length, pal_length, 0],
            y=[0, 0, pal_width, pal_width, 0, 0, pal_width, pal_width],
            z=[0, 0, 0, 0, pal_height, pal_height, pal_height, pal_height],
            i=[0, 0, 0, 2],
            j=[1, 2, 3, 3],
            k=[2, 3, 7, 6],
            opacity=0.1,
            color='lightgray',
            name='Palette'
        ))
        
        # Colis (simplifié - un seul colis représentatif)
        if best_count > 0:
            fig.add_trace(go.Mesh3d(
                x=[0, best_orientation[0], best_orientation[0], 0],
                y=[0, 0, best_orientation[1], best_orientation[1]],
                z=[0, 0, 0, 0],
                i=[0, 0],
                j=[1, 2],
                k=[2, 3],
                opacity=0.7,
                color='blue',
                name='Colis'
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Longueur (cm)',
                yaxis_title='Largeur (cm)',
                zaxis_title='Hauteur (cm)'
            ),
            width=800,
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("Informations")
    st.info("""
    **Comment utiliser :**
    1. Définissez les dimensions de votre palette/conteneur
    2. Spécifiez les dimensions de vos colis
    3. Ajustez les options de chargement
    4. Cliquez sur "Lancer l'optimisation"
    
    **Conseils :**
    - Activez la rotation pour de meilleurs résultats
    - Considérez le poids maximal autorisé
    - L'outil optimise pour le nombre maximal de colis
    """)
    
    st.header("Export des résultats")
    st.download_button(
        label="Télécharger le rapport",
        data=f"""
        Rapport d'optimisation - Palette Optimizer
        
        Dimensions palette : {pal_length} × {pal_width} × {pal_height} cm
        Dimensions colis : {box_length} × {box_width} × {box_height} cm
        Rotation autorisée : {'Oui' if allow_rotation else 'Non'}
        Poids max palette : {max_weight} kg
        Poids par colis : {box_weight} kg
        
        Résultat optimal : {best_count if 'best_count' in locals() else 'N/A'} colis
        Orientation recommandée : {best_orientation if 'best_orientation' in locals() else 'N/A'}
        Arrangement : {best_arrangement if 'best_arrangement' in locals() else 'N/A'}
        
        Volume palette : {stats['pal_volume_m3'] if 'stats' in locals() else 'N/A'} m³
        Volume occupé : {stats['total_volume_m3'] if 'stats' in locals() else 'N/A'} m³
        Taux d'occupation : {stats['volume_occupation_percent'] if 'stats' in locals() else 'N/A'}%
        Poids total : {stats['total_weight_kg'] if 'stats' in locals() else 'N/A'} kg
        """,
        file_name="rapport_optimisation_palette.txt",
        mime="text/plain"
    )

# Pied de page
st.divider()
st.caption("📦 Palette Optimizer v1.0 | Outil de dimensionnement de palettes et conteneurs")# app.py - Dimensionnement 

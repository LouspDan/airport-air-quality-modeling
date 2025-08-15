#!/usr/bin/env python3
"""
Dashboard Exécutif - Aéroport Paris-Val d'Europe
Tableau de bord dirigeant pour suivi performance environnementale
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from sqlalchemy import create_engine
import datetime as dt
import numpy as np

# Configuration page Streamlit
st.set_page_config(
    page_title="Dashboard Exécutif - Paris-Val d'Europe",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration base de données
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'airport_air_quality',
    'user': 'airport_user',
    'password': 'airport_password'
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

@st.cache_data(ttl=300)  # Cache 5 minutes
def load_data():
    """Charger les données depuis PostgreSQL avec cache"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Requête principale pour KPIs
        query_kpis = """
        SELECT 
            COUNT(DISTINCT f.flight_id) as total_flights,
            COUNT(DISTINCT f.aircraft_type) as aircraft_types,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as total_co2_kg,
            ROUND(AVG(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE NULL END)::numeric, 2) as avg_co2_per_flight
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        """
        
        kpis = pd.read_sql_query(query_kpis, engine)
        
        # Données temporelles
        query_temporal = """
        SELECT 
            DATE(f.departure_time) as flight_date,
            COUNT(DISTINCT f.flight_id) as daily_flights,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as daily_co2_kg
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        GROUP BY DATE(f.departure_time)
        ORDER BY flight_date
        """
        
        temporal_data = pd.read_sql_query(query_temporal, engine)
        
        # Données par type d'avion
        query_aircraft = """
        SELECT 
            f.aircraft_type,
            COUNT(DISTINCT f.flight_id) as flights_count,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as total_co2_kg,
            ROUND(AVG(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE NULL END)::numeric, 2) as avg_co2_per_flight
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        GROUP BY f.aircraft_type
        ORDER BY total_co2_kg DESC
        """
        
        aircraft_data = pd.read_sql_query(query_aircraft, engine)
        
        # Répartition des polluants
        query_pollutants = """
        SELECT 
            e.pollutant_type,
            ROUND(SUM(e.emission_quantity_kg)::numeric, 2) as total_emission_kg,
            COUNT(*) as calculations_count
        FROM etl.emissions_staging e
        GROUP BY e.pollutant_type
        ORDER BY total_emission_kg DESC
        """
        
        pollutants_data = pd.read_sql_query(query_pollutants, engine)
        
        return kpis, temporal_data, aircraft_data, pollutants_data
        
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return None, None, None, None

def create_kpi_cards(kpis):
    """Créer les cartes KPI"""
    if kpis is None or kpis.empty:
        st.error("Pas de données KPI disponibles")
        return
    
    row = kpis.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="✈️ Total Vols",
            value=f"{row['total_flights']:,}",
            delta="30 derniers jours"
        )
    
    with col2:
        co2_tonnes = row['total_co2_kg'] / 1000
        st.metric(
            label="💨 Émissions CO2",
            value=f"{co2_tonnes:,.1f} tonnes",
            delta=f"{row['total_co2_kg']:,.0f} kg"
        )
    
    with col3:
        st.metric(
            label="🛩️ Types d'Avions",
            value=f"{row['aircraft_types']}",
            delta="Flotte active"
        )
    
    with col4:
        avg_tonnes = row['avg_co2_per_flight'] / 1000
        st.metric(
            label="📊 Moyenne CO2/Vol",
            value=f"{avg_tonnes:.2f} tonnes",
            delta=f"{row['avg_co2_per_flight']:,.0f} kg"
        )

def create_temporal_chart(temporal_data):
    """Graphique d'évolution temporelle"""
    if temporal_data is None or temporal_data.empty:
        st.error("Pas de données temporelles")
        return
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Évolution des Vols', 'Évolution des Émissions CO2'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Graphique des vols
    fig.add_trace(
        go.Scatter(
            x=temporal_data['flight_date'],
            y=temporal_data['daily_flights'],
            mode='lines+markers',
            name='Vols/jour',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Graphique des émissions
    fig.add_trace(
        go.Scatter(
            x=temporal_data['flight_date'],
            y=temporal_data['daily_co2_kg'],
            mode='lines+markers',
            name='CO2 kg/jour',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.1)'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="📈 Évolution Temporelle - Paris-Val d'Europe",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Nombre de vols", row=1, col=1)
    fig.update_yaxes(title_text="CO2 (kg)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

def create_aircraft_ranking(aircraft_data):
    """Classement des types d'avions"""
    if aircraft_data is None or aircraft_data.empty:
        st.error("Pas de données avions")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Émetteurs CO2 (Total)")
        
        fig_total = px.bar(
            aircraft_data.head(6),
            x='aircraft_type',
            y='total_co2_kg',
            title="Émissions CO2 Totales par Type d'Avion",
            labels={'total_co2_kg': 'CO2 (kg)', 'aircraft_type': 'Type d\'Avion'},
            color='total_co2_kg',
            color_continuous_scale='Reds'
        )
        
        fig_total.update_layout(height=400)
        st.plotly_chart(fig_total, use_container_width=True)
    
    with col2:
        st.subheader("📊 Émissions Moyennes par Vol")
        
        fig_avg = px.bar(
            aircraft_data.sort_values('avg_co2_per_flight', ascending=False).head(6),
            x='aircraft_type',
            y='avg_co2_per_flight',
            title="CO2 Moyen par Vol et par Type",
            labels={'avg_co2_per_flight': 'CO2 Moyen (kg/vol)', 'aircraft_type': 'Type d\'Avion'},
            color='avg_co2_per_flight',
            color_continuous_scale='Blues'
        )
        
        fig_avg.update_layout(height=400)
        st.plotly_chart(fig_avg, use_container_width=True)

def create_pollutants_distribution(pollutants_data):
    """Distribution des polluants"""
    if pollutants_data is None or pollutants_data.empty:
        st.error("Pas de données polluants")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en secteurs
        fig_pie = px.pie(
            pollutants_data,
            values='total_emission_kg',
            names='pollutant_type',
            title="🌍 Répartition des Émissions par Polluant",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Tableau détaillé
        st.subheader("📋 Détail des Émissions")
        
        # Formater les données pour affichage
        display_data = pollutants_data.copy()
        display_data['total_emission_tonnes'] = display_data['total_emission_kg'] / 1000
        display_data = display_data.round(2)
        
        st.dataframe(
            display_data[['pollutant_type', 'total_emission_tonnes', 'calculations_count']].rename(columns={
                'pollutant_type': 'Polluant',
                'total_emission_tonnes': 'Total (tonnes)',
                'calculations_count': 'Calculs'
            }),
            use_container_width=True,
            height=400
        )

def main():
    """Interface principale du dashboard"""
    
    # En-tête
    st.title("✈️ Dashboard Exécutif")
    st.markdown("### 🌍 Aéroport Paris-Val d'Europe - Performance Environnementale")
    
    # Sidebar avec informations
    with st.sidebar:
        st.markdown("### ℹ️ Informations")
        st.markdown("""
        **Période d'analyse :** 30 derniers jours  
        **Méthodologie :** Calculs ICAO  
        **Polluants surveillés :** CO2, NOx, PM10, PM2.5, SOx  
        **Source :** Pipeline ETL temps réel
        """)
        
        st.markdown("### 🎯 Objectifs Environnementaux")
        st.markdown("""
        - **Réduction CO2 :** -5% vs année précédente
        - **Optimisation trajets :** +10% efficacité carburant  
        - **Avions propres :** 70% flotte nouvelle génération
        """)
    
    # Indicateur de mise à jour
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("---")
    with col2:
        st.caption(f"🔄 Dernière mise à jour: {dt.datetime.now().strftime('%H:%M:%S')}")
    
    # Chargement des données
    with st.spinner("📊 Chargement des données..."):
        kpis, temporal_data, aircraft_data, pollutants_data = load_data()
    
    if kpis is None:
        st.error("❌ Impossible de charger les données. Vérifiez la connexion à la base.")
        st.stop()
    
    # Section KPIs
    st.markdown("## 📊 Indicateurs Clés")
    create_kpi_cards(kpis)
    
    st.markdown("---")
    
    # Section évolution temporelle
    st.markdown("## 📈 Tendances Temporelles")
    create_temporal_chart(temporal_data)
    
    st.markdown("---")
    
    # Section analyses par avion
    st.markdown("## ✈️ Analyse par Type d'Aéronef")
    create_aircraft_ranking(aircraft_data)
    
    st.markdown("---")
    
    # Section polluants
    st.markdown("## 🌍 Impact Environnemental")
    create_pollutants_distribution(pollutants_data)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center'>
        <small>
        🌍 <strong>Paris-Val d'Europe Airport</strong> - Dashboard Exécutif<br>
        Système de Modélisation Qualité de l'Air • Pipeline ETL ICAO
        </small>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
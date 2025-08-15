#!/usr/bin/env python3
"""
Dashboard Opérationnel - Aéroport Paris-Val d'Europe
Interface terrain avancée pour managers d'exploitation et équipes techniques
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
from datetime import timedelta
import io

# Configuration page
st.set_page_config(
    page_title="Dashboard Opérationnel - Paris-Val d'Europe",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Initialisation du state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = dt.datetime.now()

@st.cache_data(ttl=60)  # Cache plus court pour données opérationnelles
def load_operational_data(date_filter, aircraft_filter, phase_filter):
    """Charger données opérationnelles avec filtres"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Construction des filtres dynamiques
        where_conditions = ["1=1"]  # Condition toujours vraie pour commencer
        
        if date_filter and len(date_filter) == 2:
            where_conditions.append(f"DATE(f.departure_time) BETWEEN '{date_filter[0]}' AND '{date_filter[1]}'")
        
        if aircraft_filter and len(aircraft_filter) > 0:
            aircraft_list = "','".join(aircraft_filter)
            where_conditions.append(f"f.aircraft_type IN ('{aircraft_list}')")
        
        if phase_filter and len(phase_filter) > 0:
            phase_list = "','".join(phase_filter)
            where_conditions.append(f"e.flight_phase IN ('{phase_list}')")
        
        where_clause = " AND ".join(where_conditions)
        
        # Requête détaillée par vol et phase
        query_details = f"""
        SELECT 
            f.flight_id,
            f.aircraft_type,
            f.departure_airport,
            f.arrival_airport,
            f.departure_time,
            f.flight_duration_minutes,
            f.passengers,
            e.flight_phase,
            e.pollutant_type,
            e.fuel_consumed_kg,
            e.emission_quantity_kg,
            e.calculation_method
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        WHERE {where_clause}
        ORDER BY f.departure_time DESC, e.flight_phase, e.pollutant_type
        """
        
        details = pd.read_sql_query(query_details, engine)
        
        # Métriques temps réel (dernières 24h)
        query_realtime = """
        SELECT 
            DATE_TRUNC('hour', f.departure_time) as hour_period,
            COUNT(DISTINCT f.flight_id) as hourly_flights,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as hourly_co2_kg,
            ROUND(AVG(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE NULL END)::numeric, 2) as avg_co2_per_flight
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        WHERE f.departure_time >= NOW() - INTERVAL '24 hours'
        GROUP BY DATE_TRUNC('hour', f.departure_time)
        ORDER BY hour_period DESC
        """
        
        realtime = pd.read_sql_query(query_realtime, engine)
        
        # Top vols émetteurs actuels
        query_top_flights = f"""
        SELECT 
            f.flight_id,
            f.aircraft_type,
            f.departure_time,
            f.passengers,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as total_co2_kg,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'NOx' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 4) as total_nox_kg
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        WHERE {where_clause}
        GROUP BY f.flight_id, f.aircraft_type, f.departure_time, f.passengers
        ORDER BY total_co2_kg DESC
        LIMIT 20
        """
        
        top_flights = pd.read_sql_query(query_top_flights, engine)
        
        # Analyse par phase de vol
        query_phases = f"""
        SELECT 
            e.flight_phase,
            COUNT(*) as phase_calculations,
            ROUND(AVG(e.fuel_consumed_kg)::numeric, 2) as avg_fuel_kg,
            ROUND(SUM(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE 0 END)::numeric, 2) as phase_co2_kg,
            ROUND(AVG(CASE WHEN e.pollutant_type = 'CO2' THEN e.emission_quantity_kg ELSE NULL END)::numeric, 2) as avg_co2_kg
        FROM etl.flights_staging f
        JOIN etl.emissions_staging e ON f.flight_id = e.flight_id
        WHERE {where_clause}
        GROUP BY e.flight_phase
        ORDER BY phase_co2_kg DESC
        """
        
        phases = pd.read_sql_query(query_phases, engine)
        
        return details, realtime, top_flights, phases
        
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return None, None, None, None

def create_control_panel():
    """Panel de contrôle avancé dans la sidebar"""
    
    st.sidebar.title("🎛️ Contrôles Opérationnels")
    
    # Auto-refresh
    st.sidebar.markdown("### ⚡ Actualisation")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    if st.sidebar.button("🔄 Actualiser maintenant"):
        st.cache_data.clear()
        st.session_state.last_refresh = dt.datetime.now()
        st.rerun()
    
    st.sidebar.caption(f"Dernière MàJ: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Filtres temporels
    st.sidebar.markdown("### 📅 Période d'Analyse")
    
    today = dt.date.today()
    
    period_options = {
        "Dernières 24h": (today - timedelta(days=1), today),
        "Derniers 7 jours": (today - timedelta(days=7), today),
        "Derniers 30 jours": (today - timedelta(days=30), today),
        "Personnalisé": None
    }
    
    period_choice = st.sidebar.selectbox(
        "Période prédéfinie",
        list(period_options.keys()),
        index=2  # Défaut: 30 jours
    )
    
    if period_choice == "Personnalisé":
        date_filter = st.sidebar.date_input(
            "Sélectionner période",
            value=(today - timedelta(days=7), today),
            max_value=today
        )
    else:
        date_filter = period_options[period_choice]
    
    # Filtres avions
    st.sidebar.markdown("### ✈️ Types d'Aéronefs")
    
    available_aircraft = ['A320', 'A321', 'A330', 'B737', 'B777', 'B787']
    aircraft_filter = st.sidebar.multiselect(
        "Sélectionner types",
        available_aircraft,
        default=available_aircraft  # Tous sélectionnés par défaut
    )
    
    # Filtres phases de vol
    st.sidebar.markdown("### 🛫 Phases de Vol")
    
    available_phases = ['taxi_out', 'takeoff', 'climb', 'cruise', 'descent', 'approach', 'taxi_in']
    phase_filter = st.sidebar.multiselect(
        "Sélectionner phases",
        available_phases,
        default=available_phases  # Toutes sélectionnées par défaut
    )
    
    # Options d'affichage
    st.sidebar.markdown("### 🎨 Options d'Affichage")
    
    show_details = st.sidebar.checkbox("Tables détaillées", value=True)
    show_alerts = st.sidebar.checkbox("Alertes seuils", value=True)
    
    # Seuils d'alerte
    if show_alerts:
        st.sidebar.markdown("#### 🚨 Seuils d'Alerte")
        co2_threshold = st.sidebar.number_input(
            "CO2 max par vol (kg)",
            min_value=1000,
            max_value=50000,
            value=25000,
            step=1000
        )
    else:
        co2_threshold = None
    
    return date_filter, aircraft_filter, phase_filter, show_details, show_alerts, co2_threshold

def create_realtime_metrics(realtime_data, co2_threshold=None):
    """Métriques temps réel avec alertes"""
    
    st.markdown("## ⚡ Monitoring Temps Réel (24h)")
    
    if realtime_data is None or realtime_data.empty:
        st.warning("Pas de données temps réel disponibles")
        return
    
    # Métriques dernière heure
    latest_hour = realtime_data.iloc[0] if not realtime_data.empty else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if latest_hour is not None:
            flights_delta = "Dernière heure"
            st.metric(
                "🛫 Vols/Heure",
                value=int(latest_hour['hourly_flights']),
                delta=flights_delta
            )
        
    with col2:
        if latest_hour is not None:
            co2_value = latest_hour['hourly_co2_kg']
            co2_color = "🔴" if co2_threshold and co2_value > co2_threshold else "🟢"
            st.metric(
                f"{co2_color} CO2 Horaire",
                value=f"{co2_value:,.0f} kg",
                delta=f"{co2_value/1000:.1f} tonnes"
            )
    
    with col3:
        if latest_hour is not None:
            avg_co2 = latest_hour['avg_co2_per_flight']
            st.metric(
                "📊 CO2 Moyen/Vol",
                value=f"{avg_co2:,.0f} kg",
                delta="Dernière heure"
            )
    
    with col4:
        # Performance vs période précédente
        if len(realtime_data) > 1:
            current_total = realtime_data['hourly_co2_kg'].sum()
            previous_period = realtime_data.tail(12)['hourly_co2_kg'].sum()  # 12h précédentes
            delta_pct = ((current_total - previous_period) / previous_period * 100) if previous_period > 0 else 0
            delta_sign = "+" if delta_pct > 0 else ""
            
            st.metric(
                "📈 Évolution 12h",
                value=f"{current_total/1000:.1f}t",
                delta=f"{delta_sign}{delta_pct:.1f}%"
            )
    
    # Graphique temps réel
    if not realtime_data.empty:
        fig_realtime = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Vols par Heure', 'Émissions CO2 par Heure'),
            vertical_spacing=0.1
        )
        
        # Graphique vols
        fig_realtime.add_trace(
            go.Scatter(
                x=realtime_data['hour_period'],
                y=realtime_data['hourly_flights'],
                mode='lines+markers',
                name='Vols/h',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Graphique CO2 avec zone d'alerte
        fig_realtime.add_trace(
            go.Scatter(
                x=realtime_data['hour_period'],
                y=realtime_data['hourly_co2_kg'],
                mode='lines+markers',
                name='CO2 kg/h',
                line=dict(color='#A23B72', width=3),
                marker=dict(size=8),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        # Ligne de seuil si définie
        if co2_threshold:
            fig_realtime.add_hline(
                y=co2_threshold,
                line_dash="dash",
                line_color="red",
                annotation_text="Seuil d'alerte",
                row=2, col=1
            )
        
        fig_realtime.update_layout(
            title="📊 Évolution Temps Réel - Dernières 24h",
            height=400,
            showlegend=False
        )
        
        fig_realtime.update_xaxes(title_text="Heure", row=2, col=1)
        fig_realtime.update_yaxes(title_text="Vols", row=1, col=1)
        fig_realtime.update_yaxes(title_text="CO2 (kg)", row=2, col=1)
        
        st.plotly_chart(fig_realtime, use_container_width=True)

def create_flight_analysis(top_flights, phases_data):
    """Analyse détaillée des vols et phases"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 10 Vols Émetteurs")
        
        if top_flights is not None and not top_flights.empty:
            # Graphique top vols
            fig_top = px.bar(
                top_flights.head(10),
                x='flight_id',
                y='total_co2_kg',
                color='aircraft_type',
                title="Émissions CO2 par Vol",
                labels={'total_co2_kg': 'CO2 (kg)', 'flight_id': 'Vol'},
                hover_data=['passengers', 'total_nox_kg']
            )
            
            fig_top.update_layout(height=400)
            fig_top.update_xaxes(tickangle=45)
            st.plotly_chart(fig_top, use_container_width=True)
        
    with col2:
        st.markdown("### 🛫 Analyse par Phase de Vol")
        
        if phases_data is not None and not phases_data.empty:
            # Graphique phases
            fig_phases = px.bar(
                phases_data,
                x='flight_phase',
                y='phase_co2_kg',
                color='avg_fuel_kg',
                title="Émissions CO2 par Phase",
                labels={'phase_co2_kg': 'CO2 Total (kg)', 'flight_phase': 'Phase'},
                color_continuous_scale='Viridis'
            )
            
            fig_phases.update_layout(height=400)
            fig_phases.update_xaxes(tickangle=45)
            st.plotly_chart(fig_phases, use_container_width=True)

def create_detailed_tables(details_data, top_flights, show_details):
    """Tables détaillées exploratoires"""
    
    if not show_details:
        return
    
    st.markdown("## 📋 Tables Exploratoires")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Détails Émissions", "🏆 Top Vols", "📊 Export Données"])
    
    with tab1:
        st.markdown("### 🔍 Détails par Vol et Phase")
        
        if details_data is not None and not details_data.empty:
            # Filtres supplémentaires pour la table
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pollutant_filter = st.selectbox(
                    "Polluant",
                    ['Tous'] + list(details_data['pollutant_type'].unique())
                )
            
            with col2:
                aircraft_table_filter = st.selectbox(
                    "Type d'avion",
                    ['Tous'] + list(details_data['aircraft_type'].unique())
                )
            
            with col3:
                max_rows = st.number_input(
                    "Lignes max",
                    min_value=10,
                    max_value=1000,
                    value=100,
                    step=10
                )
            
            # Application des filtres
            filtered_details = details_data.copy()
            
            if pollutant_filter != 'Tous':
                filtered_details = filtered_details[filtered_details['pollutant_type'] == pollutant_filter]
            
            if aircraft_table_filter != 'Tous':
                filtered_details = filtered_details[filtered_details['aircraft_type'] == aircraft_table_filter]
            
            # Affichage table avec formatting
            display_details = filtered_details.head(max_rows).copy()
            display_details['departure_time'] = pd.to_datetime(display_details['departure_time']).dt.strftime('%Y-%m-%d %H:%M')
            display_details['emission_quantity_kg'] = display_details['emission_quantity_kg'].round(4)
            display_details['fuel_consumed_kg'] = display_details['fuel_consumed_kg'].round(2)
            
            st.dataframe(
                display_details,
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Affichage de {len(display_details)} lignes sur {len(filtered_details)} disponibles")
    
    with tab2:
        st.markdown("### 🏆 Classement Vols Émetteurs")
        
        if top_flights is not None and not top_flights.empty:
            # Formatage pour affichage
            display_top = top_flights.copy()
            display_top['departure_time'] = pd.to_datetime(display_top['departure_time']).dt.strftime('%Y-%m-%d %H:%M')
            display_top['total_co2_kg'] = display_top['total_co2_kg'].round(2)
            display_top['total_nox_kg'] = display_top['total_nox_kg'].round(4)
            
            st.dataframe(
                display_top,
                use_container_width=True,
                height=400
            )
    
    with tab3:
        st.markdown("### 📊 Export des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Télécharger Détails (CSV)"):
                if details_data is not None and not details_data.empty:
                    csv = details_data.to_csv(index=False)
                    st.download_button(
                        label="💾 Détails Émissions.csv",
                        data=csv,
                        file_name=f"emissions_details_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("📥 Télécharger Top Vols (CSV)"):
                if top_flights is not None and not top_flights.empty:
                    csv = top_flights.to_csv(index=False)
                    st.download_button(
                        label="💾 Top Vols.csv",
                        data=csv,
                        file_name=f"top_flights_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

def main():
    """Interface principale dashboard opérationnel"""
    
    # En-tête
    st.title("🎛️ Dashboard Opérationnel")
    st.markdown("### 🔧 Aéroport Paris-Val d'Europe - Interface Terrain")
    
    # Panel de contrôle
    date_filter, aircraft_filter, phase_filter, show_details, show_alerts, co2_threshold = create_control_panel()
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        st.rerun()
    
    # Indicateur de filtres actifs
    active_filters = []
    if aircraft_filter and len(aircraft_filter) < 6:
        active_filters.append(f"Avions: {', '.join(aircraft_filter)}")
    if phase_filter and len(phase_filter) < 7:
        active_filters.append(f"Phases: {', '.join(phase_filter)}")
    if date_filter:
        active_filters.append(f"Période: {date_filter[0]} → {date_filter[1]}")
    
    if active_filters:
        st.info("🎯 Filtres actifs: " + " | ".join(active_filters))
    
    # Chargement des données
    with st.spinner("⚡ Chargement données opérationnelles..."):
        details, realtime, top_flights, phases = load_operational_data(date_filter, aircraft_filter, phase_filter)
    
    if details is None:
        st.error("❌ Impossible de charger les données opérationnelles")
        st.stop()
    
    # Métriques temps réel
    create_realtime_metrics(realtime, co2_threshold)
    
    st.markdown("---")
    
    # Analyse des vols
    st.markdown("## 📊 Analyse Opérationnelle")
    create_flight_analysis(top_flights, phases)
    
    st.markdown("---")
    
    # Tables détaillées
    create_detailed_tables(details, top_flights, show_details)
    
    # Footer avec statistiques
    st.markdown("---")
    
    if details is not None and not details.empty:
        total_records = len(details)
        unique_flights = details['flight_id'].nunique()
        date_range = f"{details['departure_time'].min().date()} → {details['departure_time'].max().date()}"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Enregistrements", f"{total_records:,}")
        with col2:
            st.metric("✈️ Vols Uniques", f"{unique_flights:,}")
        with col3:
            st.metric("📅 Période Analysée", date_range)
    
    # Info footer
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
    <small>
    🎛️ <strong>Dashboard Opérationnel</strong> - Interface Terrain Avancée<br>
    Filtrage dynamique • Export données • Monitoring temps réel
    </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
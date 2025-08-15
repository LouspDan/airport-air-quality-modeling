#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de fichiers CSV avec données réalistes d'aéroport
Version corrigée - Simule des sources externes
Projet: Airport Air Quality Modeling
Auteur: Portfolio Project
Date: 2025-08-15
"""

import os
import csv
import random
import datetime
from typing import List, Dict, Tuple
import argparse
import json
from pathlib import Path
import math

class AirportCSVGenerator:
    """Générateur de fichiers CSV avec patterns réalistes d'aéroports européens"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration réaliste basée sur données aéroports européens
        self.airlines = [
            # Low-Cost (forte fréquence)
            {"iata": "FR", "icao": "RYR", "name": "Ryanair", "country": "IRL", "weight": 0.25},
            {"iata": "U2", "icao": "EZY", "name": "EasyJet", "country": "GBR", "weight": 0.20},
            {"iata": "W6", "icao": "WZZ", "name": "Wizz Air", "country": "HUN", "weight": 0.15},
            
            # Compagnies nationales
            {"iata": "AF", "icao": "AFR", "name": "Air France", "country": "FRA", "weight": 0.15},
            {"iata": "KL", "icao": "KLM", "name": "KLM", "country": "NLD", "weight": 0.12},
            
            # Européennes traditionnelles
            {"iata": "LH", "icao": "DLH", "name": "Lufthansa", "country": "DEU", "weight": 0.10},
            {"iata": "BA", "icao": "BAW", "name": "British Airways", "country": "GBR", "weight": 0.08},
            {"iata": "IB", "icao": "IBE", "name": "Iberia", "country": "ESP", "weight": 0.06},
            {"iata": "AZ", "icao": "ITY", "name": "ITA Airways", "country": "ITA", "weight": 0.05},
            
            # Long-courrier
            {"iata": "EK", "icao": "UAE", "name": "Emirates", "country": "ARE", "weight": 0.03},
            {"iata": "QR", "icao": "QTR", "name": "Qatar Airways", "country": "QAT", "weight": 0.02},
            {"iata": "TK", "icao": "THY", "name": "Turkish Airlines", "country": "TUR", "weight": 0.04}
        ]
        
        self.aircraft_fleet = [
            {"icao": "A320", "airline_preference": ["U2", "W6", "AF", "LH", "BA", "IB"], "capacity": 180, "weight": 0.40},
            {"icao": "B738", "airline_preference": ["FR", "KL", "TK"], "capacity": 189, "weight": 0.35},
            {"icao": "A333", "airline_preference": ["AF", "KL", "EK", "QR", "TK"], "capacity": 300, "weight": 0.15},
            {"icao": "B77W", "airline_preference": ["AF", "EK", "QR"], "capacity": 350, "weight": 0.10}
        ]
        
        # Destinations réalistes avec distances depuis Paris
        self.destinations = {
            "domestic": [
                {"iata": "NCE", "city": "Nice", "country": "FRA", "distance": 685, "weight": 0.25},
                {"iata": "TLS", "city": "Toulouse", "country": "FRA", "distance": 590, "weight": 0.20},
                {"iata": "LYS", "city": "Lyon", "country": "FRA", "distance": 395, "weight": 0.15},
                {"iata": "MRS", "city": "Marseille", "country": "FRA", "distance": 660, "weight": 0.15},
                {"iata": "BOD", "city": "Bordeaux", "country": "FRA", "distance": 500, "weight": 0.12},
                {"iata": "NTE", "city": "Nantes", "country": "FRA", "distance": 340, "weight": 0.13}
            ],
            "european": [
                {"iata": "LHR", "city": "London", "country": "GBR", "distance": 344, "weight": 0.12},
                {"iata": "FRA", "city": "Frankfurt", "country": "DEU", "distance": 296, "weight": 0.10},
                {"iata": "AMS", "city": "Amsterdam", "country": "NLD", "distance": 266, "weight": 0.09},
                {"iata": "MAD", "city": "Madrid", "country": "ESP", "distance": 1054, "weight": 0.08},
                {"iata": "FCO", "city": "Rome", "country": "ITA", "distance": 1105, "weight": 0.08},
                {"iata": "BCN", "city": "Barcelona", "country": "ESP", "distance": 831, "weight": 0.07},
                {"iata": "MUC", "city": "Munich", "country": "DEU", "distance": 684, "weight": 0.06},
                {"iata": "ZUR", "city": "Zurich", "country": "CHE", "distance": 439, "weight": 0.05},
                {"iata": "VIE", "city": "Vienna", "country": "AUT", "distance": 1037, "weight": 0.05},
                {"iata": "BRU", "city": "Brussels", "country": "BEL", "distance": 177, "weight": 0.04}
            ],
            "international": [
                {"iata": "JFK", "city": "New York", "country": "USA", "distance": 5837, "weight": 0.15},
                {"iata": "DXB", "city": "Dubai", "country": "ARE", "distance": 5253, "weight": 0.12},
                {"iata": "DOH", "city": "Doha", "country": "QAT", "distance": 4946, "weight": 0.10},
                {"iata": "IST", "city": "Istanbul", "country": "TUR", "distance": 1713, "weight": 0.08},
                {"iata": "CAI", "city": "Cairo", "country": "EGY", "distance": 2795, "weight": 0.06},
                {"iata": "CAS", "city": "Casablanca", "country": "MAR", "distance": 1467, "weight": 0.05},
                {"iata": "YUL", "city": "Montreal", "country": "CAN", "distance": 5511, "weight": 0.04},
                {"iata": "NRT", "city": "Tokyo", "country": "JPN", "distance": 9714, "weight": 0.03}
            ]
        }
        
        # Patterns temporels réalistes
        self.seasonal_factors = {
            1: 0.75, 2: 0.80, 3: 0.90, 4: 1.00, 5: 1.10, 6: 1.25,
            7: 1.35, 8: 1.30, 9: 1.15, 10: 1.05, 11: 0.85, 12: 0.95
        }
        
        # Distribution horaire réaliste (créneaux de pointe)
        self.hourly_distribution = {
            5: 0.01, 6: 0.03, 7: 0.08, 8: 0.12, 9: 0.10, 10: 0.08,
            11: 0.07, 12: 0.06, 13: 0.05, 14: 0.05, 15: 0.06, 16: 0.07,
            17: 0.09, 18: 0.11, 19: 0.08, 20: 0.06, 21: 0.04, 22: 0.02, 23: 0.01
        }
    
    def generate_flight_number(self, airline_code: str) -> str:
        """Génération de numéros de vol réalistes par compagnie"""
        patterns = {
            "FR": lambda: f"FR{random.randint(1000, 9999)}",
            "U2": lambda: f"U2{random.randint(100, 999)}",
            "W6": lambda: f"W6{random.randint(1000, 9999)}",
            "AF": lambda: f"AF{random.randint(100, 999)}",
            "KL": lambda: f"KL{random.randint(100, 999)}",
        }
        return patterns.get(airline_code, lambda: f"{airline_code}{random.randint(100, 999)}")()
    
    def get_compatible_aircraft(self, airline_code: str) -> str:
        """Sélection d'aéronef compatible avec la compagnie"""
        compatible_aircraft = [
            ac for ac in self.aircraft_fleet 
            if airline_code in ac["airline_preference"]
        ]
        
        if compatible_aircraft:
            weights = [ac["weight"] for ac in compatible_aircraft]
            selected = random.choices(compatible_aircraft, weights=weights)[0]
            return selected["icao"]
        else:
            return "A320"
    
    def calculate_realistic_timings(self, distance_km: int, aircraft_type: str) -> Dict:
        """Calcul des timings réalistes basés sur distance et type d'avion"""
        cruise_speeds = {"A320": 450, "B738": 445, "A333": 480, "B77W": 490}
        speed = cruise_speeds.get(aircraft_type, 450)
        
        flight_time_hours = distance_km / speed
        
        if distance_km < 500:
            taxi_out = random.uniform(8, 18)
            taxi_in = random.uniform(5, 12)
        elif distance_km < 2000:
            taxi_out = random.uniform(12, 25)
            taxi_in = random.uniform(8, 15)
        else:
            taxi_out = random.uniform(18, 35)
            taxi_in = random.uniform(10, 22)
        
        return {
            "flight_time_hours": flight_time_hours,
            "taxi_out_minutes": taxi_out,
            "taxi_in_minutes": taxi_in
        }
    
    def introduce_data_quality_issues(self, data: Dict, error_rate: float = 0.05) -> Dict:
        """Introduction d'erreurs réalistes pour tester la validation qualité"""
        if random.random() < error_rate:
            error_type = random.choice([
                "missing_passenger_count",
                "invalid_time_format", 
                "wrong_aircraft_code",
                "negative_fuel"
            ])
            
            if error_type == "missing_passenger_count":
                data["passengers"] = ""
            elif error_type == "invalid_time_format":
                data["scheduled_departure"] = "25:99"
            elif error_type == "wrong_aircraft_code":
                data["aircraft_type"] = "WRONG"
            elif error_type == "negative_fuel":
                data["fuel_kg"] = -1000
            
            data["_quality_issue"] = error_type
        
        return data
    
    def generate_flights_csv(self, start_date: str, days: int, avg_flights_per_day: int) -> str:
        """Génération du fichier CSV des vols"""
        filename = f"flights_data_{start_date.replace('-', '_')}_to_{days}days.csv"
        filepath = self.output_dir / filename
        
        headers = [
            "flight_id", "flight_number", "airline_iata", "airline_icao", 
            "aircraft_type", "flight_date", "scheduled_departure", "scheduled_arrival",
            "origin_airport", "destination_airport", "destination_city", "destination_country",
            "distance_km", "passengers", "fuel_kg", "flight_type", 
            "taxi_out_minutes", "taxi_in_minutes", "flight_time_hours",
            "load_factor", "aircraft_age_years", "crew_count",
            "data_source", "created_timestamp"
        ]
        
        print(f"📝 Génération du fichier: {filename}")
        print(f"📅 Période: {start_date} ({days} jours)")
        print(f"✈️ ~{avg_flights_per_day} vols/jour")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            total_flights = 0
            
            for day in range(days):
                seasonal_factor = self.seasonal_factors.get(current_date.month, 1.0)
                weekday_factor = 0.75 if current_date.weekday() in [5, 6] else 1.0
                daily_flights = int(avg_flights_per_day * seasonal_factor * weekday_factor)
                
                for flight_idx in range(daily_flights):
                    airline = random.choices(self.airlines, weights=[a["weight"] for a in self.airlines])[0]
                    aircraft_type = self.get_compatible_aircraft(airline["iata"])
                    aircraft_data = next(ac for ac in self.aircraft_fleet if ac["icao"] == aircraft_type)
                    
                    # Sélection destination selon profil compagnie
                    if airline["iata"] in ["FR", "U2", "W6"]:
                        route_weights = {"european": 0.70, "domestic": 0.25, "international": 0.05}
                    elif airline["iata"] in ["EK", "QR", "TK"]:
                        route_weights = {"international": 0.60, "european": 0.35, "domestic": 0.05}
                    else:
                        route_weights = {"european": 0.50, "domestic": 0.30, "international": 0.20}
                    
                    route_type = random.choices(
                        list(route_weights.keys()), 
                        weights=list(route_weights.values())
                    )[0]
                    
                    destinations = self.destinations[route_type]
                    dest_weights = [d["weight"] for d in destinations]
                    destination = random.choices(destinations, weights=dest_weights)[0]
                    
                    hour_weights = list(self.hourly_distribution.values())
                    hour = random.choices(list(self.hourly_distribution.keys()), weights=hour_weights)[0]
                    minute = random.choice([0, 15, 30, 45])
                    
                    timings = self.calculate_realistic_timings(destination["distance"], aircraft_type)
                    
                    departure_time = f"{hour:02d}:{minute:02d}"
                    arrival_datetime = datetime.datetime.combine(current_date, datetime.time(hour, minute)) + \
                                     datetime.timedelta(hours=timings["flight_time_hours"])
                    arrival_time = arrival_datetime.strftime("%H:%M")
                    
                    base_capacity = aircraft_data["capacity"]
                    load_factor = random.uniform(0.65, 0.95)
                    passengers = int(base_capacity * load_factor)
                    
                    fuel_per_km = {"A320": 3.2, "B738": 3.4, "A333": 5.8, "B77W": 7.2}
                    base_fuel = destination["distance"] * fuel_per_km.get(aircraft_type, 3.5)
                    fuel_kg = int(base_fuel * random.uniform(0.9, 1.1))
                    
                    flight_data = {
                        "flight_id": f"FLT_{current_date.strftime('%Y%m%d')}_{flight_idx+1:04d}",
                        "flight_number": self.generate_flight_number(airline["iata"]),
                        "airline_iata": airline["iata"],
                        "airline_icao": airline["icao"],
                        "aircraft_type": aircraft_type,
                        "flight_date": current_date.strftime("%Y-%m-%d"),
                        "scheduled_departure": departure_time,
                        "scheduled_arrival": arrival_time,
                        "origin_airport": "PVE",
                        "destination_airport": destination["iata"],
                        "destination_city": destination["city"],
                        "destination_country": destination["country"],
                        "distance_km": destination["distance"],
                        "passengers": passengers,
                        "fuel_kg": fuel_kg,
                        "flight_type": route_type,
                        "taxi_out_minutes": round(timings["taxi_out_minutes"], 1),
                        "taxi_in_minutes": round(timings["taxi_in_minutes"], 1),
                        "flight_time_hours": round(timings["flight_time_hours"], 2),
                        "load_factor": round(load_factor, 3),
                        "aircraft_age_years": random.randint(2, 15),
                        "crew_count": 4 if aircraft_type in ["A320", "B738"] else 8,
                        "data_source": f"OPS_SYSTEM_{airline['icao']}",
                        "created_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    flight_data = self.introduce_data_quality_issues(flight_data, 0.05)
                    writer.writerow(flight_data)
                    total_flights += 1
                
                current_date += datetime.timedelta(days=1)
                
                if (day + 1) % 7 == 0:
                    print(f"  📊 Semaine {(day+1)//7}: {total_flights} vols générés")
        
        print(f"✅ Fichier généré: {filename}")
        print(f"📈 Total: {total_flights} vols")
        return str(filepath)
    
    def generate_weather_csv(self, start_date: str, days: int) -> str:
        """Génération des données météorologiques"""
        filename = f"weather_data_{start_date.replace('-', '_')}_to_{days}days.csv"
        filepath = self.output_dir / filename
        
        headers = [
            "station_id", "measurement_time", "temperature_c", "humidity_percent",
            "pressure_hpa", "wind_speed_ms", "wind_direction_deg", "visibility_m",
            "precipitation_mm", "cloud_cover_percent", "weather_conditions",
            "data_quality", "source_system"
        ]
        
        print(f"🌤️ Génération météo: {filename}")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            stations = ["PVE_METEO_01", "PVE_METEO_02", "PVE_METEO_03"]
            
            for day in range(days):
                for hour in range(24):
                    timestamp = current_date + datetime.timedelta(days=day, hours=hour)
                    
                    for station in stations:
                        base_temp = {
                            1: 4, 2: 6, 3: 10, 4: 14, 5: 18, 6: 22,
                            7: 25, 8: 24, 9: 20, 10: 15, 11: 9, 12: 5
                        }[timestamp.month]
                        
                        daily_variation = 5 * math.sin(2 * math.pi * hour / 24)
                        temperature = base_temp + daily_variation + random.uniform(-3, 3)
                        
                        weather_data = {
                            "station_id": station,
                            "measurement_time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "temperature_c": round(temperature, 1),
                            "humidity_percent": random.randint(40, 90),
                            "pressure_hpa": round(random.uniform(990, 1030), 1),
                            "wind_speed_ms": round(random.uniform(0, 15), 1),
                            "wind_direction_deg": random.randint(0, 360),
                            "visibility_m": random.choice([10000, 8000, 5000, 2000]),
                            "precipitation_mm": round(random.uniform(0, 5) if random.random() < 0.2 else 0, 1),
                            "cloud_cover_percent": random.randint(0, 100),
                            "weather_conditions": random.choice([
                                "Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Rain", "Fog"
                            ]),
                            "data_quality": random.choice(["Valid", "Valid", "Valid", "Estimated"]),
                            "source_system": "METEO_FRANCE_API"
                        }
                        
                        writer.writerow(weather_data)
        
        print(f"✅ Météo générée: {filename}")
        return str(filepath)
    
    def generate_aircraft_catalog_csv(self) -> str:
        """Génération du catalogue d'aéronefs"""
        filename = "aircraft_catalog_icao_2025.csv"
        filepath = self.output_dir / filename
        
        headers = [
            "icao_designation", "manufacturer", "model", "variant", "engine_type",
            "number_of_engines", "typical_seating", "max_seating", "cargo_capacity_m3",
            "max_takeoff_weight_kg", "empty_weight_kg", "fuel_capacity_l",
            "cruise_speed_kmh", "max_range_km", "service_ceiling_m",
            "wingspan_m", "length_m", "height_m", "first_flight_year",
            "certification_date", "production_status", "noise_chapter",
            "co2_efficiency_g_pkm", "data_source", "last_updated"
        ]
        
        aircraft_specs = [
            {
                "icao_designation": "A320", "manufacturer": "Airbus", "model": "A320",
                "variant": "A320-200", "engine_type": "CFM56-5/V2500", "number_of_engines": 2,
                "typical_seating": 150, "max_seating": 180, "cargo_capacity_m3": 37.4,
                "max_takeoff_weight_kg": 78000, "empty_weight_kg": 42600, "fuel_capacity_l": 24210,
                "cruise_speed_kmh": 828, "max_range_km": 6150, "service_ceiling_m": 12000,
                "wingspan_m": 35.8, "length_m": 37.6, "height_m": 11.8, "first_flight_year": 1987,
                "certification_date": "1988-02-26", "production_status": "Active",
                "noise_chapter": "Chapter 4", "co2_efficiency_g_pkm": 98
            },
            {
                "icao_designation": "B738", "manufacturer": "Boeing", "model": "737",
                "variant": "737-800", "engine_type": "CFM56-7", "number_of_engines": 2,
                "typical_seating": 162, "max_seating": 189, "cargo_capacity_m3": 44.5,
                "max_takeoff_weight_kg": 79000, "empty_weight_kg": 41413, "fuel_capacity_l": 26020,
                "cruise_speed_kmh": 842, "max_range_km": 5765, "service_ceiling_m": 12500,
                "wingspan_m": 35.8, "length_m": 39.5, "height_m": 12.5, "first_flight_year": 1997,
                "certification_date": "1998-03-13", "production_status": "Active",
                "noise_chapter": "Chapter 4", "co2_efficiency_g_pkm": 101
            },
            {
                "icao_designation": "A333", "manufacturer": "Airbus", "model": "A330",
                "variant": "A330-300", "engine_type": "Trent 700/PW4000", "number_of_engines": 2,
                "typical_seating": 277, "max_seating": 440, "cargo_capacity_m3": 136,
                "max_takeoff_weight_kg": 242000, "empty_weight_kg": 120500, "fuel_capacity_l": 139090,
                "cruise_speed_kmh": 871, "max_range_km": 11750, "service_ceiling_m": 12500,
                "wingspan_m": 60.3, "length_m": 63.7, "height_m": 16.9, "first_flight_year": 1992,
                "certification_date": "1993-10-21", "production_status": "Active",
                "noise_chapter": "Chapter 4", "co2_efficiency_g_pkm": 89
            },
            {
                "icao_designation": "B77W", "manufacturer": "Boeing", "model": "777",
                "variant": "777-300ER", "engine_type": "GE90-115B/Trent 800", "number_of_engines": 2,
                "typical_seating": 310, "max_seating": 396, "cargo_capacity_m3": 226,
                "max_takeoff_weight_kg": 351500, "empty_weight_kg": 167829, "fuel_capacity_l": 181280,
                "cruise_speed_kmh": 905, "max_range_km": 14490, "service_ceiling_m": 13100,
                "wingspan_m": 64.8, "length_m": 73.9, "height_m": 18.5, "first_flight_year": 2003,
                "certification_date": "2004-03-16", "production_status": "Active",
                "noise_chapter": "Chapter 4", "co2_efficiency_g_pkm": 85
            }
        ]
        
        print(f"✈️ Génération catalogue aéronefs: {filename}")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for spec in aircraft_specs:
                spec.update({
                    "data_source": "ICAO_AIRCRAFT_DATABASE_2025",
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                writer.writerow(spec)
        
        print(f"✅ Catalogue généré: {filename}")
        return str(filepath)
    
    def generate_emission_factors_csv(self) -> str:
        """Génération des facteurs d'émission certifiés ICAO"""
        filename = "emission_factors_icao_2025.csv"
        filepath = self.output_dir / filename
        
        headers = [
            "engine_uid", "engine_designation", "manufacturer", "aircraft_types",
            "certification_date", "thrust_rating_kn", "bypass_ratio",
            "fuel_flow_idle_kgs", "fuel_flow_approach_kgs", "fuel_flow_climbout_kgs", "fuel_flow_takeoff_kgs",
            "nox_idle_gkg", "nox_approach_gkg", "nox_climbout_gkg", "nox_takeoff_gkg",
            "co_idle_gkg", "co_approach_gkg", "co_climbout_gkg", "co_takeoff_gkg",
            "hc_idle_gkg", "hc_approach_gkg", "hc_climbout_gkg", "hc_takeoff_gkg",
            "certification_standard", "data_source", "last_updated"
        ]
        
        emission_data = [
            {
                "engine_uid": "1CFM56-5B4", "engine_designation": "CFM56-5B4", 
                "manufacturer": "CFM International", "aircraft_types": "A320 Family",
                "certification_date": "1996-12-20", "thrust_rating_kn": 142.3, "bypass_ratio": 5.1,
                "fuel_flow_idle_kgs": 0.193, "fuel_flow_approach_kgs": 0.532, 
                "fuel_flow_climbout_kgs": 1.678, "fuel_flow_takeoff_kgs": 2.073,
                "nox_idle_gkg": 3.90, "nox_approach_gkg": 19.60, "nox_climbout_gkg": 32.70, "nox_takeoff_gkg": 40.20,
                "co_idle_gkg": 118.00, "co_approach_gkg": 9.40, "co_climbout_gkg": 1.20, "co_takeoff_gkg": 1.10,
                "hc_idle_gkg": 13.60, "hc_approach_gkg": 0.50, "hc_climbout_gkg": 0.10, "hc_takeoff_gkg": 0.10,
                "certification_standard": "CAEP/2"
            },
            {
                "engine_uid": "2V2533-A5", "engine_designation": "V2533-A5",
                "manufacturer": "International Aero Engines", "aircraft_types": "A320 Family",
                "certification_date": "1995-04-12", "thrust_rating_kn": 147.0, "bypass_ratio": 4.9,
                "fuel_flow_idle_kgs": 0.189, "fuel_flow_approach_kgs": 0.524,
                "fuel_flow_climbout_kgs": 1.645, "fuel_flow_takeoff_kgs": 2.039,
                "nox_idle_gkg": 3.80, "nox_approach_gkg": 18.90, "nox_climbout_gkg": 31.80, "nox_takeoff_gkg": 39.10,
                "co_idle_gkg": 125.00, "co_approach_gkg": 10.20, "co_climbout_gkg": 1.30, "co_takeoff_gkg": 1.20,
                "hc_idle_gkg": 14.20, "hc_approach_gkg": 0.60, "hc_climbout_gkg": 0.12, "hc_takeoff_gkg": 0.11,
                "certification_standard": "CAEP/2"
            },
            {
                "engine_uid": "3CFM56-7B27", "engine_designation": "CFM56-7B27",
                "manufacturer": "CFM International", "aircraft_types": "B737-800",
                "certification_date": "2000-08-31", "thrust_rating_kn": 121.4, "bypass_ratio": 5.1,
                "fuel_flow_idle_kgs": 0.078, "fuel_flow_approach_kgs": 0.309,
                "fuel_flow_climbout_kgs": 1.028, "fuel_flow_takeoff_kgs": 1.210,
                "nox_idle_gkg": 4.20, "nox_approach_gkg": 8.60, "nox_climbout_gkg": 14.20, "nox_takeoff_gkg": 14.90,
                "co_idle_gkg": 26.80, "co_approach_gkg": 3.20, "co_climbout_gkg": 0.60, "co_takeoff_gkg": 0.40,
                "hc_idle_gkg": 0.40, "hc_approach_gkg": 0.15, "hc_climbout_gkg": 0.04, "hc_takeoff_gkg": 0.02,
                "certification_standard": "CAEP/4"
            },
            {
                "engine_uid": "4Trent772B", "engine_designation": "Trent 772B",
                "manufacturer": "Rolls-Royce", "aircraft_types": "A330-300",
                "certification_date": "1995-11-15", "thrust_rating_kn": 316.0, "bypass_ratio": 4.9,
                "fuel_flow_idle_kgs": 0.345, "fuel_flow_approach_kgs": 1.120,
                "fuel_flow_climbout_kgs": 3.456, "fuel_flow_takeoff_kgs": 4.123,
                "nox_idle_gkg": 2.90, "nox_approach_gkg": 15.20, "nox_climbout_gkg": 24.80, "nox_takeoff_gkg": 28.50,
                "co_idle_gkg": 78.50, "co_approach_gkg": 6.30, "co_climbout_gkg": 0.80, "co_takeoff_gkg": 0.60,
                "hc_idle_gkg": 8.70, "hc_approach_gkg": 0.35, "hc_climbout_gkg": 0.08, "hc_takeoff_gkg": 0.06,
                "certification_standard": "CAEP/2"
            }
        ]
        
        print(f"🔥 Génération facteurs d'émission: {filename}")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for data in emission_data:
                data.update({
                    "data_source": "ICAO_AIRCRAFT_ENGINE_EMISSIONS_DATABANK",
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                writer.writerow(data)
        
        print(f"✅ Facteurs d'émission générés: {filename}")
        return str(filepath)
    
    def generate_metadata_json(self, generated_files: List[str]) -> str:
        """Génération des métadonnées sur les fichiers créés"""
        metadata = {
            "generation_info": {
                "created_at": datetime.datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "python_version": "3.11+",
                "purpose": "Realistic airport data simulation for ETL pipeline testing"
            },
            "data_sources": {
                "flights": {
                    "description": "Simulated flight operations data based on European airport patterns",
                    "methodology": "Statistical distribution matching real traffic patterns",
                    "seasonal_factors": self.seasonal_factors,
                    "quality_issues": "5% error rate introduced for validation testing",
                    "volume": "Variable by season and day type"
                },
                "weather": {
                    "description": "Simulated meteorological data with realistic Paris climate",
                    "frequency": "Hourly measurements from 3 stations",
                    "parameters": "Temperature, humidity, pressure, wind, visibility, precipitation",
                    "quality": "95% valid data, 5% estimated values"
                },
                "aircraft_catalog": {
                    "description": "Technical specifications from ICAO aircraft database",
                    "source": "ICAO Aircraft Type Designators (Doc 8643)",
                    "coverage": "Major commercial aircraft types in European operations",
                    "accuracy": "Based on published manufacturer specifications"
                },
                "emission_factors": {
                    "description": "Certified emission factors from ICAO Engine Emissions Databank",
                    "standards": ["CAEP/2", "CAEP/4", "CAEP/6"],
                    "pollutants": ["NOx", "CO", "HC"],
                    "methodology": "ICAO Annex 16 Volume II standards"
                }
            },
            "files": []
        }
        
        for filepath in generated_files:
            file_path = Path(filepath)
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            metadata["files"].append({
                "filename": file_path.name,
                "path": str(file_path),
                "size_bytes": file_size,
                "encoding": "utf-8",
                "format": "CSV" if file_path.suffix == ".csv" else "JSON",
                "description": self.get_file_description(file_path.name)
            })
        
        metadata_file = self.output_dir / "data_generation_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Métadonnées générées: {metadata_file.name}")
        return str(metadata_file)
    
    def get_file_description(self, filename: str) -> str:
        """Description des fichiers générés"""
        descriptions = {
            "flights_data": "Operational flight data with schedules, aircraft, passengers, fuel",
            "weather_data": "Meteorological measurements affecting air quality and emissions",
            "aircraft_catalog": "Technical specifications and performance data for aircraft types",
            "emission_factors": "ICAO certified emission factors by engine type and operating mode"
        }
        
        for key, desc in descriptions.items():
            if key in filename:
                return desc
        return "Generated data file for airport air quality modeling"


def main():
    """Fonction principale de génération"""
    parser = argparse.ArgumentParser(description='Générateur de données CSV réalistes pour aéroport')
    parser.add_argument('--start-date', type=str, default='2025-08-01', 
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=30, 
                       help='Nombre de jours à générer')
    parser.add_argument('--flights-per-day', type=int, default=180, 
                       help='Nombre moyen de vols par jour')
    parser.add_argument('--output-dir', type=str, default='data/raw', 
                       help='Dossier de sortie des fichiers')
    parser.add_argument('--all', action='store_true', 
                       help='Générer tous les types de fichiers')
    parser.add_argument('--flights-only', action='store_true', 
                       help='Générer uniquement les données de vol')
    
    args = parser.parse_args()
    
    print("🚀 GÉNÉRATEUR DE DONNÉES CSV - AÉROPORT")
    print("=" * 50)
    print(f"📁 Dossier de sortie: {args.output_dir}")
    print(f"📅 Période: {args.start_date} ({args.days} jours)")
    print(f"✈️ Vols/jour: ~{args.flights_per_day}")
    
    generator = AirportCSVGenerator(args.output_dir)
    generated_files = []
    
    try:
        if args.flights_only:
            # Génération des vols uniquement
            flights_file = generator.generate_flights_csv(
                args.start_date, args.days, args.flights_per_day
            )
            generated_files.append(flights_file)
            
        elif args.all:
            # Génération complète
            print("\n📊 Génération complète des données...")
            
            # 1. Données de vol
            flights_file = generator.generate_flights_csv(
                args.start_date, args.days, args.flights_per_day
            )
            generated_files.append(flights_file)
            
            # 2. Données météo
            weather_file = generator.generate_weather_csv(args.start_date, args.days)
            generated_files.append(weather_file)
            
            # 3. Catalogue aéronefs
            catalog_file = generator.generate_aircraft_catalog_csv()
            generated_files.append(catalog_file)
            
            # 4. Facteurs d'émission
            emission_file = generator.generate_emission_factors_csv()
            generated_files.append(emission_file)
            
            # 5. Métadonnées
            metadata_file = generator.generate_metadata_json(generated_files)
            generated_files.append(metadata_file)
            
        else:
            print("\n❓ Utiliser --all pour génération complète ou --flights-only pour les vols")
            parser.print_help()
            return
        
        print(f"\n✅ GÉNÉRATION TERMINÉE")
        print(f"📁 {len(generated_files)} fichier(s) créé(s) dans {args.output_dir}")
        
        # Résumé des fichiers
        for file_path in generated_files:
            file_size = Path(file_path).stat().st_size
            print(f"  📄 {Path(file_path).name} ({file_size:,} bytes)")
        
        print(f"\n🔄 Prochaine étape: Pipeline ETL pour ingestion en base de données")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return 1

if __name__ == "__main__":
    main()
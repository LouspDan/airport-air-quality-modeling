#!/usr/bin/env python3
import csv
import random
from datetime import datetime, timedelta

def generate_flights_simple(days=30, flights_per_day=180):
    """Génération simple et robuste de données de vol"""
    
    filename = f"data/raw/flights_data_simple_{days}days.csv"
    
    # Données simplifiées mais réalistes
    airlines = ["FR", "U2", "W6", "AF", "KL", "LH", "BA"]
    aircraft = ["A320", "B738", "A333"]
    destinations = ["LHR", "FRA", "AMS", "MAD", "FCO", "BCN", "MUC", "NCE", "TLS", "LYS"]
    
    headers = [
        "flight_id", "flight_number", "airline_iata", "aircraft_type", 
        "flight_date", "scheduled_departure", "destination_airport",
        "distance_km", "passengers", "fuel_kg", "flight_type"
    ]
    
    print(f"Génération de {days * flights_per_day} vols...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        current_date = datetime(2025, 8, 1)
        total_flights = 0
        
        for day in range(days):
            for flight_idx in range(flights_per_day):
                airline = random.choice(airlines)
                aircraft_type = random.choice(aircraft)
                destination = random.choice(destinations)
                
                # Heure aléatoire
                hour = random.randint(6, 23)
                minute = random.choice([0, 15, 30, 45])
                
                flight_data = {
                    "flight_id": f"FLT_{current_date.strftime('%Y%m%d')}_{flight_idx+1:04d}",
                    "flight_number": f"{airline}{random.randint(100, 9999)}",
                    "airline_iata": airline,
                    "aircraft_type": aircraft_type,
                    "flight_date": current_date.strftime("%Y-%m-%d"),
                    "scheduled_departure": f"{hour:02d}:{minute:02d}",
                    "destination_airport": destination,
                    "distance_km": random.randint(300, 2000),
                    "passengers": random.randint(80, 180),
                    "fuel_kg": random.randint(2000, 8000),
                    "flight_type": random.choice(["domestic", "european", "international"])
                }
                
                writer.writerow(flight_data)
                total_flights += 1
            
            current_date += timedelta(days=1)
            
            if (day + 1) % 7 == 0:
                print(f"  Semaine {(day+1)//7}: {total_flights} vols")
    
    print(f"✅ {total_flights} vols générés dans {filename}")
    return filename

if __name__ == "__main__":
    generate_flights_simple()

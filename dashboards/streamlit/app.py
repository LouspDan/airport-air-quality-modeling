#!/usr/bin/env python3
"""
Script de lancement automatique de tous les dashboards
Permet de démarrer l'ensemble du système en une commande
"""

import subprocess
import time
import sys
import os
import webbrowser
from pathlib import Path

# Configuration des dashboards
DASHBOARDS = [
    {
        "name": "Hub Principal",
        "file": "app.py",
        "port": 8500,
        "description": "Interface de navigation principale"
    },
    {
        "name": "Dashboard Exécutif",
        "file": "dashboard_executive.py", 
        "port": 8501,
        "description": "Vue d'ensemble KPIs pour la direction"
    },
    {
        "name": "Dashboard Opérationnel",
        "file": "dashboard_operational.py",
        "port": 8502,
        "description": "Interface terrain pour l'exploitation"
    },
    {
        "name": "Dashboard Environnemental",
        "file": "dashboard_environmental.py",
        "port": 8503,
        "description": "Cartographie géospatiale et analyse atmosphérique"
    }
]

def check_streamlit_installed():
    """Vérifier que Streamlit est installé"""
    try:
        import streamlit
        print("✅ Streamlit est installé")
        return True
    except ImportError:
        print("❌ Streamlit n'est pas installé")
        print("💡 Installation: pip install streamlit")
        return False

def check_dashboard_files():
    """Vérifier que tous les fichiers dashboard existent"""
    dashboard_dir = Path("dashboards/streamlit")
    missing_files = []
    
    for dashboard in DASHBOARDS:
        file_path = dashboard_dir / dashboard["file"]
        if file_path.exists():
            print(f"✅ {dashboard['file']} trouvé")
        else:
            print(f"❌ {dashboard['file']} manquant")
            missing_files.append(dashboard["file"])
    
    return len(missing_files) == 0, missing_files

def launch_dashboard(dashboard):
    """Lancer un dashboard spécifique"""
    print(f"\n🚀 Lancement de {dashboard['name']}...")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        f"dashboards/streamlit/{dashboard['file']}",
        "--server.port", str(dashboard['port']),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   📍 URL: http://localhost:{dashboard['port']}")
        print(f"   📝 Description: {dashboard['description']}")
        print(f"   🆔 PID: {process.pid}")
        
        return process
    
    except Exception as e:
        print(f"❌ Erreur lors du lancement de {dashboard['name']}: {e}")
        return None

def wait_for_startup():
    """Attendre que les services démarrent"""
    print("\n⏳ Attente du démarrage des services...")
    for i in range(5, 0, -1):
        print(f"   {i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")

def open_browsers():
    """Ouvrir les navigateurs pour chaque dashboard"""
    print("🌐 Ouverture des navigateurs...")
    
    for dashboard in DASHBOARDS:
        url = f"http://localhost:{dashboard['port']}"
        print(f"   🔗 Ouverture de {dashboard['name']}: {url}")
        
        try:
            webbrowser.open(url)
            time.sleep(1)  # Délai entre les ouvertures
        except Exception as e:
            print(f"   ⚠️ Impossible d'ouvrir automatiquement: {e}")
            print(f"   💡 Ouvrez manuellement: {url}")

def display_summary():
    """Afficher le résumé des URLs"""
    print("\n" + "="*60)
    print("🎉 TOUS LES DASHBOARDS SONT LANCÉS !")
    print("="*60)
    
    print("\n📋 URLs d'accès:")
    for dashboard in DASHBOARDS:
        print(f"   🔗 {dashboard['name']:.<30} http://localhost:{dashboard['port']}")
    
    print(f"\n💡 Recommandation:")
    print(f"   1. Commencez par le Hub Principal: http://localhost:8500")
    print(f"   2. Naviguez entre les dashboards via les onglets ou URLs directes")
    print(f"   3. Pour arrêter: Ctrl+C dans ce terminal")
    
    print(f"\n🛠️ Commandes individuelles:")
    for dashboard in DASHBOARDS:
        print(f"   streamlit run dashboards/streamlit/{dashboard['file']} --server.port {dashboard['port']}")

def main():
    """Fonction principale"""
    print("🛬 AIRPORT AIR QUALITY - LANCEMENT MULTI-DASHBOARDS")
    print("="*60)
    
    # Vérifications préalables
    if not check_streamlit_installed():
        return
    
    files_ok, missing = check_dashboard_files()
    if not files_ok:
        print(f"\n❌ Fichiers manquants: {missing}")
        print("💡 Assurez-vous d'être dans le répertoire racine du projet")
        return
    
    # Lancement des dashboards
    processes = []
    for dashboard in DASHBOARDS:
        process = launch_dashboard(dashboard)
        if process:
            processes.append(process)
        time.sleep(2)  # Délai entre les lancements
    
    if not processes:
        print("❌ Aucun dashboard n'a pu être lancé")
        return
    
    # Attendre le démarrage
    wait_for_startup()
    
    # Ouvrir les navigateurs
    open_browsers()
    
    # Afficher le résumé
    display_summary()
    
    # Attendre l'arrêt
    try:
        print(f"\n⌨️ Appuyez sur Ctrl+C pour arrêter tous les dashboards...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n🛑 Arrêt des dashboards...")
        for i, process in enumerate(processes):
            try:
                process.terminate()
                print(f"   ✅ Dashboard {i+1} arrêté")
            except:
                print(f"   ⚠️ Dashboard {i+1} déjà arrêté")
        
        print("👋 Tous les dashboards ont été arrêtés!")

if __name__ == "__main__":
    main()
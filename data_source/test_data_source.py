#!/usr/bin/env python3
"""
Script de test pour valider la source de données USGS Earthquake
"""
import requests
import json
from datetime import datetime

def test_api_connectivity():
    """Test 1: Vérifier la connectivité à l'API"""
    print("=" * 60)
    print("Test 1: Connectivité API")
    print("=" * 60)
    
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✓ API accessible (status 200)")
            return response.json()
        else:
            print(f"✗ Erreur: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
        return None

def test_data_structure(data):
    """Test 2: Vérifier la structure des données"""
    print("\n" + "=" * 60)
    print("Test 2: Structure des données")
    print("=" * 60)
    
    if not data:
        print("✗ Pas de données à analyser")
        return False
    
    # Vérifier la structure principale
    if data.get('type') == 'FeatureCollection':
        print("✓ Type: FeatureCollection")
    else:
        print("✗ Type invalide")
        return False
    
    if 'features' in data:
        print(f"✓ Champ 'features' présent ({len(data['features'])} événements)")
    else:
        print("✗ Champ 'features' absent")
        return False
    
    if 'metadata' in data:
        print("✓ Champ 'metadata' présent")
    else:
        print("✗ Champ 'metadata' absent")
    
    return True

def test_event_schema(data):
    """Test 3: Vérifier le schéma d'un événement"""
    print("\n" + "=" * 60)
    print("Test 3: Schéma d'un événement")
    print("=" * 60)
    
    if not data or not data.get('features'):
        print("✗ Pas d'événements à analyser")
        return False
    
    event = data['features'][0]
    required_fields = {
        'id': str,
        'properties': dict,
        'geometry': dict
    }
    
    for field, expected_type in required_fields.items():
        if field in event and isinstance(event[field], expected_type):
            print(f"✓ Champ '{field}': {expected_type.__name__}")
        else:
            print(f"✗ Champ '{field}' manquant ou type invalide")
            return False
    
    # Vérifier les propriétés importantes
    props = event['properties']
    prop_fields = ['mag', 'place', 'time', 'type']
    
    for field in prop_fields:
        if field in props:
            print(f"✓ Propriété '{field}': {props[field]}")
        else:
            print(f"✗ Propriété '{field}' absente")
    
    # Vérifier la géométrie
    geom = event['geometry']
    if geom.get('type') == 'Point' and len(geom.get('coordinates', [])) == 3:
        lon, lat, depth = geom['coordinates']
        print(f"✓ Coordonnées valides: lon={lon}, lat={lat}, depth={depth}km")
    else:
        print("✗ Géométrie invalide")
    
    return True

def test_sample_data(data):
    """Test 4: Afficher des exemples de données"""
    print("\n" + "=" * 60)
    print("Test 4: Exemples de données")
    print("=" * 60)
    
    if not data or not data.get('features'):
        print("✗ Pas de données")
        return
    
    print(f"\nNombre total d'événements: {len(data['features'])}")
    print(f"Période: {data['metadata'].get('title', 'N/A')}")
    
    print("\n3 premiers événements:")
    print("-" * 60)
    
    for i, event in enumerate(data['features'][:3], 1):
        props = event['properties']
        coords = event['geometry']['coordinates']
        
        # Convertir le timestamp
        event_time = datetime.fromtimestamp(props['time'] / 1000)
        
        print(f"\nÉvénement {i}:")
        print(f"  ID: {event['id']}")
        print(f"  Magnitude: {props.get('mag', 'N/A')}")
        print(f"  Lieu: {props.get('place', 'N/A')}")
        print(f"  Temps: {event_time} UTC")
        print(f"  Position: lon={coords[0]:.2f}, lat={coords[1]:.2f}, depth={coords[2]:.1f}km")

def test_throughput_estimate():
    """Test 5: Estimer le débit"""
    print("\n" + "=" * 60)
    print("Test 5: Estimation du débit")
    print("=" * 60)
    
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        count_hour = len(data['features'])
        count_minute = count_hour / 60
        count_second = count_hour / 3600
        
        print(f"Événements dernière heure: {count_hour}")
        print(f"Débit moyen: {count_minute:.2f} événements/minute")
        print(f"Débit moyen: {count_second:.4f} événements/seconde")
        
        # Estimer la taille
        json_size = len(response.text)
        print(f"\nTaille payload JSON: {json_size / 1024:.2f} KB")
        print(f"Taille estimée par événement: {json_size / count_hour / 1024:.2f} KB")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")

def main():
    print("\n" + "=" * 60)
    print("VALIDATION DE LA SOURCE DE DONNÉES USGS EARTHQUAKE")
    print("=" * 60)
    
    # Exécuter tous les tests
    data = test_api_connectivity()
    
    if data:
        test_data_structure(data)
        test_event_schema(data)
        test_sample_data(data)
        test_throughput_estimate()
        
        print("\n" + "=" * 60)
        print("✓ TOUS LES TESTS TERMINÉS")
        print("=" * 60)
        print("\nLa source de données est validée et prête à être utilisée.")
    else:
        print("\n" + "=" * 60)
        print("✗ ÉCHEC DE LA VALIDATION")
        print("=" * 60)

if __name__ == "__main__":
    main()

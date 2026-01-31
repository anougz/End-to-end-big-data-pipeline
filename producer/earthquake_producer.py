#!/usr/bin/env python3
"""
Producer Kafka pour les données de tremblements de terre USGS
"""

from kafka import KafkaProducer
import requests
import json
import time
from datetime import datetime, timezone
import sys

# Configuration
KAFKA_BROKER = "10.0.0.121:9092"
KAFKA_TOPIC = "earthquake-events"
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
POLL_INTERVAL = 30  # Interroger l'API toutes les 60 secondes

class EarthquakeProducer:
    def __init__(self):
        """Initialiser le producer Kafka"""
        print(f"Connexion au broker Kafka: {KAFKA_BROKER}")
        
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Configuration pour la fiabilité
            acks=1,
            retries=3,
            max_in_flight_requests_per_connection=5,
            # Configuration pour la performance
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        
        # Set pour garder les IDs déjà traités
        self.seen_ids = set()
        
        print(f"✓ Producer Kafka initialisé")
        print(f"✓ Topic: {KAFKA_TOPIC}")
        print()
    
    def fetch_earthquakes(self):
        """Récupérer les données de l'API USGS"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Interrogation de l'API USGS...")
            response = requests.get(USGS_API_URL, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            print(f"  → {len(features)} événements récupérés")
            return features
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des données: {e}")
            return []
    
    def transform_event(self, feature):
        """Transformer un événement GeoJSON en format simplifié"""
        props = feature.get('properties', {})
        coords = feature.get('geometry', {}).get('coordinates', [None, None, None])
        
        event = {
            'id': feature.get('id'),
            'magnitude': props.get('mag'),
            'place': props.get('place'),
            'time': props.get('time'),  # Unix timestamp en ms
            'updated': props.get('updated'),
            'latitude': coords[1],
            'longitude': coords[0],
            'depth': coords[2],
            'type': props.get('type'),
            'status': props.get('status'),
            'tsunami': props.get('tsunami', 0),
            'sig': props.get('sig'),
            'net': props.get('net'),
            'code': props.get('code'),
            'magType': props.get('magType'),
            'ingestion_timestamp': datetime.utcnow().isoformat()
        }
        
        return event
    
    def send_to_kafka(self, event):
        """Envoyer un événement à Kafka"""
        event_id = event['id']
        
        try:
            # Envoyer le message avec l'ID comme clé
            future = self.producer.send(
                KAFKA_TOPIC,
                key=event_id,
                value=event
            )
            
            # Attendre la confirmation (optionnel, pour la démo)
            record_metadata = future.get(timeout=10)
            
            return True, record_metadata
            
        except Exception as e:
            print(f"✗ Erreur lors de l'envoi de {event_id}: {e}")
            return False, None
    
    def run(self):
        """Boucle principale du producer"""
        print("=== Démarrage du Producer Earthquake ===")
        print(f"API: {USGS_API_URL}")
        print(f"Intervalle de polling: {POLL_INTERVAL} secondes")
        print(f"Topic Kafka: {KAFKA_TOPIC}")
        print()
        print("Appuyez sur Ctrl+C pour arrêter")
        print("=" * 60)
        print()
        
        iteration = 0
        total_sent = 0
        
        try:
            while True:
                iteration += 1
                print(f"\n--- Itération {iteration} ---")
                
                # Récupérer les événements
                features = self.fetch_earthquakes()
                
                new_events = 0
                sent_count = 0
                
                # Traiter chaque événement
                for feature in features:
                    event_id = feature.get('id')
                    
                    # Ignorer si déjà traité
                    if event_id in self.seen_ids:
                        continue
                    
                    # Nouveau événement
                    new_events += 1
                    self.seen_ids.add(event_id)
                    
                    # Transformer et envoyer
                    event = self.transform_event(feature)
                    success, metadata = self.send_to_kafka(event)
                    
                    if success:
                        sent_count += 1
                        total_sent += 1
                        
                        mag = event.get('magnitude', 'N/A')
                        place = event.get('place', 'Unknown')
                        
                        print(f"  ✓ Envoyé: {event_id[:15]}... | Mag {mag} | {place[:50]}")
                
                # Résumé de l'itération
                print()
                print(f"  Nouveaux événements: {new_events}")
                print(f"  Envoyés avec succès: {sent_count}")
                print(f"  Total envoyés: {total_sent}")
                print(f"  IDs en cache: {len(self.seen_ids)}")
                
                # Nettoyer le cache si trop grand (garder les 10000 derniers)
                if len(self.seen_ids) > 10000:
                    self.seen_ids = set(list(self.seen_ids)[-5000:])
                    print("  ℹ Cache nettoyé")
                
                # Attendre avant la prochaine itération
                print(f"\n  Attente de {POLL_INTERVAL} secondes...")
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n=== Arrêt du Producer ===")
            print(f"Total d'événements envoyés: {total_sent}")
            
        finally:
            # Fermer proprement le producer
            print("Fermeture du producer Kafka...")
            self.producer.flush()
            self.producer.close()
            print("✓ Producer fermé")

def main():
    """Point d'entrée principal"""
    producer = EarthquakeProducer()
    producer.run()

if __name__ == "__main__":
    main()


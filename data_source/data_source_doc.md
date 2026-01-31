# Source de données: USGS Earthquake API

## Informations générales
- **Source**: United States Geological Survey (USGS)
- **URL de base**: https://earthquake.usgs.gov/earthquakes/feed/v1.0/
- **Type**: API REST publique
- **Format**: GeoJSON
- **Authentification**: Aucune (accès libre)

## Endpoints disponibles
- Dernière heure: `summary/all_hour.geojson`
- Dernier jour: `summary/all_day.geojson`
- Derniers 7 jours: `summary/all_week.geojson`
- Dernier mois: `summary/all_month.geojson`

## Endpoint choisi
`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`

## Schéma des données

### Structure principale
```json
{
  "type": "FeatureCollection",
  "metadata": {...},
  "features": [...]
}
```

### Structure d'un événement (feature)
```json
{
  "type": "Feature",
  "properties": {
    "mag": 1.2,              # Magnitude (Double)
    "place": "10km NE of...", # Localisation (String)
    "time": 1672531200000,   # Timestamp Unix en ms (Long)
    "updated": 1672531800000,
    "tz": null,
    "url": "...",
    "detail": "...",
    "felt": null,
    "cdi": null,
    "mmi": null,
    "alert": null,
    "status": "reviewed",
    "tsunami": 0,
    "sig": 23,
    "net": "ak",
    "code": "...",
    "ids": "...",
    "sources": "...",
    "types": "...",
    "nst": null,
    "dmin": null,
    "rms": 0.13,
    "gap": null,
    "magType": "ml",
    "type": "earthquake"
  },
  "geometry": {
    "type": "Point",
    "coordinates": [
      -151.5678,  # Longitude (Double)
      63.2345,    # Latitude (Double)  
      8.9         # Depth en km (Double)
    ]
  },
  "id": "ak0234..."
}
```

## Champs clés pour notre pipeline
- **id**: Identifiant unique de l'événement
- **time**: Timestamp de l'événement (event time) en millisecondes Unix
- **magnitude (mag)**: Magnitude du séisme
- **coordinates**: [longitude, latitude, depth]
- **place**: Description textuelle de la localisation

## Débit attendu
- **Fréquence**: ~20-200 événements par heure globalement
- **Latence API**: < 1 seconde typiquement
- **Rate limit**: Aucun mentionné (usage raisonnable attendu)

## Stratégie de polling
- Interroger l'API toutes les 60 secondes
- Filtrer les événements déjà traités via leur ID
- Gérer les duplicatas côté producer

## Timezone et sémantique temporelle
- **Event time**: Champ `time` (milliseconds since epoch, UTC)
- **Processing time**: Timestamp d'ingestion dans Kafka
- **Watermark**: 10 minutes de retard toléré

## Licensing et attribution
- **Source**: USGS - Domaine public (US Government work)
- **Attribution recommandée**: "Data provided by USGS Earthquake Hazards Program"
- **URL**: https://earthquake.usgs.gov/earthquakes/feed/v1.0/

## Tests effectués
```bash
# Test effectué le: [DATE]
curl -s "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson" | jq '.features | length'
# Résultat: X événements récupérés
```

## Alternatives considérées
1. ❌ CoinGecko API - Nécessite API key, rate limits stricts
2. ❌ Wikimedia EventStreams - Format SSE complexe
3. ✅ USGS Earthquake - Simple, fiable, pas d'auth requise

# ShoppingSync Control Dokumentation

## Zweck

Das Add-on dient als installierbare Home-Assistant-Huelle fuer den externen ShoppingSync Python-Dienst.

Die Synchronisationslogik bleibt im externen Dienst. Das Add-on uebernimmt:

- Konfigurationszugriff
- Status- und Diagnoseanzeige
- Verbindungstest
- spaeter Standardaktionen wie `sync_now`, `reload`, `restart` und `shutdown`

## Add-on-Optionen

| Option | Beschreibung |
| --- | --- |
| `external_host` | IP-Adresse oder Hostname des Servers, auf dem ShoppingSync laeuft |
| `external_port` | Port des externen ShoppingSync-Dienstes, Standard `8095` |
| `api_base_path` | API-Basispfad, Standard `/api/v1` |
| `api_token` | Token fuer geschuetzte API-Aufrufe |
| `request_timeout_seconds` | Timeout fuer API-Abfragen |

## Geplanter API-Standard

Der externe Dienst soll mindestens diese Endpunkte anbieten:

```text
GET  /api/v1/manifest
GET  /api/v1/health
GET  /api/v1/status
GET  /api/v1/config
PUT  /api/v1/config
POST /api/v1/reload
POST /api/v1/actions/{action_id}
GET  /api/v1/logs/recent
```

## Naechste Ausbaustufen

- Konfigurationsformular aus `/api/v1/manifest` erzeugen
- `PUT /api/v1/config` anbinden
- Aktionen fuer Sync, Reload, Restart und Shutdown anbinden
- Home-Assistant-Zeitzone aus `/api/config` an den externen Dienst uebergeben
- optionale Live-Diagnose ueber WebSocket, SSE oder MQTT vorbereiten

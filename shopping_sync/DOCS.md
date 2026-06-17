# ShoppingSync Control Dokumentation

## Zweck

Das Add-on dient als installierbare Home-Assistant-Huelle fuer den externen ShoppingSync Python-Dienst.

Die Synchronisationslogik bleibt im externen Dienst. Das Add-on uebernimmt:

- Konfigurationszugriff
- Status- und Diagnoseanzeige
- Verbindungstest
- Standardaktionen wie `sync_now`, `reload`, `restart` und `shutdown`

## Add-on-Optionen

| Option | Beschreibung |
| --- | --- |
| `external_host` | IP-Adresse oder Hostname des Servers, auf dem ShoppingSync laeuft |
| `external_port` | Port des externen ShoppingSync-Dienstes, Standard `8095` |
| `api_base_path` | API-Basispfad, Standard `/api/v1` |
| `api_token` | Token fuer geschuetzte API-Aufrufe |
| `request_timeout_seconds` | Timeout fuer API-Abfragen |

## API-Standard

Der externe Dienst bietet mindestens diese Endpunkte an:

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

## Bedienung

Die Ingress-Seite ruft die API des externen Dienstes ueber die Add-on-Optionen auf. Schreibende und kritische Endpunkte benoetigen den API-Token, sofern im externen Dienst `admin.api_token` gesetzt ist.

Secrets werden vom externen Dienst maskiert. Wenn ein maskierter Wert `***` unveraendert zurueckgespeichert wird, bleibt der echte Wert in der lokalen Konfiguration erhalten.

`restart` und `shutdown` beenden den externen Prozess kontrolliert. Ob der Dienst danach wieder startet, haengt vom Dienstmanager auf dem externen Server ab, zum Beispiel NSSM.

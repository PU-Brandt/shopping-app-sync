# ShoppingSync Control

Dieses Add-on stellt eine Home-Assistant-Oberflaeche fuer einen extern laufenden ShoppingSync-Dienst bereit.

## Voraussetzungen

- Der externe ShoppingSync-Dienst laeuft auf einem Server im lokalen Netzwerk.
- Der Dienst stellt die standardisierte API unter `/api/v1` bereit.
- Host/IP, Port und API-Token werden in den Add-on-Optionen gesetzt.
- Der API-Token kann fuer die Ersteinrichtung leer bleiben. Sobald im externen Dienst `admin.api_token` gesetzt ist, muss derselbe Token im Add-on eingetragen werden.

## Standardwerte

- Standardport des externen Dienstes: `8095`
- API-Basispfad: `/api/v1`
- Home-Assistant-Seitenleiste: `ShoppingSync`

## Funktionen

- Verbindungstest ueber `/api/v1/health`
- Manifest- und Statusanzeige
- Konfiguration lesen und speichern
- Aktionen `sync_now`, `reload`, `restart`, `shutdown`
- Anzeige der letzten Logzeilen

Die fachliche Synchronisation laeuft weiterhin im externen Python-Dienst.

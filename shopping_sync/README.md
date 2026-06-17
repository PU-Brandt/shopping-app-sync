# ShoppingSync Control

Dieses Add-on stellt eine Home-Assistant-Oberflaeche fuer einen extern laufenden ShoppingSync-Dienst bereit.

## Voraussetzungen

- Der externe ShoppingSync-Dienst laeuft auf einem Server im lokalen Netzwerk.
- Der Dienst stellt perspektivisch die standardisierte API unter `/api/v1` bereit.
- Host/IP, Port und API-Token werden in den Add-on-Optionen gesetzt.

## Standardwerte

- Standardport des externen Dienstes: `8095`
- API-Basispfad: `/api/v1`
- Home-Assistant-Seitenleiste: `ShoppingSync`

## Aktueller Stand

Dieses Add-on ist ein erstes Grundgeruest. Es startet eine Ingress-Seite in Home Assistant und kann die spaeteren Endpunkte `health` und `status` des externen Dienstes abfragen.

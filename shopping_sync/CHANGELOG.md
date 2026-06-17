# Changelog

## 0.2.6

- Alte Neustart-/Beenden-Rueckmeldungen werden ausgeblendet, sobald der Dienst wieder erreichbar ist.

## 0.2.5

- Live-Log-Aktualisieren durch `Log loeschen` ersetzt.
- API-Endpunkt zum Loeschen der Dienst- und Live-Logpuffer ergaenzt.
- Seitenleisten-Icon explizit als Material-Design-Icon deklariert.

## 0.2.4

- Live-Log bleibt automatisch an der letzten Zeile, solange nicht manuell hochgescrollt wurde.

## 0.2.3

- Add-on- und Dienstversion neben der Ueberschrift angezeigt.
- Betriebsart-Kachel und Umschalter fuer `Bei Bedarf` und `Echtzeit` ergaenzt.
- Timeout-Beschriftung als API-Antwortzeit verdeutlicht.

## 0.2.2

- Statusuebersicht mit Kacheln wie in der urspruenglichen Admin-Seite ergaenzt.
- Live-Monitor, Sync-Zustand, Verbindungen, Listen und Fehler direkt sichtbar gemacht.

## 0.2.1

- `/api/v1/logs/recent` zeigt jetzt auch die Home-Assistant-Live-Events.
- Add-on-Live-Logs werden alle zwei Sekunden aktualisiert.
- Einkaufswagen-Icon fuer Seitenleiste und Add-on-Anzeige nachgezogen.

## 0.2.0

- Add-on-Oberflaeche auf den standardisierten `/api/v1`-Dienst umgestellt.
- Manifest, Health, Status, Konfiguration, Aktionen und Recent Logs angebunden.
- Kritische Aktionen bleiben durch den externen API-Token geschuetzt.

## 0.1.0

- Erstes Add-on-Grundgeruest fuer ShoppingSync Control.
- Ingress-Seite mit Verbindungstest und Statusabfrage vorbereitet.
- Add-on-Optionen fuer Host, Port, API-Basispfad und Token angelegt.

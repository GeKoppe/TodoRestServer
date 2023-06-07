# Installation Webserver
1. apt update
2. apt install apache2

# Installation Rest Api auf Betriebssystem
1. Ordner machen
2. Repo klonen
3. Pip install den ganzen library quatsch

# Konfiguration Netzwerk
1. /etc/dhcpcd.conf Datei anpassen
   1. Statische IP 192.168.24.113 eintragen
2. Firewall konfigurieren
   1. Full Upgrade des APT
   2. UFW Installieren
   3. SSH Port freigeben
   4. UFW enable
   5. SSH nur aus eigenem Netzwerk erlauben
   6. alte ssh regeln löschen
   7. Deny all incoming

# Konfiguration User
1. benutzer72 User mit Passwort "elo123" hinzugefügt
2. fernzugriff User mit Passwort "helloelo123" hinzugefügt
3. In /etc/ssh/sshd_config Fernzugriff unter AllowUsers hinzugefügt
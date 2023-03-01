# Warning-Messenger-Bot
Bachelorpraktikum Projekt

## Beschreibung
Dies ist ein Telegram-Bot, der Bevölkerungswarnungen über die NINA API abrufen und über die Telegram API vermitteln kann. 
Die Warnungen sind den Kategorien Hochwasser, Wetter und Bevölkerungsschutz  zugeordnet und Standort- und Risikostufen-abhängig verarbeitet. Nutzer:innen können per Abfrage aktuelle Warnungen erhalten oder Abonnements hinzufügen, um per Push-Benachrichtigung über Gefahren informiert zu werden. 
Außerdem kann man bei Bedarf Corona-Informationen über einen Standort abfragen.
Darüber hinaus können Informationen zu Verhaltenshinweisen in Notfällen abgerufen werden. Die nutzerbezogenen Daten, welche der Bot speichert, können jederzeit gelöscht werden.
Der Bot wird über Texteingaben und Buttons im Telegram-Chat gesteuert und antwortet Nutzer:innen über selbigen Chat.

Das Projekt wurde im Auftrag von PEASEC erstellt, um einen Warning Messenger Bot als konkretes Beispiel für die Forschung, also z.B. Umfragen (aktuell z.B. um sich ein Bild zu machen, ob die Bevölkerung einen Warn-Bot nutzen würde bzw. er eine gute Alternative zu den Warn-Apps darstellt), zu haben.

## Installation
???
Packages:
-"pyTelegramBotAPI"
-"python-decouple"

## Erster Start
1. bot_runner.py Datei ausführen
Befehl: nohup python3 bot_runner.py
2. Den Bot über Telegram suchen und auf den “Start” Knopf drücken 
→ der Bot schickt direkt eine Nachricht zur Einleitung des Chats

## Konfigurationsoptionen
- token
- text_templates.json

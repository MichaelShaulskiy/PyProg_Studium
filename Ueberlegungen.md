# Wie ist eine Nachrichtenseite Aufgebaut
Sie hat eine Frontpage, meist mit tickern.
Oftmals ist ein Artikel groß vorgehoben
Oftmals bei großen Nachrichten ändert sich das Layout ein wenig
Es gibt oftmals eine Schlagzeilen sektion die das laut redaktion wichtigste/größte erfasst
Wenn man scrollt sieht man meist eine Liste von Artikeln mit vorschaubild usw...

=> Hauptseite ist mehr oder weniger ne liste von Artikeln

# Wie kommen wir an eine Liste der artikel
Wenns angeboten wird: rss feed (präferiert)
Wenn nicht: HTML parsing mit beautifulsoup (Scraping, nicht gern gesehen)

# Was hat ein Artikel?
- In welchem Blatt er erschienen ist
- Titel
- Author
- Rubrik
- Timestamp
- Vielleicht auch Lesedauer
- Text
- Grafiken
- Braucht man ein Abo Ja/Nein

Darauf muss die Datenbank aufbauen

# Wahl der Datenbank
Wir könnten git als eine Datenbank für artikel verwenden
Vorteil:
- Gut diffbar
Nachteil:
- Schwer querybar

# Wie geben wir die Zusammenfassungen aus?
- Terminal (unschön)
- PySide2 Qt GUI
- Webinterface (HTML/CSS/react etc...)

# UPDATE
Nach unserem Treffen
- GUI wird Qt
- 4 Nachrichtenquellen
- Nutzung von RSS

Architektonisch ist das alles grad ein wenig wirr.
Grober Überblick:
Wir haben eine Datenbank, um die herum ist alles gebaut
Befüllt wird sie mithilfe des util packages auf eine clevere art (Wenn sie befüllt werden muss dank dem Decorator)
Die links zum befüllen kriegen wir über die RSS Feeds die in der NewsSources Tabelle hinterlegt sind

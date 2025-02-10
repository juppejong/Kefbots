Kef-bot Kraken Trading Bot
Deze Django-webapplicatie maakt het mogelijk om automatisch te handelen op de Kraken exchange. Gebruikers kunnen hun API-sleutels invoeren, handelstrategieën selecteren en hun handelsgeschiedenis bekijken. De bot ondersteunt strategieën zoals RSI en Moving Average Crossover en biedt live grafieken om marktanalyses visueel weer te geven.

📌 Functies
Dashboard: Bekijk accountbalans en recente trades.
Automatische Handel: Stel strategieën en parameters in voor automatische koop- en verkoopacties.
Handelsgeschiedenis: Bekijk een overzicht van je eerdere trades.
Grafieken: Visualisatie van marktgegevens zoals RSI en MA Crossover met behulp van Plotly.
Gebruikersbeheer: Registratie, inloggen, en beveiligde gebruikerssessies.
Logboek: Gedetailleerde logs van alle handelsacties en signalen.
🛠️ Installatie
Vereisten
Python 3.x
Django
pandas
numpy
plotly
krakenex
Installatie-instructies
Kloon de repository:

bash
Kopiëren
Bewerken
git clone https://github.com/yourusername/kraken-trading-bot.git
cd kraken-trading-bot
Maak een virtuele omgeving en installeer vereisten:

bash
Kopiëren
Bewerken
python -m venv venv
source venv/bin/activate  # Voor Windows: venv\Scripts\activate
pip install -r requirements.txt
Voer de migraties uit:

bash
Kopiëren
Bewerken
python manage.py migrate
Start de server:

bash
Kopiëren
Bewerken
python manage.py runserver
Ga naar de applicatie: Open http://127.0.0.1:8000 in je browser.

🔑 Configuratie
API-sleutels instellen:

Ga naar het Dashboard na het inloggen.
Voer je Kraken API Key en Secret in.
Stel de gewenste handelsinstellingen in, zoals het handelspaar (bijv. SOLUSD) en volume.
Automatische handelsstrategie kiezen:

Ga naar de AutoTrade Settings.
Kies een strategie zoals RSI of Moving Average Crossover.
Pas de parameters aan, zoals RSI-drempels of SMA-periodes.
📈 Ondersteunde Strategieën
RSI (Relative Strength Index):

Koop wanneer RSI onder de ingestelde drempel komt.
Verkoop wanneer RSI boven de drempel komt.
Moving Average Crossover:

Koop wanneer de korte termijn gemiddelde (SMA Short) de lange termijn gemiddelde (SMA Long) van onder kruist.
Verkoop wanneer de korte termijn gemiddelde de lange termijn gemiddelde van boven kruist.
Bollinger Bands (toekomstige ondersteuning):

Dynamische koop- en verkoopsignalen gebaseerd op volatiliteit.
⚙️ Belangrijke Bestanden
views.py: Bevat de logica voor de weergave van de dashboard, instellingen, strategieën en autotrade functies.
kraken_client.py: Beheer van communicatie met de Kraken API.
models.py: Definieert de database modellen voor API-instellingen, autotrade-configuraties en handelslogs.
forms.py: Formulieren voor gebruikersinvoer, zoals autotrade-instellingen.
strategys.py: Bevat de implementatie van handelsstrategieën zoals RSI.
🚀 Automatisch Handelen Starten
Ga naar de AutoTrade pagina.
Stel je strategieën en instellingen in.
Klik op Start AutoTrade om de bot te starten.
De bot draait in een achtergrondproces en logt alle activiteiten.
Stoppen? Klik simpelweg op Stop AutoTrade.

📝 Bijdragen
Wil je bijdragen aan dit project? Volg dan deze stappen:

Fork het project.
Maak een nieuwe branch: git checkout -b feature/jouw-feature.
Voeg je wijzigingen toe en commit: git commit -m 'Voeg nieuwe feature toe'.
Push naar de branch: git push origin feature/jouw-feature.
Maak een pull request.
🛡️ Disclaimer
Deze applicatie is bedoeld voor educatieve doeleinden. Handelen in cryptocurrencies brengt risico’s met zich mee. Gebruik deze software op eigen risico en test grondig in een veilige omgeving voordat je live handelt.

📧 Contact
Voor vragen of suggesties, neem contact op via [your-email@example.com].
from django.shortcuts import render, redirect
from .models import APISettings, AutoTradeSettings, TradeLog
from .kraken_client import KrakenClient
from django.contrib.auth.decorators import login_required
import threading
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import krakenex
from django.contrib.auth import logout
from django.contrib import messages
from .forms import AutoTradeSettingsForm
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime  # Import voor tijdconversie
from .strategys import calculate_rsi

bot_thread = None  # Globale variabele om de bot-status bij te houden
bot_running = False

from django.contrib.auth.decorators import login_required
from .kraken_client import KrakenClient  # Zorg ervoor dat deze import klopt
from .models import APISettings, TradeLog

def logout_view(request):
    logout(request)  # Logt de gebruiker uit
    return render(request, 'bot/home.html')

def custom_logout_view(request):
    # Dit logout de gebruiker expliciet en redirect naar de homepagina
    from django.contrib.auth import logout
    logout(request)
    return render(request, 'bot/home.html')

@login_required
def dashboard(request):
    settings, created = APISettings.objects.get_or_create(user=request.user)
    error = None
    balance = {}
    trades = []

    # Verwerk API sleutels
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        api_secret = request.POST.get('api_secret')

        if api_key and api_secret:
            settings.api_key = api_key
            settings.api_secret = api_secret
            settings.pair = request.POST.get('pair', 'SOLUSD')
            settings.volume = request.POST.get('volume', 1.0)
            settings.save()
        else:
            error = "API Key en API Secret mogen niet leeg zijn."

    # Kraken API aanroepen
    if settings.api_key and settings.api_secret:
        try:
            client = KrakenClient(settings.api_key, settings.api_secret)
            balance = client.get_balance()

            # Haal de laatste 5 trades op van Kraken
            raw_trades = client.get_trade_history()

            # Converteer UNIX-tijd naar leesbare datum
            trades = []
            for trade_id, trade in raw_trades.items():
                trade['readable_time'] = datetime.fromtimestamp(trade['time']).strftime('%Y-%m-%d %H:%M:%S')
                trades.append(trade)

            # Sorteer de trades op tijd (nieuwste eerst) en neem de laatste 10
            trades = sorted(trades, key=lambda x: x['time'], reverse=True)[:15]
        except Exception as e:
            error = f"Fout bij ophalen van balans of trades: {str(e)}"
    else:
        error = error or "Voer eerst je API Key en Secret in."

    # Bepaal de bot status
    is_running = bot_running

    return render(request, 'bot/dashboard.html', {
        'settings': settings,
        'balance': balance,
        'error': error,
        'trades': trades,
        'is_running': is_running,
    })

@login_required
def settings_view(request):
    settings, _ = AutoTradeSettings.objects.get_or_create(user=request.user)
    error = None

    if request.method == 'POST':
        try:
            # Verkrijg de formuliergegevens van de POST
            settings.api_key = request.POST.get('api_key')
            settings.api_secret = request.POST.get('api_secret')
            settings.notification_preference = request.POST.get('notification_preference')
            settings.exchange = request.POST.get('exchange')
            settings.volume = float(request.POST.get('volume', 1.0))
            settings.pair = request.POST.get('pair')
            settings.strategy = request.POST.get('strategy')
            settings.candle_period = int(request.POST.get('candle_period', 1))
            settings.buy_margin = float(request.POST.get('buy_margin', 0.0))
            settings.sell_margin = float(request.POST.get('sell_margin', 0.0))

            settings.save()
            messages.success(request, 'Instellingen zijn succesvol opgeslagen!')
            return redirect('settings')  # Redirect naar de instellingenpagina om dubbele POSTs te voorkomen
        except Exception as e:
            error = f"Fout bij het opslaan van instellingen: {str(e)}"
            messages.error(request, error)

    return render(request, 'bot/settings.html', {'settings': settings, 'error': error})


@login_required
def history_view(request):
    settings, created = APISettings.objects.get_or_create(user=request.user)
    trades = []
    error = None

    if settings.api_key and settings.api_secret:
        try:
            client = KrakenClient(settings.api_key, settings.api_secret)
            raw_trades = client.get_trade_history()

            # Converteer UNIX-tijd naar leesbare datum
            trades = []
            for trade_id, trade in raw_trades.items():
                trade['readable_time'] = datetime.fromtimestamp(trade['time']).strftime('%Y-%m-%d %H:%M:%S')
                trades.append(trade)

            # Sorteer de trades op tijd (nieuwste eerst) en neem de laatste 10
            trades = sorted(trades, key=lambda x: x['time'], reverse=True)[:15]
                
        except Exception as e:
            error = f"Fout bij ophalen van trades: {str(e)}"
    else:
        error = "Voer eerst je API Key en Secret in via het Dashboard."

    return render(request, 'bot/history.html', {'trades': trades, 'error': error})

def home_view(request):
    return render(request, 'bot/home.html')

@login_required
def strategies_view(request):
    if request.method == 'POST':
        selected_strategy = request.POST.get('strategy')
        # Hier sla je de strategie op
    return render(request, 'bot/strategies.html')

@login_required
def autotrade_view(request):
    # Haal de instellingen op voor de gebruiker (maakt ze aan als ze nog niet bestaan)
    settings, created = AutoTradeSettings.objects.get_or_create(user=request.user)
    
    # Formulierverwerking
    if request.method == 'POST':
        form = AutoTradeSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instellingen zijn succesvol opgeslagen!')
            return redirect('autotrade_settings')  # Zorg ervoor dat dit de juiste naam is van je URL.
        else:
            messages.error(request, 'Er is een fout opgetreden bij het opslaan van de instellingen.')
    
    else:
        form = AutoTradeSettingsForm(instance=settings)

    # Trade log gegevens
    logs = TradeLog.objects.filter(user=request.user).order_by('-timestamp')[:10]

    try:
        # API instellingen voor Kraken
        api_settings = APISettings.objects.get(user=request.user)
        api_key = api_settings.api_key
        api_secret = api_settings.api_secret
    except APISettings.DoesNotExist:
        api_key = None
        api_secret = None

    # Kraken API om gegevens op te halen
    api = krakenex.API(api_key, api_secret)
    response = api.query_public('OHLC', {'pair': settings.pair, 'interval': 1, 'count': 200})  # Haal 200 candles op
    ohlc_data = response['result'][list(response['result'].keys())[0]]

    # DataFrame maken van de OHLC-gegevens
    df = pd.DataFrame(ohlc_data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['close'] = pd.to_numeric(df['close'])

    # Bereken de RSI
    rsi = calculate_rsi(df['close'])

    # Verwijder NaN-waarden uit de RSI voordat we deze gebruiken voor de grafiek
    rsi_cleaned = rsi.dropna()

    # Plotly: maak de RSI-grafiek
    fig = go.Figure()

    # Voeg RSI-lijn toe
    fig.add_trace(go.Scatter(x=df['time'][:len(rsi_cleaned)], y=rsi_cleaned, mode='lines', name='RSI'))

    # Voeg een lijn voor de overgekochte (70) en oververkochte (30) niveaus toe
    fig.add_trace(go.Scatter(x=df['time'][:len(rsi_cleaned)], y=[70]*len(rsi_cleaned), mode='lines', name='Overgekocht (70)', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df['time'][:len(rsi_cleaned)], y=[30]*len(rsi_cleaned), mode='lines', name='Oververkocht (30)', line=dict(dash='dash')))

    # Opmaak van de grafiek
    # Opmaak van de grafiek met aangepaste marges
    fig.update_layout(
        title="RSI Visualisatie",
        xaxis_title="Tijd",
        yaxis_title="RSI",
        template="plotly_dark",
        margin=dict(l=50, r=50, t=50, b=50),  # Stel marges in
        height=250,  # Stel de hoogte van de grafiek in als dat nodig is
    )

    

    # Converteer de grafiek naar HTML
    graph_html = fig.to_html(full_html=False)

        # Toon de status van de bot (bijvoorbeeld: running or stopped)
    is_running = bot_running  # Zorg ervoor dat bot_running goed is ingesteld

    # Stuur de grafiek, instellingen en formulier naar de template
    return render(request, 'bot/autotrade.html', {
        'settings': settings,
        'logs': logs,
        'is_running': is_running,  # Dit kan verder worden aangepast afhankelijk van je bot-status
        'graph_html': graph_html,
        'form': form,  # Voeg het formulier toe aan de context
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Je account is succesvol aangemaakt! Je kunt nu inloggen.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def start_autotrade(request):
    global bot_thread, bot_running

    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=run_bot, args=(request.user,))
        bot_thread.start()

    return redirect('autotrade')

@login_required
def stop_autotrade(request):
    global bot_running
    bot_running = False
    return redirect('autotrade')

def run_bot(user):
    settings = AutoTradeSettings.objects.get(user=user)
    api_settings = user.apisettings
    api = krakenex.API(api_settings.api_key, api_settings.api_secret)

    trigger_price_buy = None
    trigger_price_sell = None
    buy_triggered = False
    sell_triggered = False
    last_trade_action = None

    while True:
        try:
            # Haal OHLC-gegevens op
            response = api.query_public('OHLC', {'pair': settings.pair, 'interval': 1})
            ohlc_data = response['result'][list(response['result'].keys())[0]]
            df = pd.DataFrame(ohlc_data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            df['close'] = pd.to_numeric(df['close'])
            current_price = df['close'].iloc[-1]
            rsi = calculate_rsi(df['close'])
            last_rsi = round(rsi.iloc[-1], 0)

            log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Logging van marktstatus
            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Marktupdate - Prijs: {current_price:.2f}, RSI: {last_rsi}")

            if not buy_triggered and not sell_triggered:
                signal = get_trade_signal(settings.strategy, df, user)
                TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Wachten op signaal... (Prijs: {current_price:.2f}, RSI: {last_rsi})")

                if signal == 'buy' and last_trade_action != 'buy':
                    buy_triggered = True
                    trigger_price_buy = current_price
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Koopsignaal ontvangen. Triggerprijs ingesteld op {trigger_price_buy:.2f}")

                elif signal == 'sell' and last_trade_action != 'sell':
                    sell_triggered = True
                    trigger_price_sell = current_price
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Verkoopsignaal ontvangen. Triggerprijs ingesteld op {trigger_price_sell:.2f}")

            # Kooplogica
            if buy_triggered:
                if current_price < trigger_price_buy:
                    trigger_price_buy = current_price
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Prijs gedaald, nieuwe triggerprijs (koop): {trigger_price_buy:.2f}")

                elif current_price >= trigger_price_buy * 1.001:
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Prijs gestegen met 0.1% boven de triggerprijs. Kooporder wordt geplaatst.")
                    try:
                        response = api.query_private('AddOrder', {
                            'pair': settings.pair,
                            'type': 'buy',
                            'ordertype': 'market',
                            'volume': settings.volume,
                        })
                        if response['error']:
                            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] ERROR: Fout bij kooporder: {response['error']}")
                        else:
                            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] SUCCESS: Kooporder succesvol uitgevoerd!")
                        
                        buy_triggered = False
                        trigger_price_buy = None
                        last_trade_action = 'buy'
                        TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Wacht op verkoopsignaal.")
                    except Exception as e:
                        TradeLog.objects.create(user=user, message=f"[{log_timestamp}] ERROR: API Fout bij kooporder: {str(e)}")
                        buy_triggered = False
                        trigger_price_buy = None

            # Verkooplogica
            if sell_triggered:
                if current_price > trigger_price_sell:
                    trigger_price_sell = current_price
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Prijs gestegen, nieuwe triggerprijs (verkoop): {trigger_price_sell:.2f}")

                elif current_price <= trigger_price_sell * 0.999:
                    TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Prijs gedaald met 0.1% onder de triggerprijs. Verkooporder wordt geplaatst.")
                    try:
                        response = api.query_private('AddOrder', {
                            'pair': settings.pair,
                            'type': 'sell',
                            'ordertype': 'market',
                            'volume': settings.volume,
                        })
                        if response['error']:
                            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] ERROR: Fout bij verkooporder: {response['error']}")
                        else:
                            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] SUCCESS: Verkooporder succesvol uitgevoerd!")
                        
                        sell_triggered = False
                        trigger_price_sell = None
                        last_trade_action = 'sell'
                        TradeLog.objects.create(user=user, message=f"[{log_timestamp}] INFO: Wacht op koopsignaal.")
                    except Exception as e:
                        TradeLog.objects.create(user=user, message=f"[{log_timestamp}] ERROR: API Fout bij verkooporder: {str(e)}")
                        sell_triggered = False
                        trigger_price_sell = None

        except Exception as e:
            TradeLog.objects.create(user=user, message=f"[{log_timestamp}] CRITICAL: Fout tijdens trading: {str(e)}")
            buy_triggered = False
            sell_triggered = False
            trigger_price_buy = None
            trigger_price_sell = None

        time.sleep(settings.interval)  # Interval tussen checks


def get_trade_signal(strategy, df, user):
    settings = AutoTradeSettings.objects.get(user=user)  # Haal de instellingen van de gebruiker op

    if strategy == 'RSI':
        rsi = calculate_rsi(df['close'])
        last_rsi = round(rsi.iloc[-1], 0)

        # Gebruik de ingestelde drempels
        if last_rsi < settings.rsi_buy_threshold:
            return 'buy'
        elif last_rsi > settings.rsi_sell_threshold:
            return 'sell'
    
    elif strategy == 'MA_Crossover':
        # Gebruik de door de gebruiker ingestelde periodes voor de MA
        short_period = settings.sma_short_period  # Korte MA-periode (bijvoorbeeld 50)
        long_period = settings.sma_long_period  # Lange MA-periode (bijvoorbeeld 200)

        # Bereken de moving averages
        df['SMA_short'] = df['close'].rolling(window=short_period).mean()
        df['SMA_long'] = df['close'].rolling(window=long_period).mean()

        # Detecteer het crossover-punt
        last_sma_short = df['SMA_short'].iloc[-1]
        last_sma_long = df['SMA_long'].iloc[-1]
        previous_sma_short = df['SMA_short'].iloc[-2]
        previous_sma_long = df['SMA_long'].iloc[-2]

        # Koop Signaal: wanneer de korte MA de lange MA van onder naar boven kruist
        if previous_sma_short < previous_sma_long and last_sma_short > last_sma_long:
            return 'buy'
        # Verkoop Signaal: wanneer de korte MA de lange MA van boven naar beneden kruist
        elif previous_sma_short > previous_sma_long and last_sma_short < last_sma_long:
            return 'sell'
    
    elif strategy == 'Bollinger':
        pass  # Andere strategieën
    
    return None



@login_required
def get_ma_crossover_graph(request):
    # Verkrijg instellingen van de gebruiker
    settings = AutoTradeSettings.objects.get(user=request.user)
    api_settings = APISettings.objects.get(user=request.user)
    api = krakenex.API(api_settings.api_key, api_settings.api_secret)

    # Haal de OHLC data op van de API (Kraken)
    response = api.query_public('OHLC', {'pair': settings.pair, 'interval': 1})
    if not response['result']:
        return JsonResponse({'error': 'Geen data ontvangen van API'}, status=500)

    ohlc_key = [key for key in response['result'].keys() if key != 'last'][0]
    ohlc_data = response['result'][ohlc_key]

    # Zet de data om naar een DataFrame
    df = pd.DataFrame(ohlc_data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    # Bereken de Moving Averages
    short_ma_period = 50
    long_ma_period = 200
    df['short_ma'] = df['close'].rolling(window=short_ma_period).mean()
    df['long_ma'] = df['close'].rolling(window=long_ma_period).mean()

    # Selecteer alleen de laatste 300 datapunten om te sturen naar de frontend
    df = df.tail(300)

    # Voorbereiden van de data om naar de frontend te sturen
    labels = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    close_prices = df['close'].ffill().tolist()  # Vul ontbrekende waarden in met forward fill
    short_ma = df['short_ma'].ffill().tolist()
    long_ma = df['long_ma'].ffill().tolist()

    return JsonResponse({
        'labels': labels,
        'prices': close_prices,
        'short_ma': short_ma,
        'long_ma': long_ma
    })


def get_historical_data():
    # Haal de historische data op via een API of een andere bron
    # Voorbeeld: Stel dat je gegevens ophaalt via een API:
    # api_response = get_api_data()
    # Verwerk de API data in een formaat dat geschikt is voor de DataFrame

    # Hier is een voorbeeld van wat een API-antwoord zou kunnen zijn
    data = [
        {'timestamp': '2025-02-01 00:00:00', 'open': 150, 'high': 155, 'low': 148, 'close': 152},
        {'timestamp': '2025-02-01 01:00:00', 'open': 152, 'high': 157, 'low': 151, 'close': 154},
        # Voeg meer datapoints toe
    ]
    
    return data


@login_required
def get_rsi_graph(request):
    # Haal de instellingen op voor de gebruiker
    settings = AutoTradeSettings.objects.get(user=request.user)
    api_settings = APISettings.objects.get(user=request.user)
    api = krakenex.API(api_settings.api_key, api_settings.api_secret)

    # Haal OHLC-data op van Kraken
    response = api.query_public('OHLC', {'pair': settings.pair, 'interval': 1})
    if not response['result']:
        return JsonResponse({'error': 'Geen data ontvangen van API'}, status=500)

    ohlc_key = [key for key in response['result'].keys() if key != 'last'][0]
    ohlc_data = response['result'][ohlc_key]

    # Zet data om naar DataFrame
    df = pd.DataFrame(ohlc_data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    # Bereken de RSI
    df['rsi'] = calculate_rsi(df['close']).fillna(0)

    # Selecteer de laatste 300 datapunten
    df = df.tail(300)

    # Voorbereiden van data om naar de frontend te sturen
    labels = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    rsi_values = df['rsi'].tolist()
    overbought = [70] * len(rsi_values)
    oversold = [30] * len(rsi_values)

    # Stuur data als JSON naar de frontend
    return JsonResponse({
        'labels': labels,
        'values': rsi_values,  # Gebruik 'values' in plaats van 'rsi'
        'overbought': overbought,
        'oversold': oversold
    })




def get_logs(request):
    logs = TradeLog.objects.filter(user=request.user).order_by('-timestamp')[:30]
    log_data = [{'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'message': log.message} for log in logs]
    
    return JsonResponse({'logs': log_data})

def about_view(request):
    return render(request, 'bot/about.html')





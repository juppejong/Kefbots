import pandas as pd
import numpy as np


def calculate_moving_average(data, short_window=50, long_window=200):
    # Bereken de korte en lange Moving Averages
    data['SMA50'] = data['Close'].rolling(window=short_window).mean()
    data['SMA200'] = data['Close'].rolling(window=long_window).mean()

    return data

def detect_crossovers(data):
    # Koop Signaal: wanneer de SMA50 de SMA200 van onder naar boven kruist
    data['Signal'] = 0  # Default is geen signaal
    data.loc[data['SMA50'] > data['SMA200'], 'Signal'] = 1  # Koop signaal (1 = koop)
    data.loc[data['SMA50'] < data['SMA200'], 'Signal'] = -1  # Verkoop signaal (-1 = verkoop)
    
    # We moeten het punt van de crossover vinden, dus we kunnen de verandering in 'Signal' detecteren
    data['Crossover'] = data['Signal'].diff()
    
    return data

def moving_average_crossover_strategy(data):
    # Bereken de Moving Averages
    data = calculate_moving_average(data)

    # Detecteer de crossovers
    data = detect_crossovers(data)
    
    # Genereer een koop/verkoop signaal
    buy_signals = data[data['Crossover'] == 1]
    sell_signals = data[data['Crossover'] == -1]
    
    return buy_signals, sell_signals




def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Gebruik Wilder's smoothing
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Functie voor het berekenen van de SMA's
def calculate_sma(data, short_window=50, long_window=200):
    data['SMA50'] = data['Close'].rolling(window=short_window).mean()
    data['SMA200'] = data['Close'].rolling(window=long_window).mean()
    return data



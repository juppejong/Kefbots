from django.db import models
from django.contrib.auth.models import User

class APISettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=100, blank=True, null=True)
    api_secret = models.CharField(max_length=100, blank=True, null=True)
    pair = models.CharField(max_length=10, default='SOLUSD')
    volume = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    strategy = models.CharField(max_length=50, default='simple_moving_average')  # Voor toekomstig gebruik

    def __str__(self):
        return f'{self.user.username} - {self.pair}'

class AutoTradeSettings(models.Model):
    STRATEGY_CHOICES = [
        ('RSI', 'RSI Strategie'),
        ('MA_Crossover', 'Moving Average Crossover'),
        ('Bollinger', 'Bollinger Bands'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=50, default='Kraken')
    pair = models.CharField(max_length=10, default='SOLUSD')
    volume = models.FloatField(default=1.0)
    interval = models.IntegerField(default=60)
    candle_period = models.CharField(max_length=5, default='1m')
    strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, default='RSI')

    # Nieuwe instellingen
    buy_margin = models.FloatField(default=0.0, verbose_name="Buy Margin")
    sell_margin = models.FloatField(default=0.0, verbose_name="Sell Margin")

    # RSI Instellingen
    rsi_buy_threshold = models.IntegerField(default=30, verbose_name='RSI Koopdrempel')
    rsi_sell_threshold = models.IntegerField(default=70, verbose_name='RSI Verkoopdrempel')

    # SMA Instellingen
    sma_short_period = models.IntegerField(default=50)  # Korte MA-periode
    sma_long_period = models.IntegerField(default=200)   # Lange MA-periode

    def __str__(self):
        return f"{self.user.username}'s AutoTrade Settings"




class TradeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    action = models.CharField(max_length=10, default='none')  # Voeg een default toe



    def __str__(self):
        return f"{self.timestamp}: {self.message[:50]}"




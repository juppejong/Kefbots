# bot/forms.py
from django import forms
from .models import AutoTradeSettings

class AutoTradeSettingsForm(forms.ModelForm):
    class Meta:
        model = AutoTradeSettings
        fields = ['exchange', 'pair', 'volume', 'interval', 'strategy', 'candle_period', 'rsi_buy_threshold', 'rsi_sell_threshold', 'sma_short_period', 'sma_long_period']
        widgets = {
            'rsi_buy_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'rsi_sell_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'sma_short_period': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'sma_long_period': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }


import krakenex
import time

class KrakenClient:
    def __init__(self, api_key, api_secret):
        self.api = krakenex.API(api_key, api_secret)
        self.last_nonce = int(time.time() * 1000)  # Initialiseer de nonce met de huidige tijd in milliseconden

    def get_nonce(self):
        self.last_nonce += 1
        return self.last_nonce

    def get_balance(self):
        nonce = self.get_nonce()
        response = self.api.query_private('Balance', {'nonce': nonce})
        return response['result'] if response['error'] == [] else response['error']

    def place_order(self, pair, type, ordertype, volume, price=None):
        data = {
            'pair': pair,
            'type': type,  # 'buy' of 'sell'
            'ordertype': ordertype,  # 'market' of 'limit'
            'volume': volume
        }
        if price:
            data['price'] = price
        response = self.api.query_private('AddOrder', data)
        return response['result'] if response['error'] == [] else response['error']
    
    def get_trade_history(self, start=None, end=None, ofs=None):
        """
        Haalt de tradegeschiedenis op van je Kraken-account.
        
        Parameters:
            start (int): Begin timestamp (optional).
            end (int): Eind timestamp (optional).
            ofs (int): Resultaat offset voor paginering (optional).
        
        Returns:
            dict: Bevat een lijst van trades of een foutmelding.
        """
        params = {}
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        if ofs:
            params['ofs'] = ofs

        nonce = self.get_nonce()
        params['nonce'] = nonce
        
        response = self.api.query_private('TradesHistory', params)
        return response['result']['trades'] if response['error'] == [] else response['error']

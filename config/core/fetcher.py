import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests

class AdvancedStockFetcher:
    def __init__(self, cache_duration=300):
        self.cache = {}
        self.cache_duration = cache_duration
        
    def get_stock_data(self, symbol, period="5d", interval="15m"):
        """Fetch stock data with caching"""
        cache_key = f"{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return data
        
        try:
            # Fetch from Yahoo Finance
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            # Add additional data
            data['Symbol'] = symbol
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            data['Gap_Up'] = (data['Open'] > data['Close'].shift(1) * 1.02)
            data['Gap_Down'] = (data['Open'] < data['Close'].shift(1) * 0.98)
            
            # Cache the data
            self.cache[cache_key] = (datetime.now(), data)
            
            return data
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols_list, **kwargs):
        """Fetch multiple stocks concurrently"""
        from concurrent.futures import ThreadPoolExecutor
        
        all_data = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.get_stock_data, symbol, **kwargs): symbol 
                for symbol in symbols_list
            }
            
            for future in future_to_symbol:
                symbol = future_to_symbol[future]
                try:
                    data = future.result(timeout=10)
                    if data is not None:
                        all_data[symbol] = data
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
        
        return all_data
    
    def get_market_sentiment(self):
        """Fetch market sentiment indicators"""
        try:
            # Nifty 50 data
            nifty = yf.download("^NSEI", period="1d", progress=False)
            
            # VIX India
            vix = yf.download("INDIAVIX.NS", period="1d", progress=False)
            
            # Market breadth
            advance_decline = self.get_advance_decline_ratio()
            
            sentiment = {
                'nifty_change': nifty['Close'].pct_change().iloc[-1] * 100 if not nifty.empty else 0,
                'vix': vix['Close'].iloc[-1] if not vix.empty else 0,
                'advance_decline': advance_decline,
                'timestamp': datetime.now()
            }
            
            return sentiment
            
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return None
    
    def get_advance_decline_ratio(self):
        """Calculate advance/decline ratio"""
        # This is a simplified version
        # In reality, you'd fetch NSE advance/decline data
        return 1.2  # Placeholder
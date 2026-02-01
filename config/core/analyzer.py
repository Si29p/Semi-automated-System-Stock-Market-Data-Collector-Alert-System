import pandas as pd
import numpy as np
import talib as ta
from typing import Dict, List, Tuple
import json

class MultiStrategyAnalyzer:
    def __init__(self, config_path="config/strategies.json"):
        self.strategies = self.load_strategies(config_path)
        
    def load_strategies(self, config_path):
        """Load strategy configurations"""
        default_strategies = {
            "momentum": {
                "indicators": ["RSI", "MACD", "Stochastic"],
                "buy_conditions": ["RSI < 35", "MACD_crossover_up"],
                "sell_conditions": ["RSI > 70", "MACD_crossover_down"],
                "weight": 0.3
            },
            "trend_following": {
                "indicators": ["EMA", "ADX", "ParabolicSAR"],
                "buy_conditions": ["EMA_20 > EMA_50", "ADX > 25"],
                "sell_conditions": ["EMA_20 < EMA_50"],
                "weight": 0.4
            },
            "mean_reversion": {
                "indicators": ["Bollinger", "RSI", "ATR"],
                "buy_conditions": ["Price < Bollinger_Lower", "RSI < 30"],
                "sell_conditions": ["Price > Bollinger_Upper", "RSI > 70"],
                "weight": 0.3
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return default_strategies
    
    def calculate_all_indicators(self, data):
        """Calculate all technical indicators"""
        if data is None or len(data) < 50:
            return None
        
        df = data.copy()
        
        # Price based indicators
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Momentum Indicators
        df['RSI'] = ta.RSI(df['Close'], timeperiod=14)
        df['Stoch_K'], df['Stoch_D'] = ta.STOCH(
            df['High'], df['Low'], df['Close'],
            fastk_period=14, slowk_period=3, slowd_period=3
        )
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = ta.MACD(
            df['Close'], fastperiod=12, slowperiod=26, signalperiod=9
        )
        
        # Trend Indicators
        df['EMA_9'] = ta.EMA(df['Close'], timeperiod=9)
        df['EMA_20'] = ta.EMA(df['Close'], timeperiod=20)
        df['EMA_50'] = ta.EMA(df['Close'], timeperiod=50)
        df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
        
        # Volatility Indicators
        df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = ta.BBANDS(
            df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2
        )
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # Volume Indicators
        df['OBV'] = ta.OBV(df['Close'], df['Volume'])
        df['MFI'] = ta.MFI(
            df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14
        )
        
        # Custom Indicators
        df['SuperTrend'] = self.calculate_supertrend(df)
        df['VWAP'] = self.calculate_vwap(df)
        df['Support'] = self.calculate_support_resistance(df)
        df['Resistance'] = self.calculate_support_resistance(df, mode='resistance')
        
        return df
    
    def calculate_supertrend(self, df, period=10, multiplier=3):
        """Calculate SuperTrend indicator"""
        hl2 = (df['High'] + df['Low']) / 2
        atr = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > upper_band.iloc[i-1]:
                direction.iloc[i] = 1
            elif df['Close'].iloc[i] < lower_band.iloc[i-1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i-1]
            
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
        
        return supertrend
    
    def calculate_vwap(self, df):
        """Calculate Volume Weighted Average Price"""
        vwap = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        return vwap
    
    def calculate_support_resistance(self, df, window=20, mode='support'):
        """Calculate support/resistance levels"""
        if mode == 'support':
            return df['Low'].rolling(window=window).min()
        else:
            return df['High'].rolling(window=window).max()
    
    def analyze_stock(self, symbol, data):
        """Complete analysis of a stock"""
        if data is None or len(data) < 20:
            return None
        
        # Calculate indicators
        analyzed_data = self.calculate_all_indicators(data)
        if analyzed_data is None:
            return None
        
        latest = analyzed_data.iloc[-1]
        previous = analyzed_data.iloc[-2]
        
        # Generate signals from each strategy
        signals = []
        confidence_scores = []
        
        for strategy_name, strategy_config in self.strategies.items():
            signal, confidence = self.apply_strategy(
                strategy_name, analyzed_data, strategy_config
            )
            signals.append(signal)
            confidence_scores.append(confidence)
        
        # Weighted decision
        final_signal = self.weighted_decision(signals, confidence_scores)
        
        # Risk assessment
        risk_score = self.calculate_risk(analyzed_data)
        
        # Entry/Exit levels
        entry, stop_loss, target = self.calculate_levels(analyzed_data, final_signal)
        
        result = {
            'symbol': symbol,
            'signal': final_signal,
            'confidence': np.mean(confidence_scores),
            'risk_score': risk_score,
            'current_price': latest['Close'],
            'entry': entry,
            'stop_loss': stop_loss,
            'target': target,
            'timestamp': datetime.now(),
            'details': {
                'strategies': dict(zip(self.strategies.keys(), signals)),
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'volume': latest['Volume'],
                'vwap': latest['VWAP']
            }
        }
        
        return result
    
    def apply_strategy(self, strategy_name, data, config):
        """Apply specific trading strategy"""
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        buy_score = 0
        sell_score = 0
        total_conditions = 0
        
        # Check buy conditions
        for condition in config.get('buy_conditions', []):
            if self.evaluate_condition(condition, latest, previous):
                buy_score += 1
            total_conditions += 1
        
        # Check sell conditions
        for condition in config.get('sell_conditions', []):
            if self.evaluate_condition(condition, latest, previous):
                sell_score += 1
            total_conditions += 1
        
        if total_conditions == 0:
            return 'HOLD', 0.5
        
        buy_ratio = buy_score / len(config.get('buy_conditions', [1]))
        sell_ratio = sell_score / len(config.get('sell_conditions', [1]))
        
        if buy_ratio > 0.6 and buy_ratio > sell_ratio:
            return 'BUY', buy_ratio
        elif sell_ratio > 0.6 and sell_ratio > buy_ratio:
            return 'SELL', sell_ratio
        else:
            return 'HOLD', max(buy_ratio, sell_ratio)
    
    def evaluate_condition(self, condition, latest, previous):
        """Evaluate a condition string"""
        try:
            # Simple condition evaluation
            if 'RSI' in condition:
                if '<' in condition:
                    value = float(condition.split('<')[1].strip())
                    return latest['RSI'] < value
                elif '>' in condition:
                    value = float(condition.split('>')[1].strip())
                    return latest['RSI'] > value
            
            elif 'MACD' in condition:
                if 'crossover_up' in condition:
                    return latest['MACD'] > latest['MACD_Signal'] and previous['MACD'] <= previous['MACD_Signal']
                elif 'crossover_down' in condition:
                    return latest['MACD'] < latest['MACD_Signal'] and previous['MACD'] >= previous['MACD_Signal']
            
            elif 'EMA' in condition:
                parts = condition.split()
                if len(parts) == 3:
                    ema1 = latest[f"EMA_{parts[0].split('_')[1]}"]
                    ema2 = latest[f"EMA_{parts[2].split('_')[1]}"]
                    if parts[1] == '>':
                        return ema1 > ema2
                    elif parts[1] == '<':
                        return ema1 < ema2
            
            return False
            
        except:
            return False
    
    def weighted_decision(self, signals, confidences):
        """Make weighted decision based on multiple strategies"""
        from collections import Counter
        
        if not signals:
            return 'HOLD'
        
        # Weight votes by confidence
        weighted_votes = []
        for signal, confidence in zip(signals, confidences):
            weighted_votes.extend([signal] * int(confidence * 10))
        
        if not weighted_votes:
            return 'HOLD'
        
        # Count votes
        vote_count = Counter(weighted_votes)
        return vote_count.most_common(1)[0][0]
    
    def calculate_risk(self, data):
        """Calculate risk score (0-10, lower is better)"""
        if len(data) < 20:
            return 5
        
        latest = data.iloc[-1]
        
        risk_score = 0
        
        # Volatility risk
        volatility = data['Close'].pct_change().std() * 100
        risk_score += min(volatility / 2, 3)
        
        # RSI risk
        if latest['RSI'] > 70 or latest['RSI'] < 30:
            risk_score += 2
        
        # Volume risk
        if latest['Volume'] < data['Volume'].mean() * 0.5:
            risk_score += 1
        
        # ATR risk (high volatility)
        atr_pct = (latest['ATR'] / latest['Close']) * 100
        risk_score += min(atr_pct, 2)
        
        return min(risk_score, 10)
    
    def calculate_levels(self, data, signal):
        """Calculate entry, stop loss, and target levels"""
        latest = data.iloc[-1]
        atr = latest['ATR']
        
        if signal == 'BUY':
            entry = latest['Close'] * 1.002  # Slightly above current
            stop_loss = latest['Close'] - (atr * 1.5)
            target = latest['Close'] + (atr * 3)
        elif signal == 'SELL':
            entry = latest['Close'] * 0.998  # Slightly below current
            stop_loss = latest['Close'] + (atr * 1.5)
            target = latest['Close'] - (atr * 3)
        else:
            entry = stop_loss = target = latest['Close']
        
        return round(entry, 2), round(stop_loss, 2), round(target, 2)
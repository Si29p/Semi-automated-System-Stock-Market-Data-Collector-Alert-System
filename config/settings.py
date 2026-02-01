import os
from datetime import time
from dotenv import load_dotenv

load_dotenv()

# ============ API KEYS ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============ EMAIL SETTINGS ============
EMAIL_CONFIG = {
    'sender': os.getenv("EMAIL_SENDER", ""),
    'password': os.getenv("EMAIL_PASSWORD", ""),
    'receiver': os.getenv("EMAIL_RECEIVER", ""),
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

# ============ DATABASE ============
DATABASE_CONFIG = {
    'path': 'data/stocks.db',
    'tables': ['signals', 'portfolio', 'logs']
}

# ============ MARKET HOURS (IST) ============
MARKET_HOURS = {
    'open': time(9, 15),
    'close': time(15, 30),
    'holidays': [
        '2024-01-26', '2024-03-08', '2024-03-25',
        '2024-03-29', '2024-04-11', '2024-04-17',
        '2024-05-01', '2024-06-17', '2024-07-17',
        '2024-08-15', '2024-10-02', '2024-11-01',
        '2024-11-15', '2024-12-25'
    ]
}

# ============ STRATEGIES ============
STRATEGIES = {
    'intraday': {
        'enabled': True,
        'interval': '5m',
        'period': '1d',
        'indicators': ['RSI', 'MACD', 'VWAP', 'SuperTrend']
    },
    'swing': {
        'enabled': True,
        'interval': '1h',
        'period': '5d',
        'indicators': ['RSI', 'MACD', 'EMA', 'Bollinger']
    },
    'positional': {
        'enabled': True,
        'interval': '1d',
        'period': '1mo',
        'indicators': ['SMA', 'RSI', 'ADX', 'ATR']
    }
}

# ============ RISK MANAGEMENT ============
RISK_CONFIG = {
    'max_portfolio_risk': 2.0,  # 2% per trade
    'stop_loss_pct': 5.0,       # 5% stop loss
    'target_pct': 10.0,         # 10% target
    'max_open_positions': 5,
    'min_volume': 100000        # Minimum volume filter
}

# ============ ALERT SETTINGS ============
ALERT_CONFIG = {
    'email': True,
    'telegram': True,
    'sms': False,
    'webhook': False,
    'check_interval_minutes': 15
}
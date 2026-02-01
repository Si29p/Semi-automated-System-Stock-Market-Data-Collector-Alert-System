# Semi-automated-System-Stock-Market-Data-Collector-Alert-System
📌 Project Features  1. Daily stock data automatically fetch karega. 2. Technical indicators calculate karega. 3. Buy/Sell/Hold signals generate karega. 4. Email ya SMS alerts bhejega. 5. Excel/CSV mein reports banayega.
advanced_stock_system/
│
├── app.py                      # Main Flask application
├── bot.py                      # Telegram/SMS bot
├── database.py                 # SQLite database handling
├── backtester.py               # Strategy backtesting
├── dashboard.html              # Web interface
│
├── core/
│   ├── fetcher.py              # Advanced data fetching
│   ├── analyzer.py  
           # Multiple strategy analysis
│   ├── risk_manager.py         # Risk calculation
│   └── portfolio.py            # Portfolio tracking
│
├── config/
│   ├── settings.py             # All configurations
│   ├── strategies.json         # Strategy configurations
│   └── stocks.json             # Stock watchlist
│
├── utils/
│   ├── helpers.py              # Helper functions
│   ├── notifier.py             # Multiple notification methods
│   └── logger.py               # Logging system
│
├── templates/                  # HTML templates
├── static/                     # CSS, JS files
├── requirements.txt            # All dependencies
└── README.md                   # Documentation

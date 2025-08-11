# config.py
class Config:
    # 币安API设置
    SPOT_API_URL = "https://api.binance.com"
    FUTURES_API_URL = "https://fapi.binance.com"
    
    # 监控配置
    SYMBOLS = [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "SOLUSDT_PERP",  # 永续合约
        "XRPUSDT_PERP"   # 永续合约
    ]
    
    # 时间窗口及对应的波动阈值 (分钟为单位)
    TIME_WINDOWS = {
        5: 1.0    # 5分钟窗口阈值 1.0%
        15: 2.0,   # 15分钟窗口阈值 2.0%
        60: 3.5    # 60分钟窗口阈值 3.5%
    }
    
    CHECK_INTERVAL = 60  # 检查间隔(秒)
    
    # 历史数据设置
    MAX_HISTORY_HOURS = 24  # 保留历史数据的小时数
    DATA_FILE = "price_history.json"  # 历史数据存储文件
    
    # Telegram通知设置
    TELEGRAM_ENABLED = True                         # True 为开启通知，False 为不开启
    TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"  # 替换你的TG机器人token
    TELEGRAM_CHAT_ID = "your_telegram_chat_id"      # 替换你的chat_id
    
    # 启动通知
    STARTUP_NOTIFICATION = True  # 是否发送启动通知
    
    # 代理设置 (如果需要)
    USE_PROXY = False
    PROXY_URL = "http://user:pass@host:port"  # 代理地址
    
    # 调试模式
    DEBUG = True

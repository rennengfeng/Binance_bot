# -*- coding: utf-8 -*-
# 币安监控机器人配置

class Config:
    # ====== 基础配置 ======
    DEBUG = True  # 调试模式开关
    
    # ====== API配置 ======
    # 币安API地址 (现货和合约)
    SPOT_API_URL = "https://api.binance.com"
    FUTURES_API_URL = "https://fapi.binance.com"
    
    # ====== 监控配置 ======
    # 要监控的交易对 (支持现货和合约)
    SYMBOLS = [
        "BTCUSDT",  # 比特币
        "ETHUSDT",  # 以太坊
        "BNBUSDT",  # BNB
        "SOLUSDT",  # Solana
        "XRPUSDT",  # Ripple
        "DOGEUSDT", # Dogecoin
    ]
    
    # 监控时间间隔 (秒)
    CHECK_INTERVAL = 60  # 默认60秒
    
    # 价格波动阈值 (百分比)
    PRICE_CHANGE_THRESHOLD = 3.0  # 默认3%
    
    # 时间窗口设置 (分钟)
    TIME_WINDOWS = [5, 15, 60]  # 监控5分钟/15分钟/1小时涨跌幅
    
    # ====== 通知配置 ======
    # Telegram通知设置 (可选)
    TELEGRAM_ENABLED = False
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
    
    # 邮件通知设置 (可选)
    EMAIL_ENABLED = False
    EMAIL_SMTP_SERVER = "smtp.example.com"
    EMAIL_SMTP_PORT = 587
    EMAIL_USER = "your_email@example.com"
    EMAIL_PASSWORD = "your_email_password"
    EMAIL_RECEIVERS = ["receiver1@example.com", "receiver2@example.com"]
    
    # ====== 代理配置 ======
    # 如果需要代理访问币安API
    USE_PROXY = False
    PROXY_URL = "http://proxy-ip:port"  # 格式: http://username:password@ip:port
    
    # ====== 数据存储 ======
    DATA_FILE = "price_history.json"  # 价格历史存储文件
    MAX_HISTORY_HOURS = 24  # 最大存储历史小时数

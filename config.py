# -*- coding: utf-8 -*-
# 币安价格监控机器人配置

class Config:
    # ====== 基础配置 ======
    DEBUG = True  # 调试模式开关，生产环境设为 False
    
    # ====== API配置 ======
    SPOT_API_URL = "https://api.binance.com"          # 现货API地址
    FUTURES_API_URL = "https://fapi.binance.com"      # 合约API地址
    
    # ====== 监控配置 ======
    # 要监控的交易对 (支持现货和合约)
    SYMBOLS = [
        "BTCUSDT",      # 比特币现货
        "ETHUSDT",      # 以太坊现货
        "BNBUSDT",      # BNB现货
        "SOLUSDT",      # Solana现货
        "BTCUSDT_PERP", # 比特币永续合约
        "ETHUSDT_PERP", # 以太坊永续合约
    ]
    
    # 监控时间间隔 (秒)
    CHECK_INTERVAL = 30
    
    # 价格波动阈值 (百分比)
    PRICE_CHANGE_THRESHOLD = 2.0
    
    # 时间窗口设置 (分钟)
    TIME_WINDOWS = [5, 15, 60]  # 监控5分钟/15分钟/1小时涨跌幅
    
    # ====== Telegram通知配置 ======
    TELEGRAM_ENABLED = True  # 是否启用Telegram通知
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"  # 替换为您的Bot Token
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"      # 替换为您的Chat ID
    
    # ====== 代理配置 (如果需要) ======
    USE_PROXY = False  # 是否使用代理
    PROXY_URL = "http://proxy-ip:port"  # 代理地址
    
    # ====== 数据存储 ======
    DATA_FILE = "price_history.json"  # 价格历史存储文件
    MAX_HISTORY_HOURS = 24  # 存储24小时历史数据

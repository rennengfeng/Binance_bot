#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安价格监控机器人 - 最终优化版
功能：
1. 监控指定交易对的价格
2. 检测指定时间窗口内的价格涨跌幅
3. 当涨跌幅超过阈值时发送Telegram通知
4. 记录价格历史数据
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from config import Config

# 设置日志
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('binance_monitor.log')
    ]
)
logger = logging.getLogger('BinanceMonitor')

class PriceHistory:
    """价格历史数据管理"""
    def __init__(self, data_file=Config.DATA_FILE, max_hours=Config.MAX_HISTORY_HOURS):
        self.data_file = data_file
        self.max_hours = max_hours
        self.history = self.load_history()
    
    def load_history(self):
        """从文件加载历史数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载历史数据失败: {e}")
                return {}
        return {}
    
    def save_history(self):
        """保存历史数据到文件"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"保存历史数据失败: {e}")
    
    def add_price(self, symbol, price):
        """添加新的价格记录"""
        now = datetime.utcnow()
        timestamp = now.isoformat()
        
        if symbol not in self.history:
            self.history[symbol] = []
        
        # 添加新记录
        self.history[symbol].append({
            "timestamp": timestamp,
            "price": float(price)
        })
        
        # 清理过期数据
        self.cleanup_old_data(symbol, now)
        
        # 保存数据
        self.save_history()
    
    def cleanup_old_data(self, symbol, current_time):
        """清理超过最大保留时间的数据"""
        if symbol not in self.history:
            return
        
        # 计算最早保留的时间点
        cutoff_time = current_time - timedelta(hours=self.max_hours)
        
        # 过滤掉旧数据
        self.history[symbol] = [
            entry for entry in self.history[symbol]
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
    
    def get_price_changes(self, symbol, time_windows):
        """计算指定时间窗口内的价格变化"""
        if symbol not in self.history or not self.history[symbol]:
            return {}
        
        current_price = self.history[symbol][-1]["price"]
        current_time = datetime.fromisoformat(self.history[symbol][-1]["timestamp"])
        
        changes = {}
        
        for window in time_windows:
            # 计算窗口开始时间
            window_start = current_time - timedelta(minutes=window)
            
            # 找到窗口开始时间之后的最早价格
            for entry in self.history[symbol]:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= window_start:
                    start_price = entry["price"]
                    price_change = ((current_price - start_price) / start_price) * 100
                    changes[f"{window}m"] = {
                        "start_price": start_price,
                        "current_price": current_price,
                        "change_percent": round(price_change, 2),
                        "time_window": window
                    }
                    break
            else:
                # 如果没有找到足够的历史数据
                changes[f"{window}m"] = {
                    "start_price": None,
                    "current_price": current_price,
                    "change_percent": 0.0,
                    "time_window": window
                }
        
        return changes

class NotificationManager:
    """通知管理器"""
    def __init__(self, config):
        self.config = config
    
    def send_alert(self, symbol, time_window, change_data):
        """发送价格警报"""
        if not self.config.TELEGRAM_ENABLED:
            return
            
        message = self.create_alert_message(symbol, time_window, change_data)
        logger.info(f"ALERT: {message}")
        self.send_telegram(message)
    
    def create_alert_message(self, symbol, time_window, change_data):
        """创建警报消息"""
        change_percent = change_data["change_percent"]
        direction = "📈 上涨" if change_percent > 0 else "📉 下跌"
        abs_change = abs(change_percent)
        
        # 判断是现货还是合约
        market_type = "现货" if "_PERP" not in symbol else "永续合约"
        clean_symbol = symbol.replace("_PERP", "")
        
        return (
            f"🚨 *币安价格波动警报* ({market_type})\n"
            f"• 交易对: `{clean_symbol}`\n"
            f"• 时间窗口: `{time_window}分钟`\n"
            f"• 价格变化: {direction} `{abs_change:.2f}%`\n"
            f"• 起始价格: `${change_data['start_price']:,.2f}`\n"
            f"• 当前价格: `${change_data['current_price']:,.2f}`\n"
            f"• 时间: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )
    
    def send_telegram(self, message):
        """发送Telegram通知"""
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "MarkdownV2"
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Telegram发送失败: {response.text}")
        except Exception as e:
            logger.error(f"Telegram通知错误: {e}")

class BinanceMonitor:
    """币安价格监控器"""
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BinanceMonitor/1.0",
            "Accept": "application/json"
        })
        
        # 设置代理
        self.proxies = None
        if self.config.USE_PROXY and self.config.PROXY_URL:
            self.proxies = {'https': self.config.PROXY_URL}
            logger.info(f"使用代理: {self.config.PROXY_URL}")
        
        # 初始化组件
        self.price_history = PriceHistory()
        self.notifier = NotificationManager(config)
        
        # 警报冷却时间 (避免重复通知)
        self.last_alert_time = {}
        self.alert_cooldown = 5 * 60  # 5分钟
    
    def get_price(self, symbol, futures=False):
        """获取指定交易对的价格"""
        try:
            base_url = self.config.FUTURES_API_URL if futures else self.config.SPOT_API_URL
            endpoint = "/fapi/v1/ticker/price" if futures else "/api/v3/ticker/price"
            url = f"{base_url}{endpoint}?symbol={symbol}"
            
            response = self.session.get(url, proxies=self.proxies, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            return None
    
    def monitor_prices(self):
        """监控价格并检测波动"""
        logger.info("=== 币安价格监控机器人启动 ===")
        logger.info(f"监控交易对: {', '.join(self.config.SYMBOLS)}")
        logger.info(f"监控间隔: {self.config.CHECK_INTERVAL}秒")
        logger.info(f"波动阈值: {self.config.PRICE_CHANGE_THRESHOLD}%")
        logger.info(f"时间窗口: {', '.join(map(str, self.config.TIME_WINDOWS))}分钟")
        
        if self.config.TELEGRAM_ENABLED:
            logger.info("Telegram通知已启用")
        else:
            logger.info("Telegram通知未启用")
        
        while True:
            try:
                current_time = datetime.utcnow()
                logger.debug(f"监控周期开始: {current_time.strftime('%H:%M:%S UTC')}")
                
                for symbol in self.config.SYMBOLS:
                    # 获取当前价格 (自动识别是否永续合约)
                    is_futures = '_PERP' in symbol
                    clean_symbol = symbol.replace('_PERP', '')
                    price = self.get_price(clean_symbol, is_futures)
                    
                    if price is None:
                        logger.warning(f"无法获取 {symbol} 价格，将重试")
                        continue
                    
                    # 添加到历史记录
                    self.price_history.add_price(symbol, price)
                    
                    # 计算价格变化
                    price_changes = self.price_history.get_price_changes(
                        symbol, self.config.TIME_WINDOWS
                    )
                    
                    # 检查是否需要发送警报
                    self.check_for_alerts(symbol, price_changes)
                
                # 等待下一个监控周期
                time.sleep(self.config.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("用户中断，退出程序")
                sys.exit(0)
            except Exception as e:
                logger.error(f"监控出错: {e}")
                time.sleep(30)  # 出错后等待30秒再重试
    
    def check_for_alerts(self, symbol, price_changes):
        """检查价格变化是否超过阈值"""
        for time_key, change_data in price_changes.items():
            if change_data["start_price"] is None:
                continue  # 没有足够历史数据
            
            abs_change = abs(change_data["change_percent"])
            if abs_change >= self.config.PRICE_CHANGE_THRESHOLD:
                # 检查冷却时间
                alert_key = f"{symbol}_{time_key}"
                current_time = time.time()
                last_alert = self.last_alert_time.get(alert_key, 0)
                
                if current_time - last_alert > self.alert_cooldown:
                    # 发送警报
                    self.notifier.send_alert(symbol, change_data["time_window"], change_data)
                    self.last_alert_time[alert_key] = current_time

def main():
    """主函数"""
    try:
        config = Config()
        monitor = BinanceMonitor(config)
        monitor.monitor_prices()
    except Exception as e:
        logger.exception(f"程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

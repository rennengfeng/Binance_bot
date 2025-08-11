#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        # 忽略无效价格
        if price is None or price <= 0:
            logger.warning(f"忽略无效价格: {symbol} {price}")
            return
            
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
    
    def get_price_changes(self, symbol, time_windows_dict):
        """计算指定时间窗口内的价格变化"""
        if symbol not in self.history or not self.history[symbol]:
            return {}
        
        current_price = self.history[symbol][-1]["price"]
        current_time = datetime.fromisoformat(self.history[symbol][-1]["timestamp"])
        
        changes = {}
        
        # 遍历所有时间窗口
        for window, _ in time_windows_dict.items():
            # 计算窗口开始时间
            window_start = current_time - timedelta(minutes=window)
            
            # 找到窗口开始时间之后的最早价格
            for entry in self.history[symbol]:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= window_start:
                    start_price = entry["price"]
                    
                    # 检查价格有效性
                    if start_price <= 0:
                        continue
                        
                    price_change = ((current_price - start_price) / start_price) * 100
                    changes[window] = {
                        "start_price": start_price,
                        "current_price": current_price,
                        "change_percent": round(price_change, 2)
                    }
                    break
            else:
                # 如果没有找到足够的历史数据
                changes[window] = {
                    "start_price": None,
                    "current_price": current_price,
                    "change_percent": 0.0
                }
        
        return changes

class NotificationManager:
    """通知管理器"""
    def __init__(self, config):
        self.config = config
    
    def send_alert(self, symbol, time_window, change_data, threshold):
        """发送价格警报"""
        if not self.config.TELEGRAM_ENABLED:
            return
            
        message = self.create_alert_message(symbol, time_window, change_data, threshold)
        logger.info(f"ALERT: {message}")
        self.send_telegram(message)
    
    def send_startup_message(self, symbols, initial_prices):
        """发送启动通知"""
        if not self.config.TELEGRAM_ENABLED or not self.config.STARTUP_NOTIFICATION:
            return
            
        message = self.create_startup_message(symbols, initial_prices)
        logger.info(f"STARTUP: {message}")
        self.send_telegram(message)
    
    def create_alert_message(self, symbol, time_window, change_data, threshold):
        """创建警报消息"""
        # 转义Telegram MarkdownV2特殊字符
        def escape_markdown(text):
            escape_chars = r'_*[]()~`>#+-=|{}.!'
            return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))
        
        change_percent = change_data["change_percent"]
        direction = "📈 上涨" if change_percent > 0 else "📉 下跌"
        abs_change = abs(change_percent)
        
        # 判断是现货还是合约
        market_type = "现货" if "_PERP" not in symbol else "永续合约"
        clean_symbol = symbol.replace("_PERP", "")
        
        # 转义所有动态内容
        escaped_symbol = escape_markdown(clean_symbol)
        escaped_window = escape_markdown(str(time_window))
        escaped_change = escape_markdown(f"{abs_change:.2f}%")
        escaped_threshold = escape_markdown(f"{threshold}%")
        escaped_start = escape_markdown(f"{change_data['start_price']:,.2f}")
        escaped_current = escape_markdown(f"{change_data['current_price']:,.2f}")
        escaped_time = escape_markdown(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
        
        return (
            f"🚨 *币安价格波动警报* \\({escape_markdown(market_type)}\\)\n"
            f"• 交易对: `{escaped_symbol}`\n"
            f"• 时间窗口: `{escaped_window}分钟` (阈值: `{escaped_threshold}`)\n"
            f"• 价格变化: {direction} `{escaped_change}`\n"
            f"• 起始价格: `${escaped_start}`\n"
            f"• 当前价格: `${escaped_current}`\n"
            f"• 时间: `{escaped_time}`"
        )
    
    def create_startup_message(self, symbols, initial_prices):
        """创建启动消息 - 包含初始价格"""
        # 转义Telegram MarkdownV2特殊字符
        def escape_markdown(text):
            escape_chars = r'_*[]()~`>#+-=|{}.!'
            return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))
        
        # 格式化币种列表
        symbol_list = []
        for symbol in symbols:
            market_type = "现货" if "_PERP" not in symbol else "永续合约"
            clean_symbol = escape_markdown(symbol.replace("_PERP", ""))
            
            # 获取初始价格
            price = initial_prices.get(symbol)
            price_str = f"{price:,.4f}" if price is not None else "获取失败"
            
            # 转义括号
            symbol_list.append(f"• `{clean_symbol}` \\({escape_markdown(market_type)}\\): `{escape_markdown(price_str)}`")
        
        symbol_list_str = "\n".join(symbol_list)
        escaped_time = escape_markdown(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
        
        # 格式化阈值配置
        threshold_config = []
        for window, threshold in self.config.TIME_WINDOWS.items():
            # 双重转义确保安全
            escaped_window = escape_markdown(str(window))
            escaped_threshold = escape_markdown(str(threshold))
            threshold_config.append(f"• `{escaped_window}分钟`: `{escaped_threshold}%`")
        threshold_config_str = "\n".join(threshold_config)
        
        # 确保启动消息包含所有必要信息
        return (
            f"🚀 *币安价格监控已启动* \n"
            f"• 监控开始时间: `{escaped_time}`\n"
            f"• 监控币种 \\({len(symbols)}个\\):\n"  # 转义括号
            f"{symbol_list_str}\n\n"
            f"*监控配置*:\n"
            f"• 检查间隔: `{escape_markdown(str(self.config.CHECK_INTERVAL))}秒`\n"
            f"• 波动阈值:\n"
            f"{threshold_config_str}"
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
                return False
            return True
        except Exception as e:
            logger.error(f"Telegram通知错误: {e}")
            return False

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
        
        # 启动通知标志
        self.startup_notification_sent = False
    
    def get_price(self, symbol, futures=False):
        """获取指定交易对的价格"""
        try:
            base_url = self.config.FUTURES_API_URL if futures else self.config.SPOT_API_URL
            endpoint = "/fapi/v1/ticker/price" if futures else "/api/v3/ticker/price"
            url = f"{base_url}{endpoint}?symbol={symbol}"
            
            response = self.session.get(url, proxies=self.proxies, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = float(data['price'])
            
            # 检查价格有效性
            if price <= 0:
                logger.error(f"获取到无效价格: {symbol} {price}")
                return None
                
            return price
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            return None
    
    def monitor_prices(self):
        """监控价格并检测波动"""
        logger.info("=== 币安价格监控机器人启动 ===")
        logger.info(f"监控交易对: {', '.join(self.config.SYMBOLS)}")
        logger.info(f"监控间隔: {self.config.CHECK_INTERVAL}秒")
        
        # 记录阈值配置
        for window, threshold in self.config.TIME_WINDOWS.items():
            logger.info(f"{window}分钟窗口阈值: {threshold}%")
        
        # 获取初始价格用于启动通知
        initial_prices = {}
        for symbol in self.config.SYMBOLS:
            is_futures = '_PERP' in symbol
            clean_symbol = symbol.replace('_PERP', '')
            price = self.get_price(clean_symbol, is_futures)
            initial_prices[symbol] = price
            if price is None:
                logger.warning(f"获取初始价格失败: {symbol}")
            else:
                logger.info(f"{symbol} 初始价格: {price}")
        
        if self.config.TELEGRAM_ENABLED:
            logger.info("Telegram通知已启用")
            # 发送启动通知
            if not self.startup_notification_sent and self.config.STARTUP_NOTIFICATION:
                logger.info("尝试发送启动通知...")
                if self.notifier.send_startup_message(self.config.SYMBOLS, initial_prices):
                    self.startup_notification_sent = True
                    logger.info("已发送启动通知")
                else:
                    logger.warning("启动通知发送失败")
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
        for window, change_data in price_changes.items():
            # 获取该时间窗口的阈值
            threshold = self.config.TIME_WINDOWS.get(window)
            if threshold is None:
                continue
                
            # 检查数据有效性
            if (
                change_data["start_price"] is None or 
                change_data["start_price"] <= 0 or
                change_data["current_price"] <= 0
            ):
                logger.debug(f"跳过无效数据: {symbol} {window}分钟 - 起始价: {change_data['start_price']}, 当前价: {change_data['current_price']}")
                continue
                
            abs_change = abs(change_data["change_percent"])
            
            # 检查价格变化是否合理
            if abs_change > 1000:  # 超过1000%的变化通常不合理
                logger.warning(f"检测到异常价格波动: {symbol} {window}分钟 {abs_change}%")
                continue
                
            if abs_change >= threshold:
                # 检查冷却时间
                alert_key = f"{symbol}_{window}"
                current_time = time.time()
                last_alert = self.last_alert_time.get(alert_key, 0)
                
                if current_time - last_alert > self.alert_cooldown:
                    # 发送警报
                    self.notifier.send_alert(symbol, window, change_data, threshold)
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

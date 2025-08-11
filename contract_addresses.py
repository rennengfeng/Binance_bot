# -*- coding: utf-8 -*-
# 加密货币合约地址存储

# 格式: 
# 网络名称: {
#     "币种符号": "合约地址",
# }

CONTRACT_ADDRESSES = {
    # Ethereum (ERC20)
    "ETH": {
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "BNB": "0xB8c77482e45F1F44dE1745F52C74426C631bDD52",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    },
    
    # Binance Smart Chain (BEP20)
    "BSC": {
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "ETH": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        "BTCB": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
    },
    
    # Tron (TRC20)
    "TRX": {
        "USDT": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "USDC": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",
        "TUSD": "TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4",
        "BTC": "TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9",
        "ETH": "THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF",
    },
    
    # Polygon (MATIC)
    "MATIC": {
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "DAI": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        "WBTC": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
    },
    
    # 添加更多网络和代币...
}

# 代币符号到名称的映射
TOKEN_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "BNB": "Binance Coin",
    "USDT": "Tether",
    "USDC": "USD Coin",
    "BUSD": "Binance USD",
    "SOL": "Solana",
    "XRP": "Ripple",
    "ADA": "Cardano",
    "DOGE": "Dogecoin",
    "DOT": "Polkadot",
    "AVAX": "Avalanche",
    "LINK": "Chainlink",
    "MATIC": "Polygon",
    "SHIB": "Shiba Inu",
    "TRX": "Tron",
    "UNI": "Uniswap",
    "LTC": "Litecoin",
    # 添加更多代币...
}

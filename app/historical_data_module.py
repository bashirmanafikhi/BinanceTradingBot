# historical_data_module.py
from datetime import datetime, timedelta
import pandas as pd
import helpers.my_logger as my_logger
from helpers.trading_data_service import TradingDataService
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategyEdited
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem

def get_historical_data(year):
    trading_data_service = TradingDataService()
    #success = trading_data_service.load_data(file_name=f'BTC-{year}min.csv')
    success = trading_data_service.load_data()
    
    if success:
        start_date = datetime(2017, 1, 1, 0, 0, 1)
        end_date = start_date + timedelta(days=2000)
        return trading_data_service.query_data()
    else:
        my_logger.info("Data didn't load.")
        return pd.DataFrame()

def historical_data_example():
    symbol = "BTCUSDT"
    trading_client_factory = TradingClientFactory()
    years = [2017, 2018, 2019, 2020, 2021] 
    years = [2021]

    for year in years:
        data = get_historical_data(year)
        fake_client = trading_client_factory.create_fake_trading_client()
        strategy = BollingerRSIStrategyEdited(600, 2, 14, 75, 35)
        trading_system = TradingSystem(symbol, strategy, fake_client)

        signals = trading_system.run_strategy(data)
        trading_system.calculate_profit_loss()

        print(f"\nYear: {year}")
        print(f"Total Commission: {trading_system.trading_client.total_paid_commission}")
        print(f"Trades Count: {trading_system.trades_count}")
        print(f"Total Profit: {trading_system.getTotalProfit()}")
        
        break

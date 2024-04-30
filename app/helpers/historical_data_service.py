from datetime import datetime, timedelta
import helpers.my_logger as my_logger
import os
import pandas as pd


class HistoricalDataService:

    def __init__(self):
        self.data = None


    def get_historical_data(self):
        trading_data_service = HistoricalDataService()
        success = trading_data_service.load_data(file_name=f'BTC-2021min.csv')
        success = trading_data_service.load_data()
        
        if success:
            start_date = datetime(2017, 1, 1, 0, 0, 1)
            end_date = start_date + timedelta(days=2000)
            return trading_data_service.query_data()
        else:
            my_logger.info("Data didn't load.")
            return pd.DataFrame()

    def load_data(self, data_dir = 'bitcoin_historical_data\\2019-2023', file_name = 'chunk_20201223_20210323.csv'):
    #def load_data(self, data_dir = 'app\\bitcoin_historical_data\\Bitcoin Historical Dataset', file_name = 'BTC-2021min.csv'):
        file_path = os.path.join(data_dir, file_name)
        try:
            data = pd.read_csv(file_path, engine="c")
            
            # Inverse data order
            data = data.iloc[::-1]
            
            data = data.rename(columns={'date': 'date1'})
            data = data.rename(columns={'timestamp': 'date'})
            data["date"] = pd.to_datetime(data["date"], unit='ms')
            
            
            #data = data.drop(["unix", "symbol"], axis=1)
            #data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d %H:%M:%S")
            
            
            
            self.data = data
            return True
        except FileNotFoundError:
            my_logger.info(f"File not found: {file_path}")
            return False




    def query_data(self, start_date=None, end_date=None):
        if self.data is None:
            my_logger.info("Data not loaded. Use 'load_data()' to load the data first.")
            return None

        queried_data = self.data
        
        if start_date is not None:
            queried_data = queried_data[queried_data["date"] >= start_date]

        if end_date is not None:
            queried_data = queried_data[queried_data["date"] <= end_date]

        return queried_data
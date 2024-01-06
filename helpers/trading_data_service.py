import logging
import os
import pandas as pd


class TradingDataService:

    def __init__(self, data_dir = 'bitcoin_historical_data\\Bitcoin Historical Dataset', file_name = 'BTC-2017min.csv'):
        self.data_dir = data_dir
        self.file_name = file_name
        self.file_path = os.path.join(data_dir, file_name)
        self.data = None
        # self.load_data()

    def load_data(self):
        """
        Load historical trading data from the CSV file.
        """
        try:
            self.data = pd.read_csv(self.file_path, engine="c")
            # Inverse data order
            self.data = self.data.iloc[::-1]
            # Drop irrelevant columns
            self.data = self.data.drop(["unix", "symbol"], axis=1)
            return True
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return False

    def query_one_month(self):
        start_date = "2017-01-01"
        end_date = "2017-01-31"
        return self.query_data(start_date, end_date)
    

    def query_data(self, start_date=None, end_date=None):
        """
        Query historical trading data based on specific conditions and date range.

        Args:
        - start_date: Start date for filtering (optional).
        - end_date: End date for filtering (optional).

        Returns:
        - Pandas DataFrame containing the queried data.
        """
        if self.data is None:
            print("Data not loaded. Use 'load_data()' to load the data first.")
            return None

        queried_data = self.data
        queried_data["date"] = pd.to_datetime(queried_data["date"], format="%Y-%m-%d %H:%M:%S")
        
        if start_date is not None:
            queried_data = queried_data[queried_data["date"] >= start_date]

        if end_date is not None:
            queried_data = queried_data[queried_data["date"] <= end_date]

        return queried_data

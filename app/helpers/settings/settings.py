import json

import_path = "app/helpers/settings/settings.json"


class BinanceSettings:
    def __init__(self, api_key, api_secret, api_testnet):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_testnet = api_testnet

class Settings:
    def __init__(self, json_file_path= import_path):
        self.json_file_path = json_file_path
        self.settings = self.load_settings()
        self.binance_settings = BinanceSettings(
            api_key=self.settings.get("Binance", {}).get("API_Key"),
            api_secret=self.settings.get("Binance", {}).get("API_Secret"),
            api_testnet=self.settings.get("Binance", {}).get("API_Testnet")
        )

    def load_settings(self):
        try:
            with open(self.json_file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Settings file not found at: {self.json_file_path}")

    @property
    def binance(self):
        return self.binance_settings

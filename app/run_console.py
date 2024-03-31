# main.py
from helpers.settings.log_config import configure_logging
from historical_data_module import historical_data_example
from live_data_module import live_data_example

# Rest of your code...

if __name__ == "__main__":
    configure_logging()
    #live_data_example()
    historical_data_example()

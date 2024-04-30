from io import BytesIO
from trading_conditions.macd_condition import MacdCondition
from trading_conditions.rsi_condition import RSICondition
from trading_conditions.bollinger_bands_condition import BollingerBandsCondition
from trading_conditions.stop_loss_condition import StopLossCondition
from trading_conditions.take_profit_condition import TakeProfitCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from models.database_models import User, TradingBot


def start_bot(id, kline_callback):
    trading_bot = TradingBot.query.get_or_404(id)

    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if trading_system is not None and trading_system.is_running:
        return "Already running!"

    start_kline_socket(trading_bot, kline_callback)

    exchange = trading_bot.exchange

    binance_client = BinanceTradingClient(exchange.api_key, exchange.api_secret, exchange.is_test)
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(
        trading_bot.base_asset, trading_bot.quote_asset, strategy, binance_client, trading_bot.trade_size
    )

    CurrentAppManager.set_trading_system(trading_bot.id, trading_system)

    return "Started successfully."


def stop_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)

    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if trading_system is not None:
        trading_system.stop()

    # Stop Kline Socket and it's thread
    binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
    if binance_websocket_manager is not None:
        binance_websocket_manager.stop_kline_socket()
        CurrentAppManager.remove_websocket_manager(trading_bot.id)

    return "Stopped successfully."


def start_kline_socket(trading_bot, kline_callback):
    try:
        binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
        if binance_websocket_manager is None:
            exchange = trading_bot.exchange
            binance_websocket_manager = MyBinanceSocketManager(exchange.api_key, exchange.api_secret, exchange.is_test)
            CurrentAppManager.set_websocket_manager(trading_bot.id, binance_websocket_manager)

            binance_websocket_manager.start_kline_in_new_thread(
                symbol=trading_bot.get_symbol(), callback=lambda data: kline_callback(data, trading_bot.id)
            )

    except Exception as e:
        CurrentAppManager.remove_websocket_manager(trading_bot.id)
        # Handle the exception as per your application's requirements
        print(f"An error occurred: {e}")


def get_chart_details(trading_system, signals, plot_size=10000):
    if signals is None:
        return

    if plot_size is not None:
        signals = signals.tail(plot_size)

    last_signal = signals.iloc[-1]
    # Convert data to lists
    close_x_data = signals.index.tolist()
    close_y_data = signals["close"].tolist()

    last_order = trading_system.orders_history[-1] if trading_system.orders_history else None
    strategy = trading_system.strategy
    conditions_manager = strategy.conditions_manager
    stop_loss_condition = conditions_manager.get_first_condition_of_type(StopLossCondition)
    take_profit_condition = conditions_manager.get_first_condition_of_type(TakeProfitCondition)

    # Prepare data dictionary
    data = {
        "last_action_price": last_order.price if last_order else None,
        "last_action": last_order.action if last_order else None,
        "last_signal": last_signal.to_json(),
        "take_profit": take_profit_condition.take_profit if take_profit_condition else None,
        "stop_loss": stop_loss_condition.stop_loss if stop_loss_condition else None,
        "last_profit": trading_system.get_last_profit(),
        "last_profit_percentage": trading_system.get_last_profit_percentage(),
        "total_profit": trading_system.total_profit,
        "total_profit_percentage": trading_system.total_profit_percentage,
        "total_trades_count": len(trading_system.orders_history),
        "price_x_data": close_x_data,
        "price_y_data": close_y_data,
    }

    # action signals
    if "signal" in signals.columns:
        # Keep only 'close' and 'signal' columns and drop rows with NaN in 'signal'
        action_signals = signals[["close", "signal"]].dropna(subset=["signal"])

        # Filter buy and sell signals
        buy_signals = action_signals[action_signals["signal"].apply(lambda x: x.action) == ACTION_BUY]
        sell_signals = action_signals[action_signals["signal"].apply(lambda x: x.action) == ACTION_SELL]

        # Extract buy signal x and y data
        data["buy_signal_x_data"] = buy_signals.index.tolist()
        data["buy_signal_y_data"] = buy_signals["close"].tolist()
        data["buy_signal_hover_text"] = (
            buy_signals["signal"].apply(lambda x: f"scale: {x.scale}, category: {x.signal_category}").tolist()
        )

        # Extract sell signal x and y data
        data["sell_signal_x_data"] = sell_signals.index.tolist()
        data["sell_signal_y_data"] = sell_signals["close"].tolist()
        data["sell_signal_hover_text"] = (
            sell_signals["signal"].apply(lambda x: f"scale: {x.scale}, category: {x.signal_category}").tolist()
        )

    bollinger_band_condition = conditions_manager.get_first_condition_of_type(BollingerBandsCondition)
    if bollinger_band_condition:
        upper_band_key = bollinger_band_condition.get_upper_band_key()
        lower_band_key = bollinger_band_condition.get_lower_band_key()

        if lower_band_key in signals.columns and upper_band_key in signals.columns:
            # Drop rows with NaN values in 'BBL' and 'BBU' columns
            bollinger_signals = signals[[lower_band_key, upper_band_key]].dropna()

            # Extract x data
            data["bbl_bbu_x_data"] = bollinger_signals.index.tolist()

            # Extract y data for 'BBL' and 'BBU'
            data["bbl_y_data"] = bollinger_signals[lower_band_key].tolist()
            data["bbu_y_data"] = bollinger_signals[upper_band_key].tolist()

    rsi_condition = conditions_manager.get_first_condition_of_type(RSICondition)
    if rsi_condition:
        rsi_key = rsi_condition.get_rsi_key()

        if rsi_key in signals.columns:
            # Replace rows with NaN values
            rsi_signals = signals[[rsi_key]].fillna(50)

            # Extract x and y data
            data["rsi_x_data"] = rsi_signals.index.tolist()
            data["rsi_y_data"] = rsi_signals[rsi_key].tolist()

    macd_condition = conditions_manager.get_first_condition_of_type(MacdCondition)
    if macd_condition:
        macd_key = macd_condition.get_macd_key()
        macd_signal_key = macd_condition.get_macd_signal_key()
        macd_histogram_key = macd_condition.get_macd_histogram_key()

        if macd_key in signals.columns and macd_signal_key in signals.columns and macd_histogram_key in signals.columns:
            # Drop rows with NaN values in MACD and signal columns
            macd_signals = signals[[macd_key, macd_signal_key, macd_histogram_key]].dropna()

            # Extract x data
            data["macd_x_data"] = macd_signals.index.tolist()

            # Extract y data for MACD and signal
            data["macd_y_data"] = macd_signals[macd_key].tolist()
            data["macd_signal_y_data"] = macd_signals[macd_signal_key].tolist()
            data["macd_histogram_y_data"] = macd_signals[macd_histogram_key].tolist()

    return data


def update_running_trading_system(trading_bot):
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if trading_system is None:
        return

    trading_system.trade_quote_size = trading_bot.trade_size
    strategy = trading_system.strategy
    strategy.conditions_manager.on_conditions_changed(trading_bot.get_start_conditions())


def generate_csv(trading_system):
    if trading_system is None:
        return None

    signals = trading_system.signals

    # Keep only specific columns
    signals = signals.loc[:, ["timestamp", "open", "high", "low", "close"]]

    # Create a BytesIO object to hold the CSV data in memory
    csv_buffer = BytesIO()

    # Write DataFrame to the BytesIO object as a CSV file
    signals.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Reset file pointer to beginning of the file

    return csv_buffer

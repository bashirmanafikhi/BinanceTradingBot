from flask import current_app

class CurrentAppManager:
    
    @staticmethod
    def initialize_objects(app):
        """
        Initialize objects in current_app.
        """
        app.websocket_managers = {}
        app.trading_systems = {}
        
    
    @staticmethod
    def set_websocket_manager(trading_bot_id, websocket_manager):
        """
        Set the WebSocket manager associated with a specific trading bot ID.
        """
        current_app.websocket_managers = current_app.websocket_managers or {}
        current_app.websocket_managers[trading_bot_id] = websocket_manager

    @staticmethod
    def get_websocket_manager(trading_bot_id):
        """
        Get the WebSocket manager associated with a specific trading bot ID.
        """
        return current_app.websocket_managers.get(trading_bot_id)
    
    @staticmethod    
    def remove_websocket_manager(trading_bot_id):
        """
        Remove the WebSocket manager associated with a specific trading bot ID.
        """
        current_app.websocket_managers.pop(trading_bot_id, None)
    
    
    @staticmethod
    def set_trading_system(trading_bot_id, trading_system):
        """
        Set the Trading System associated with a specific trading bot ID.
        """
        current_app.trading_systems = current_app.trading_systems or {}
        current_app.trading_systems[trading_bot_id] = trading_system

    @staticmethod
    def get_trading_system(trading_bot_id):
        """
        Get the Trading System associated with a specific trading bot ID.
        """
        return current_app.trading_systems.get(trading_bot_id)

    @staticmethod
    def get_all_trading_systems():
        return current_app.trading_systems
    
    @staticmethod    
    def remove_trading_system(trading_bot_id):
        """
        Remove the Trading System associated with a specific trading bot ID.
        """
        current_app.trading_systems.pop(trading_bot_id, None)

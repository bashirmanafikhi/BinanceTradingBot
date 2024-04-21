class TradeHistory:
    
    def __init__(self, action, price, quantity, profit):
        self.action = action
        self.price = price
        self.quantity = quantity
        self.profit = profit


    def calculate_order_profit(self, current_price):
        # Calculate costs
        start_cost = self.price * self.quantity
        end_cost = current_price * self.quantity

        # Calculate profit for last action
        profit = end_cost - start_cost
        
        self.profit = profit
        return profit
class RiskManager:
    def __init__(self, portfolio_value=100000):
        self.portfolio_value = portfolio_value
        self.max_risk_per_trade = 0.02  # 2% per trade
        self.max_portfolio_risk = 0.10  # 10% total
        self.position_sizing_enabled = True
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calculate position size based on risk"""
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share <= 0:
            return 0
        
        max_loss = self.portfolio_value * self.max_risk_per_trade
        position_size = max_loss / risk_per_share
        
        # Adjust for portfolio constraints
        position_value = position_size * entry_price
        max_position_value = self.portfolio_value * 0.20  # Max 20% in one stock
        
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
        
        return int(position_size)
    
    def check_portfolio_diversification(self, current_positions, new_symbol):
        """Check diversification rules"""
        # Maximum 5 positions
        if len(current_positions) >= 5:
            return False, "Maximum 5 positions reached"
        
        # Maximum 30% in one sector
        # (You would implement sector checking here)
        
        return True, "OK"
    
    def calculate_var(self, returns, confidence_level=0.95):
        """Calculate Value at Risk"""
        if len(returns) < 20:
            return 0
        
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return abs(var)
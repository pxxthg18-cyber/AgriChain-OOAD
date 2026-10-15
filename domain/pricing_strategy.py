"""
Strategy Design Pattern - Agricultural Pricing Strategies
Demonstrates the Strategy Pattern for dynamically choosing pricing algorithms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IPricingStrategy(ABC):
    """
    Strategy Interface for Produce Pricing Algorithms.
    Allows dynamic calculation of final checkout price depending on market policies.
    """

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Returns readable name of the strategy."""
        pass

    @abstractmethod
    def calculate_price(self, base_price_per_kg: float, quantity_kg: float, days_since_harvest: int) -> Dict[str, Any]:
        """Calculates item cost breakdown and returns total USD price."""
        pass


class FairTradePricingStrategy(IPricingStrategy):
    """
    Fair Trade Strategy: Guarantees a minimum price floor for local farmers
    plus a 10% Fair Trade reinvestment bonus towards SDG 2 Zero Hunger initiatives.
    """

    def get_strategy_name(self) -> str:
        return "Fair Trade Protection (Farmer Guarantee)"

    def calculate_price(self, base_price_per_kg: float, quantity_kg: float, days_since_harvest: int) -> Dict[str, Any]:
        subtotal = base_price_per_kg * quantity_kg
        fair_trade_bonus = subtotal * 0.10  # 10% goes directly to farmer sustainable agriculture fund
        total_price = subtotal + fair_trade_bonus
        
        return {
            "strategy": self.get_strategy_name(),
            "base_unit_price": base_price_per_kg,
            "quantity_kg": quantity_kg,
            "subtotal": round(subtotal, 2),
            "fair_trade_bonus": round(fair_trade_bonus, 2),
            "discount": 0.0,
            "total_price": round(total_price, 2),
            "note": "Includes 10% direct reinvestment in local farming infrastructure."
        }


class DynamicMarketPricingStrategy(IPricingStrategy):
    """
    Dynamic Pricing Strategy: Adjusts price based on produce age (spoilage prevention)
    to reduce post-harvest food waste.
    """

    def get_strategy_name(self) -> str:
        return "Zero Waste Dynamic Pricing (Freshness Discount)"

    def calculate_price(self, base_price_per_kg: float, quantity_kg: float, days_since_harvest: int) -> Dict[str, Any]:
        subtotal = base_price_per_kg * quantity_kg
        discount_rate = 0.0
        
        # Discount older produce to accelerate distribution and prevent wastage
        if days_since_harvest >= 5:
            discount_rate = 0.35  # 35% discount if 5+ days old
        elif days_since_harvest >= 3:
            discount_rate = 0.15  # 15% discount if 3+ days old
            
        discount = subtotal * discount_rate
        total_price = subtotal - discount
        
        return {
            "strategy": self.get_strategy_name(),
            "base_unit_price": base_price_per_kg,
            "quantity_kg": quantity_kg,
            "subtotal": round(subtotal, 2),
            "fair_trade_bonus": 0.0,
            "discount": round(discount, 2),
            "discount_percentage": f"{int(discount_rate * 100)}%",
            "total_price": round(total_price, 2),
            "note": f"Adjusted for harvest freshness ({days_since_harvest} days old)."
        }


class BulkWholesalePricingStrategy(IPricingStrategy):
    """
    Bulk Wholesale Strategy: Provides volume discounts for cooperatives, food banks,
    and institutional buyers aiming for food distribution efficiency.
    """

    def get_strategy_name(self) -> str:
        return "Bulk Wholesale & Food Security Discount"

    def calculate_price(self, base_price_per_kg: float, quantity_kg: float, days_since_harvest: int) -> Dict[str, Any]:
        subtotal = base_price_per_kg * quantity_kg
        discount_rate = 0.0
        
        if quantity_kg >= 500:
            discount_rate = 0.25  # 25% bulk discount for 500kg+
        elif quantity_kg >= 100:
            discount_rate = 0.12  # 12% bulk discount for 100kg+
            
        discount = subtotal * discount_rate
        total_price = subtotal - discount
        
        return {
            "strategy": self.get_strategy_name(),
            "base_unit_price": base_price_per_kg,
            "quantity_kg": quantity_kg,
            "subtotal": round(subtotal, 2),
            "fair_trade_bonus": 0.0,
            "discount": round(discount, 2),
            "discount_percentage": f"{int(discount_rate * 100)}%",
            "total_price": round(total_price, 2),
            "note": f"Volume tier applied for {quantity_kg} kg order."
        }

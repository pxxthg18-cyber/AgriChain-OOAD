"""
Produce Domain Models and ProduceFactory (Factory Design Pattern)
Demonstrates Abstraction, Inheritance, Polymorphism, Encapsulation, and Factory Pattern.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Dict, Any, Optional
from .pricing_strategy import IPricingStrategy, FairTradePricingStrategy, DynamicMarketPricingStrategy, BulkWholesalePricingStrategy


class Produce(ABC):
    """
    Abstract Base Class for Agricultural Produce.
    Encapsulates common produce properties and defines polymorphic interfaces.
    """

    def __init__(
        self,
        produce_id: str,
        crop_name: str,
        category: str,
        base_price_per_kg: float,
        quantity_kg: float,
        harvest_date_str: str,
        origin_farm: str,
        farmer_id: str,
        pricing_strategy: Optional[IPricingStrategy] = None
    ):
        self._produce_id = produce_id
        self._crop_name = crop_name
        self._category = category
        self._base_price_per_kg = base_price_per_kg
        self._quantity_kg = quantity_kg
        self._harvest_date = datetime.strptime(harvest_date_str, "%Y-%m-%d").date()
        self._origin_farm = origin_farm
        self._farmer_id = farmer_id
        # Strategy Pattern reference
        self._pricing_strategy = pricing_strategy or FairTradePricingStrategy()

    @property
    def produce_id(self) -> str:
        return self._produce_id

    @property
    def crop_name(self) -> str:
        return self._crop_name

    @property
    def category(self) -> str:
        return self._category

    @property
    def base_price_per_kg(self) -> float:
        return self._base_price_per_kg

    @property
    def quantity_kg(self) -> float:
        return self._quantity_kg

    @quantity_kg.setter
    def quantity_kg(self, val: float):
        if val >= 0:
            self._quantity_kg = val
        else:
            raise ValueError("Quantity cannot be negative")

    @property
    def origin_farm(self) -> str:
        return self._origin_farm

    @property
    def farmer_id(self) -> str:
        return self._farmer_id

    @property
    def pricing_strategy(self) -> IPricingStrategy:
        return self._pricing_strategy

    def set_pricing_strategy(self, strategy: IPricingStrategy):
        """Dynamic strategy replacement at runtime (Strategy Pattern)."""
        self._pricing_strategy = strategy

    def get_days_since_harvest(self) -> int:
        today = date.today()
        delta = (today - self._harvest_date).days
        return max(0, delta)

    @abstractmethod
    def get_cold_chain_requirement(self) -> Dict[str, Any]:
        """Polymorphic method returning temperature and humidity specifications."""
        pass

    @abstractmethod
    def calculate_remaining_shelf_life_days(self) -> int:
        """Polymorphic calculation of perishable shelf life."""
        pass

    def calculate_final_cost(self, order_quantity_kg: Optional[float] = None) -> Dict[str, Any]:
        """Uses the assigned Strategy Pattern to compute total price."""
        qty = order_quantity_kg if order_quantity_kg is not None else self._quantity_kg
        days_old = self.get_days_since_harvest()
        return self._pricing_strategy.calculate_price(self._base_price_per_kg, qty, days_old)

    def to_dict(self) -> Dict[str, Any]:
        cost_breakdown = self.calculate_final_cost()
        return {
            "produce_id": self._produce_id,
            "crop_name": self._crop_name,
            "category": self._category,
            "base_price_per_kg": self._base_price_per_kg,
            "quantity_kg": self._quantity_kg,
            "harvest_date": self._harvest_date.strftime("%Y-%m-%d"),
            "days_since_harvest": self.get_days_since_harvest(),
            "origin_farm": self._origin_farm,
            "farmer_id": self._farmer_id,
            "pricing_strategy": self._pricing_strategy.get_strategy_name(),
            "cold_chain": self.get_cold_chain_requirement(),
            "remaining_shelf_life_days": self.calculate_remaining_shelf_life_days(),
            "cost_breakdown": cost_breakdown
        }


class FreshProduce(Produce):
    """
    Fresh Produce subclass (Tomatoes, Berries, Leafy Greens).
    Requires strict temperature-controlled cold chain logistics.
    """

    def __init__(self, produce_id: str, crop_name: str, base_price_per_kg: float, quantity_kg: float, harvest_date_str: str, origin_farm: str, farmer_id: str, max_shelf_life_days: int = 10, target_temp_celsius: float = 4.0):
        super().__init__(produce_id, crop_name, "Fresh Vegetable/Fruit", base_price_per_kg, quantity_kg, harvest_date_str, origin_farm, farmer_id)
        self._max_shelf_life_days = max_shelf_life_days
        self._target_temp_celsius = target_temp_celsius

    def get_cold_chain_requirement(self) -> Dict[str, Any]:
        return {
            "requires_refrigeration": True,
            "target_temp_celsius": self._target_temp_celsius,
            "allowed_temp_variance": "± 2°C",
            "humidity_percent": "85% - 90%"
        }

    def calculate_remaining_shelf_life_days(self) -> int:
        remaining = self._max_shelf_life_days - self.get_days_since_harvest()
        return max(0, remaining)


class GrainProduce(Produce):
    """
    Grain Produce subclass (Rice, Wheat, Corn, Legumes).
    Focuses on low moisture levels and ambient bulk storage.
    """

    def __init__(self, produce_id: str, crop_name: str, base_price_per_kg: float, quantity_kg: float, harvest_date_str: str, origin_farm: str, farmer_id: str, moisture_percentage: float = 12.5):
        super().__init__(produce_id, crop_name, "Grain & Staple", base_price_per_kg, quantity_kg, harvest_date_str, origin_farm, farmer_id)
        self._moisture_percentage = moisture_percentage

    def get_cold_chain_requirement(self) -> Dict[str, Any]:
        return {
            "requires_refrigeration": False,
            "target_temp_celsius": 20.0,
            "max_moisture": f"{self._moisture_percentage}%",
            "storage_type": "Dry Silo / Aerated Storage"
        }

    def calculate_remaining_shelf_life_days(self) -> int:
        # Grains have long shelf life (up to 365 days)
        return max(0, 365 - self.get_days_since_harvest())


class OrganicProduce(Produce):
    """
    Organic Certified Produce subclass.
    Includes organic certification codes and premium fair-trade protection.
    """

    def __init__(self, produce_id: str, crop_name: str, base_price_per_kg: float, quantity_kg: float, harvest_date_str: str, origin_farm: str, farmer_id: str, cert_number: str):
        super().__init__(produce_id, crop_name, "Organic Certified", base_price_per_kg, quantity_kg, harvest_date_str, origin_farm, farmer_id)
        self._cert_number = cert_number

    def get_cold_chain_requirement(self) -> Dict[str, Any]:
        return {
            "requires_refrigeration": True,
            "target_temp_celsius": 6.0,
            "organic_certified": True,
            "cert_number": self._cert_number
        }

    def calculate_remaining_shelf_life_days(self) -> int:
        return max(0, 14 - self.get_days_since_harvest())


# ---------------------------------------------------------
# Factory Pattern: ProduceFactory
# ---------------------------------------------------------
class ProduceFactory:
    """
    Factory Class (Factory Pattern) encapsulating object creation logic.
    Decouples client code from concrete Produce instantiation details.
    """

    @staticmethod
    def create_produce(
        produce_type: str,
        produce_id: str,
        crop_name: str,
        base_price_per_kg: float,
        quantity_kg: float,
        harvest_date_str: str,
        origin_farm: str,
        farmer_id: str,
        **extra_kwargs
    ) -> Produce:
        p_type = produce_type.lower().strip()
        
        if "fresh" in p_type or "fruit" in p_type or "vegetable" in p_type:
            return FreshProduce(
                produce_id=produce_id,
                crop_name=crop_name,
                base_price_per_kg=base_price_per_kg,
                quantity_kg=quantity_kg,
                harvest_date_str=harvest_date_str,
                origin_farm=origin_farm,
                farmer_id=farmer_id,
                max_shelf_life_days=extra_kwargs.get("max_shelf_life_days", 12),
                target_temp_celsius=extra_kwargs.get("target_temp_celsius", 4.0)
            )
        elif "grain" in p_type or "staple" in p_type:
            return GrainProduce(
                produce_id=produce_id,
                crop_name=crop_name,
                base_price_per_kg=base_price_per_kg,
                quantity_kg=quantity_kg,
                harvest_date_str=harvest_date_str,
                origin_farm=origin_farm,
                farmer_id=farmer_id,
                moisture_percentage=extra_kwargs.get("moisture_percentage", 12.0)
            )
        elif "organic" in p_type:
            return OrganicProduce(
                produce_id=produce_id,
                crop_name=crop_name,
                base_price_per_kg=base_price_per_kg,
                quantity_kg=quantity_kg,
                harvest_date_str=harvest_date_str,
                origin_farm=origin_farm,
                farmer_id=farmer_id,
                cert_number=extra_kwargs.get("cert_number", "ORG-SDG2-9982")
            )
        else:
            # Default fallback to FreshProduce
            return FreshProduce(
                produce_id=produce_id,
                crop_name=crop_name,
                base_price_per_kg=base_price_per_kg,
                quantity_kg=quantity_kg,
                harvest_date_str=harvest_date_str,
                origin_farm=origin_farm,
                farmer_id=farmer_id
            )

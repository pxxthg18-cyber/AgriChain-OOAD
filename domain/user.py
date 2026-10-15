"""
User Domain Models
Demonstrates Abstraction, Encapsulation, Inheritance, and Polymorphism.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class User(ABC):
    """
    Abstract Base Class for all system users.
    Enforces encapsulation and defines common interface for all actors.
    """

    def __init__(self, user_id: str, name: str, email: str, location: str, username: str = "", password: str = "pass123", phone: str = "+91 98765 43210"):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._location = location
        self._username = username or user_id.lower()
        self._password = password
        self._phone = phone
        self._rating: float = 5.0
        self._active: bool = True

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def phone(self) -> str:
        return self._phone

    # Encapsulation via Read-Only Properties
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def location(self) -> str:
        return self._location

    @property
    def rating(self) -> float:
        return self._rating

    @rating.setter
    def rating(self, value: float):
        if 0.0 <= value <= 5.0:
            self._rating = round(value, 2)
        else:
            raise ValueError("Rating must be between 0.0 and 5.0")

    @property
    def is_active(self) -> bool:
        return self._active

    @abstractmethod
    def get_role(self) -> str:
        """Polymorphic method returning the role string."""
        pass

    @abstractmethod
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Polymorphic method returning custom dashboard analytics for the user role."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializes user data to a dictionary."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "password": self._password,
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "location": self._location,
            "role": self.get_role(),
            "rating": self._rating,
            "is_active": self._active
        }


class Farmer(User):
    """
    Farmer class extending User (Inheritance).
    Represents local agricultural producers.
    """

    def __init__(self, user_id: str, name: str, email: str, location: str, farm_name: str, farm_size_acres: float, username: str = "", password: str = "pass123", phone: str = "+91 98765 43210"):
        super().__init__(user_id, name, email, location, username, password, phone)
        self._farm_name = farm_name
        self._farm_size_acres = farm_size_acres
        self._fair_trade_verified = True
        self._total_harvest_sold_kg = 0.0

    @property
    def farm_name(self) -> str:
        return self._farm_name

    @property
    def farm_size_acres(self) -> float:
        return self._farm_size_acres

    @property
    def fair_trade_verified(self) -> bool:
        return self._fair_trade_verified

    def record_sale(self, quantity_kg: float):
        """Updates cumulative harvest metrics."""
        self._total_harvest_sold_kg += quantity_kg

    def get_role(self) -> str:
        return "Farmer"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "farm_name": self._farm_name,
            "farm_size_acres": self._farm_size_acres,
            "fair_trade_verified": self._fair_trade_verified,
            "total_harvest_sold_kg": self._total_harvest_sold_kg
        })
        return base

    def get_dashboard_summary(self) -> Dict[str, Any]:
        summary = self.to_dict()
        summary.update({
            "farm_name": self._farm_name,
            "farm_size_acres": self._farm_size_acres,
            "fair_trade_verified": self._fair_trade_verified,
            "total_harvest_sold_kg": self._total_harvest_sold_kg,
            "badge": "Fair Trade Certified Farmer"
        })
        return summary


class Buyer(User):
    """
    Buyer class extending User (Inheritance).
    Represents retail consumers, cooperative hubs, or wholesale markets.
    """

    def __init__(self, user_id: str, name: str, email: str, location: str, buyer_type: str = "Wholesale", username: str = "", password: str = "pass123", phone: str = "+91 98765 43210"):
        super().__init__(user_id, name, email, location, username, password, phone)
        self._buyer_type = buyer_type  # Retail, Wholesale, Cooperative
        self._total_purchases_usd = 0.0

    @property
    def buyer_type(self) -> str:
        return self._buyer_type

    def record_purchase(self, amount_usd: float):
        self._total_purchases_usd += amount_usd

    def get_role(self) -> str:
        return "Buyer"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "buyer_type": self._buyer_type,
            "total_purchases_usd": self._total_purchases_usd
        })
        return base

    def get_dashboard_summary(self) -> Dict[str, Any]:
        summary = self.to_dict()
        summary.update({
            "buyer_type": self._buyer_type,
            "total_purchases_usd": self._total_purchases_usd,
            "badge": f"{self._buyer_type} Partner"
        })
        return summary


class LogisticsPartner(User):
    """
    Logistics Partner extending User.
    Monitors cold chain transport and temperature-controlled logistics.
    """

    def __init__(self, user_id: str, name: str, email: str, location: str, fleet_vehicle: str, cold_storage_capable: bool, username: str = "", password: str = "pass123", phone: str = "+91 98765 43210"):
        super().__init__(user_id, name, email, location, username, password, phone)
        self._fleet_vehicle = fleet_vehicle
        self._cold_storage_capable = cold_storage_capable
        self._active_shipments_count = 0

    @property
    def fleet_vehicle(self) -> str:
        return self._fleet_vehicle

    @property
    def cold_storage_capable(self) -> bool:
        return self._cold_storage_capable

    def get_role(self) -> str:
        return "Logistics Partner"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "fleet_vehicle": self._fleet_vehicle,
            "vehicle_info": self._fleet_vehicle,
            "cold_storage_capable": self._cold_storage_capable,
            "active_shipments_count": self._active_shipments_count
        })
        return base

    def get_dashboard_summary(self) -> Dict[str, Any]:
        summary = self.to_dict()
        summary.update({
            "fleet_vehicle": self._fleet_vehicle,
            "cold_storage_capable": self._cold_storage_capable,
            "active_shipments_count": self._active_shipments_count
        })
        return summary


class QualityInspector(User):
    """
    Quality Inspector checking organic certifications and shelf life parameters.
    """

    def __init__(self, user_id: str, name: str, email: str, location: str, certification_agency: str):
        super().__init__(user_id, name, email, location)
        self._certification_agency = certification_agency

    def get_role(self) -> str:
        return "Quality Inspector"

    def get_dashboard_summary(self) -> Dict[str, Any]:
        summary = self.to_dict()
        summary.update({
            "certification_agency": self._certification_agency
        })
        return summary

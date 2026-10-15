"""
Observer Design Pattern - Supply Chain Telemetry & Event Notifications
Demonstrates the Observer Pattern for loosely coupled event notifications.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class IObserver(ABC):
    """Observer Interface. Objects implementing this receive updates from Subject."""

    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        pass


class ISubject(ABC):
    """Subject Interface for registering, unregistering, and notifying observers."""

    @abstractmethod
    def attach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def detach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        pass


class SupplyChainSubject(ISubject):
    """
    Concrete Subject broadcasting supply chain notifications
    (e.g., order created, state transition, cold chain temperature anomaly).
    """

    def __init__(self):
        self._observers: List[IObserver] = []

    def attach(self, observer: IObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event_type, data)


# ---------------------------------------------------------
# Concrete Observers
# ---------------------------------------------------------
class FarmerNotifier(IObserver):
    """Concrete Observer delivering alerts to Farmers."""

    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        time_str = datetime.now().strftime("%H:%M:%S")
        if event_type == "ORDER_PLACED":
            msg = f"🌾 [Farmer Alert] Order #{data.get('order_id')} placed for {data.get('quantity_kg')} kg of {data.get('produce_name')}. Total: ${data.get('total_price_usd')}."
        elif event_type == "TEMP_ANOMALY":
            msg = f"⚠️ [Cold Chain Warning] Temperature spike reported ({data.get('temp_celsius')}°C) for order #{data.get('order_id')}!"
        else:
            msg = f"ℹ️ [Farmer Update] Order #{data.get('order_id')} status updated to {data.get('state')}."
            
        self.notifications.append({"time": time_str, "type": event_type, "message": msg, "target": "Farmer"})


class BuyerNotifier(IObserver):
    """Concrete Observer delivering order tracking updates to Buyers."""

    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        time_str = datetime.now().strftime("%H:%M:%S")
        if event_type == "ORDER_PLACED":
            msg = f"🛒 [Buyer Confirmation] Order #{data.get('order_id')} successfully created. Pricing strategy applied: {data.get('pricing_strategy_used')}."
        elif event_type == "DELIVERED":
            msg = f"🎉 [Delivery Confirmation] Fresh produce order #{data.get('order_id')} has been delivered safely."
        else:
            msg = f"🚚 [Shipment Tracking] Order #{data.get('order_id')} state changed to {data.get('state')}."
            
        self.notifications.append({"time": time_str, "type": event_type, "message": msg, "target": "Buyer"})


class AuditLogger(IObserver):
    """Concrete Observer recording global audit trail."""

    def __init__(self):
        self.audit_trail: List[Dict[str, Any]] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "order_id": data.get("order_id"),
            "payload_summary": f"State={data.get('state', 'N/A')}, Produce={data.get('produce_name', 'N/A')}"
        }
        self.audit_trail.append(entry)

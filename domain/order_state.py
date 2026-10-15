"""
State Design Pattern - Order Lifecycle & Cold Chain Tracking
Demonstrates the State Pattern for dynamic object behavior depending on state.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IOrderState(ABC):
    """
    State Interface for Supply Chain Orders.
    Each state subclass defines allowed transitions and state-dependent behavior.
    """

    @abstractmethod
    def get_state_name(self) -> str:
        pass

    @abstractmethod
    def proceed(self, order: 'Order') -> bool:
        """Transitions order to the next valid lifecycle state."""
        pass

    @abstractmethod
    def cancel(self, order: 'Order') -> bool:
        """Attempts to cancel the order."""
        pass


class PlacedState(IOrderState):
    """Initial state when buyer places an order."""

    def get_state_name(self) -> str:
        return "ORDER_PLACED"

    def proceed(self, order: 'Order') -> bool:
        # Transition from Placed -> Quality Inspected
        order.set_state(QualityInspectedState())
        order.add_history_log("Quality Inspection passed. Cold storage batch sealed.")
        return True

    def cancel(self, order: 'Order') -> bool:
        order.set_state(CancelledState())
        order.add_history_log("Order cancelled before dispatch.")
        return True


class QualityInspectedState(IOrderState):
    """State after agricultural inspector verifies batch quality."""

    def get_state_name(self) -> str:
        return "QUALITY_INSPECTED"

    def proceed(self, order: 'Order') -> bool:
        # Transition from Inspected -> In Transit
        order.set_state(InTransitState())
        order.add_history_log("Loaded onto temperature-monitored refrigerated vehicle. In Transit.")
        return True

    def cancel(self, order: 'Order') -> bool:
        order.set_state(CancelledState())
        order.add_history_log("Order cancelled post-inspection.")
        return True


class InTransitState(IOrderState):
    """State when order is currently in cold-chain transport."""

    def get_state_name(self) -> str:
        return "IN_TRANSIT_COLD_STORAGE"

    def proceed(self, order: 'Order') -> bool:
        # Transition from In Transit -> Delivered
        order.record_delivery_date()
        order.set_state(DeliveredState())
        order.add_history_log("Shipment safely delivered to buyer destination. Temperature log verified.")
        return True

    def cancel(self, order: 'Order') -> bool:
        # Cannot cancel easily while in transit without penalty
        return False


class DeliveredState(IOrderState):
    """Terminal state when produce is delivered."""

    def get_state_name(self) -> str:
        return "DELIVERED"

    def proceed(self, order: 'Order') -> bool:
        # Already delivered - terminal state
        return False

    def cancel(self, order: 'Order') -> bool:
        # Cannot cancel delivered order
        return False


class CancelledState(IOrderState):
    """Terminal state for cancelled orders."""

    def get_state_name(self) -> str:
        return "CANCELLED"

    def proceed(self, order: 'Order') -> bool:
        return False

    def cancel(self, order: 'Order') -> bool:
        return False


# ---------------------------------------------------------
# Order Context Class (State Pattern Context)
# ---------------------------------------------------------
class Order:
    """
    Order Context Class. Maintains a reference to an instance of IOrderState
    representing the current state of the order.
    """

    def __init__(
        self,
        order_id: str,
        buyer_id: str,
        farmer_id: str,
        produce_id: str,
        produce_name: str,
        quantity_kg: float,
        total_price_usd: float,
        pricing_strategy_used: str,
        order_date: Optional[str] = None
    ):
        self._order_id = order_id
        self._buyer_id = buyer_id
        self._farmer_id = farmer_id
        self._produce_id = produce_id
        self._produce_name = produce_name
        self._quantity_kg = quantity_kg
        self._total_price_usd = total_price_usd
        self._pricing_strategy_used = pricing_strategy_used
        self._timestamp = order_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._delivery_timestamp: Optional[str] = None

        # Initial State (State Pattern)
        self._current_state: IOrderState = PlacedState()
        self._telemetry_logs: List[Dict[str, Any]] = []
        self._history_logs: List[str] = [f"Order created on {self._timestamp}"]

        # Cold chain sensor telemetry
        self._current_temp_celsius: float = 4.0
        self._humidity_percent: float = 88.0

    @property
    def order_id(self) -> str:
        return self._order_id

    @property
    def farmer_id(self) -> str:
        return self._farmer_id

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def quantity_kg(self) -> float:
        return self._quantity_kg

    @property
    def total_price_usd(self) -> float:
        return self._total_price_usd

    @property
    def current_state_name(self) -> str:
        return self._current_state.get_state_name()

    @property
    def order_date(self) -> str:
        return self._timestamp

    @property
    def delivery_date(self) -> Optional[str]:
        return self._delivery_timestamp

    def record_delivery_date(self):
        """Records the delivery date when the order reaches Delivered state."""
        if self._delivery_timestamp is None:
            self._delivery_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_state(self, new_state: IOrderState):
        """Sets the new state object (State Pattern Transition)."""
        self._current_state = new_state

    def proceed_state(self) -> bool:
        """Delegates transition behavior to current state object."""
        return self._current_state.proceed(self)

    def cancel_order(self) -> bool:
        """Delegates cancel behavior to current state object."""
        return self._current_state.cancel(self)

    def add_history_log(self, message: str):
        time_str = datetime.now().strftime("%H:%M:%S")
        self._history_logs.append(f"[{time_str}] {message}")

    def record_telemetry(self, temp_celsius: float, humidity_percent: float, gps_loc: str = "Route 9, Sector B"):
        """Simulates IoT cold-storage sensor telemetry reading."""
        self._current_temp_celsius = temp_celsius
        self._humidity_percent = humidity_percent
        time_str = datetime.now().strftime("%H:%M:%S")
        
        anomaly = temp_celsius > 8.0 or temp_celsius < 1.0
        status = "ALERT: Temp Anomaly!" if anomaly else "Optimal Cold Chain"
        
        entry = {
            "time": time_str,
            "temp_celsius": temp_celsius,
            "humidity_percent": humidity_percent,
            "gps_location": gps_loc,
            "status": status,
            "anomaly": anomaly
        }
        self._telemetry_logs.append(entry)
        if anomaly:
            self.add_history_log(f"SENSOR WARNING: Temperature reading {temp_celsius}°C drifted outside safe range!")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self._order_id,
            "buyer_id": self._buyer_id,
            "farmer_id": self._farmer_id,
            "produce_id": self._produce_id,
            "produce_name": self._produce_name,
            "quantity_kg": self._quantity_kg,
            "total_price_usd": self._total_price_usd,
            "pricing_strategy_used": self._pricing_strategy_used,
            "created_timestamp": self._timestamp,
            "order_date": self.order_date,
            "delivery_date": self.delivery_date,
            "state": self._current_state.get_state_name(),
            "current_temp_celsius": self._current_temp_celsius,
            "current_humidity_percent": self._humidity_percent,
            "history_logs": self._history_logs,
            "telemetry_logs": self._telemetry_logs
        }

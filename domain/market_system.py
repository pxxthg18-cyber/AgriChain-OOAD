"""
Singleton / Façade Design Pattern - MarketManager
Central controller orchestrating all domain services, users, catalog items, orders, and observers.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from .user import User, Farmer, Buyer, LogisticsPartner, QualityInspector
from .produce import Produce, ProduceFactory
from .pricing_strategy import FairTradePricingStrategy, DynamicMarketPricingStrategy, BulkWholesalePricingStrategy
from .order_state import Order
from .observers import SupplyChainSubject, FarmerNotifier, BuyerNotifier, AuditLogger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager


class MarketManager:
    """
    Singleton Class & Façade Pattern.
    Single instance controlling system state, coordinating Factory, Strategy, State, and Observer interactions.
    """

    _instance: Optional['MarketManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._users: Dict[str, User] = {}
        self._produce_catalog: Dict[str, Produce] = {}
        self._orders: Dict[str, Order] = {}
        self.db = DatabaseManager()

        # Observer Pattern Event Bus
        self._event_bus = SupplyChainSubject()
        self._farmer_notifier = FarmerNotifier()
        self._buyer_notifier = BuyerNotifier()
        self._audit_logger = AuditLogger()

        self._event_bus.attach(self._farmer_notifier)
        self._event_bus.attach(self._buyer_notifier)
        self._event_bus.attach(self._audit_logger)

        # Seed initial sample data for quick demonstration
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Populates realistic initial domain objects to jumpstart the UI."""
        # 1. Farmers
        f1 = Farmer("F-101", "Rajesh Kumar", "rajesh@agrifarm.org", "Ludhiana, Punjab", "Green Earth Organics", 25.5, username="farmer_rajesh", password="farmer123")
        f2 = Farmer("F-102", "Elena Rostova", "elena@harvest.org", "Valley Farm Hub", "Sunburst Produce Co.", 40.0, username="elena", password="pass123")
        f3 = Farmer("F-103", "Ramesh Patel", "ramesh@patelagri.in", "Nashik, Maharashtra", "Patel Agro Farms", 30.0, username="ramesh", password="pass123")
        f4 = Farmer("F-104", "Sunita Devi", "sunita@annapurna.in", "Muzaffarpur, Bihar", "Annapurna Krishi Hub", 18.0, username="sunita", password="pass123")
        f5 = Farmer("F-105", "Venkatesh Rao", "venkat@deccanorganic.in", "Guntur, Andhra Pradesh", "Deccan Organic Gardens", 50.0, username="venkatesh", password="pass123")

        # 2. Buyers
        b1 = Buyer("B-201", "Metropolitan Co-op Market", "procure@metromarket.com", "Central City", "Cooperative", username="metro", password="pass123")
        b2 = Buyer("B-202", "FreshBasket Supermarkets", "orders@freshbasket.com", "North District", "Wholesale", username="freshbasket", password="pass123")
        b3 = Buyer("B-203", "Reliance Smart Distribution", "supply@reliancesmart.in", "Mumbai", "Wholesale", username="reliance", password="pass123")
        b4 = Buyer("B-204", "BigBasket Sourcing Hub", "procurement@bigbasket.in", "Bengaluru", "Retail", username="bigbasket", password="pass123")
        b5 = Buyer("B-205", "Ramya Kannan", "ramya12@gmail.com", "Madurai, Tamil Nadu", "Wholesale Cooperative", username="buyer_ramya", password="buyer123", phone="+91 90899 08990")

        # 3. Logistics Partners
        l1 = LogisticsPartner("L-301", "AgriCold Logistics India", "dispatch@agricold.in", "Highway Hub 4", "Refrigerated Container Semi-Truck #9", True, username="agricold", password="pass123")
        l2 = LogisticsPartner("L-302", "Saranya Patel", "saranya@coldlogistics.in", "Chennai, Tamil Nadu", "Refrigerated Container Semi-Truck #18", True, username="logistics_saranya", password="logistics123", phone="+91 91234 56789")

        self._users[f1.user_id] = f1
        self._users[f2.user_id] = f2
        self._users[f3.user_id] = f3
        self._users[f4.user_id] = f4
        self._users[f5.user_id] = f5
        self._users[b1.user_id] = b1
        self._users[b2.user_id] = b2
        self._users[b3.user_id] = b3
        self._users[b4.user_id] = b4
        self._users[b5.user_id] = b5
        self._users[l1.user_id] = l1
        self._users[l2.user_id] = l2

        # 4. Produce items created via ProduceFactory
        p1 = ProduceFactory.create_produce(
            produce_type="fresh", produce_id="P-501", crop_name="Vine Ripe Heirloom Tomatoes",
            base_price_per_kg=45.00, quantity_kg=850.0, harvest_date_str="2026-07-26",
            origin_farm="Green Earth Organics", farmer_id="F-101", max_shelf_life_days=10, target_temp_celsius=4.0
        )
        p1.set_pricing_strategy(FairTradePricingStrategy())

        p2 = ProduceFactory.create_produce(
            produce_type="organic", produce_id="P-502", crop_name="Organic Golden Bell Peppers",
            base_price_per_kg=85.00, quantity_kg=400.0, harvest_date_str="2026-07-27",
            origin_farm="Sunburst Produce Co.", farmer_id="F-102", cert_number="ORG-SDG2-8821"
        )
        p2.set_pricing_strategy(FairTradePricingStrategy())

        p3 = ProduceFactory.create_produce(
            produce_type="grain", produce_id="P-503", crop_name="Basmati Long-Grain Paddy Rice",
            base_price_per_kg=65.00, quantity_kg=2500.0, harvest_date_str="2026-07-20",
            origin_farm="Green Earth Organics", farmer_id="F-101", moisture_percentage=11.8
        )
        p3.set_pricing_strategy(BulkWholesalePricingStrategy())

        p4 = ProduceFactory.create_produce(
            produce_type="fresh", produce_id="P-504", crop_name="Crisp Harvest Spinach",
            base_price_per_kg=35.00, quantity_kg=300.0, harvest_date_str="2026-07-24",
            origin_farm="Sunburst Produce Co.", farmer_id="F-102"
        )
        p4.set_pricing_strategy(DynamicMarketPricingStrategy())

        p5 = ProduceFactory.create_produce(
            produce_type="organic", produce_id="P-505", crop_name="Ratnagiri Alphonso Mangoes",
            base_price_per_kg=180.00, quantity_kg=600.0, harvest_date_str="2026-07-25",
            origin_farm="Patel Agro Farms", farmer_id="F-103", cert_number="ORG-SDG2-9901"
        )
        p5.set_pricing_strategy(FairTradePricingStrategy())

        p6 = ProduceFactory.create_produce(
            produce_type="fresh", produce_id="P-506", crop_name="Fresh Sweet Green Peas (Matar)",
            base_price_per_kg=50.00, quantity_kg=750.0, harvest_date_str="2026-07-26",
            origin_farm="Annapurna Krishi Hub", farmer_id="F-104"
        )
        p6.set_pricing_strategy(FairTradePricingStrategy())

        p7 = ProduceFactory.create_produce(
            produce_type="organic", produce_id="P-507", crop_name="Organic Lakadong Turmeric (Haldi)",
            base_price_per_kg=140.00, quantity_kg=500.0, harvest_date_str="2026-07-15",
            origin_farm="Deccan Organic Gardens", farmer_id="F-105", cert_number="ORG-SDG2-7712"
        )
        p7.set_pricing_strategy(BulkWholesalePricingStrategy())

        p8 = ProduceFactory.create_produce(
            produce_type="grain", produce_id="P-508", crop_name="Premium Sharbati Wheat Grains",
            base_price_per_kg=40.00, quantity_kg=3500.0, harvest_date_str="2026-07-18",
            origin_farm="Green Earth Organics", farmer_id="F-101"
        )
        p8.set_pricing_strategy(BulkWholesalePricingStrategy())

        p9 = ProduceFactory.create_produce(
            produce_type="organic", produce_id="P-509", crop_name="Nashik Seedless Black Grapes",
            base_price_per_kg=95.00, quantity_kg=900.0, harvest_date_str="2026-07-26",
            origin_farm="Patel Agro Farms", farmer_id="F-103", cert_number="ORG-SDG2-9902"
        )
        p9.set_pricing_strategy(FairTradePricingStrategy())

        p10 = ProduceFactory.create_produce(
            produce_type="fresh", produce_id="P-510", crop_name="Muzaffarpur Sweet Shahi Litchi",
            base_price_per_kg=120.00, quantity_kg=650.0, harvest_date_str="2026-07-27",
            origin_farm="Annapurna Krishi Hub", farmer_id="F-104"
        )
        p10.set_pricing_strategy(FairTradePricingStrategy())

        p11 = ProduceFactory.create_produce(
            produce_type="organic", produce_id="P-511", crop_name="Guntur Spicy Red Chillies (Mirchi)",
            base_price_per_kg=160.00, quantity_kg=800.0, harvest_date_str="2026-07-22",
            origin_farm="Deccan Organic Gardens", farmer_id="F-105", cert_number="ORG-SDG2-7715"
        )
        p11.set_pricing_strategy(FairTradePricingStrategy())

        self._produce_catalog[p1.produce_id] = p1
        self._produce_catalog[p2.produce_id] = p2
        self._produce_catalog[p3.produce_id] = p3
        self._produce_catalog[p4.produce_id] = p4
        self._produce_catalog[p5.produce_id] = p5
        self._produce_catalog[p6.produce_id] = p6
        self._produce_catalog[p7.produce_id] = p7
        self._produce_catalog[p8.produce_id] = p8
        self._produce_catalog[p9.produce_id] = p9
        self._produce_catalog[p10.produce_id] = p10
        self._produce_catalog[p11.produce_id] = p11

        # 5. Save users & produce to DB
        for u in self._users.values():
            self.db.save_user(u.to_dict())
        for p in self._produce_catalog.values():
            self.db.save_produce(p.to_dict())

        # 6. Seed Orders
        demo_dates = [
            (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d 09:15:00"),
            (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d 14:30:00"),
            (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d 11:45:00"),
            (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d 16:10:00"),
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 10:20:00")
        ]
        o1 = self.create_order("B-201", "P-501", 200.0, "FairTrade", demo_dates[0])
        o2 = self.create_order("B-203", "P-505", 150.0, "FairTrade", demo_dates[1])
        o3 = self.create_order("B-204", "P-503", 500.0, "Bulk", demo_dates[2])
        o4 = self.create_order("B-205", "P-501", 100.0, "FairTrade", demo_dates[3])
        o5 = self.create_order("B-205", "P-503", 250.0, "Bulk", demo_dates[4])

        if o2:
            self.advance_order_state(o2["order_id"])  # Quality Inspected
        if o3:
            self.advance_order_state(o3["order_id"])  # Quality Inspected
            self.advance_order_state(o3["order_id"])  # In Transit
        if o5:
            self.advance_order_state(o5["order_id"])  # Quality Inspected
        if o4:
            self.advance_order_state(o4["order_id"])  # Quality Inspected
            self.advance_order_state(o4["order_id"])  # In Transit
            self.advance_order_state(o4["order_id"])  # Delivered

    # ---------------------------------------------------------
    # Domain Management API
    # ---------------------------------------------------------
    def register_user(self, user: User) -> Dict[str, Any]:
        self._users[user.user_id] = user
        return user.to_dict()

    def get_users(self) -> List[Dict[str, Any]]:
        return [u.to_dict() for u in self._users.values()]

    def get_all_users(self) -> List[Dict[str, Any]]:
        return [u.to_dict() for u in self._users.values()]

    def add_produce_listing(
        self,
        produce_type: str,
        crop_name: str,
        base_price_per_kg: float,
        quantity_kg: float,
        harvest_date_str: str,
        origin_farm: str,
        farmer_id: str,
        pricing_strategy_name: str = "FairTrade",
        **extra_kwargs
    ) -> Dict[str, Any]:

        produce_id = f"P-{uuid.uuid4().hex[:6].upper()}"
        produce = ProduceFactory.create_produce(
            produce_type=produce_type,
            produce_id=produce_id,
            crop_name=crop_name,
            base_price_per_kg=base_price_per_kg,
            quantity_kg=quantity_kg,
            harvest_date_str=harvest_date_str,
            origin_farm=origin_farm,
            farmer_id=farmer_id,
            **extra_kwargs
        )

        # Apply strategy
        if "dynamic" in pricing_strategy_name.lower():
            produce.set_pricing_strategy(DynamicMarketPricingStrategy())
        elif "bulk" in pricing_strategy_name.lower():
            produce.set_pricing_strategy(BulkWholesalePricingStrategy())
        else:
            produce.set_pricing_strategy(FairTradePricingStrategy())

        self._produce_catalog[produce_id] = produce
        self.db.save_produce(produce.to_dict())
        return produce.to_dict()

    def set_produce_strategy(self, produce_id: str, strategy_name: str) -> Optional[Dict[str, Any]]:
        produce = self._produce_catalog.get(produce_id)
        if not produce:
            return None

        if strategy_name == "Dynamic":
            produce.set_pricing_strategy(DynamicMarketPricingStrategy())
        elif strategy_name == "Bulk":
            produce.set_pricing_strategy(BulkWholesalePricingStrategy())
        else:
            produce.set_pricing_strategy(FairTradePricingStrategy())

        return produce.to_dict()

    def get_produce_catalog(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._produce_catalog.values()]

    def create_order(
        self,
        buyer_id: str,
        produce_id: str,
        quantity_kg: float,
        strategy_override: Optional[str] = None,
        order_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:

        produce = self._produce_catalog.get(produce_id)
        buyer = self._users.get(buyer_id)

        if not produce or produce.quantity_kg < quantity_kg:
            return None

        # Temporarily apply strategy override if requested
        if strategy_override == "Dynamic":
            produce.set_pricing_strategy(DynamicMarketPricingStrategy())
        elif strategy_override == "Bulk":
            produce.set_pricing_strategy(BulkWholesalePricingStrategy())
        elif strategy_override == "FairTrade":
            produce.set_pricing_strategy(FairTradePricingStrategy())

        cost_breakdown = produce.calculate_final_cost(quantity_kg)
        total_price = cost_breakdown["total_price"]

        order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        order = Order(
            order_id=order_id,
            buyer_id=buyer_id,
            farmer_id=produce.farmer_id,
            produce_id=produce_id,
            produce_name=produce.crop_name,
            quantity_kg=quantity_kg,
            total_price_usd=total_price,
            pricing_strategy_used=produce.pricing_strategy.get_strategy_name(),
            order_date=order_date
        )

        # Deduct available inventory
        produce.quantity_kg = produce.quantity_kg - quantity_kg
        self._orders[order_id] = order
        self.db.save_produce(produce.to_dict())
        self.db.save_order(order.to_dict())

        # Notify Observers (Observer Pattern)
        self._event_bus.notify("ORDER_PLACED", order.to_dict())

        return order.to_dict()

    def advance_order_state(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Advances Order lifecycle state using State Pattern."""
        order = self._orders.get(order_id)
        if not order:
            return None

        success = order.proceed_state()
        if success:
            self.db.save_order(order.to_dict())
            self._event_bus.notify(order.current_state_name, order.to_dict())

        return order.to_dict()

    def rate_farmer(self, order_id: str, buyer_id: str, stars: float) -> Optional[Dict[str, Any]]:
        """
        Allows a buyer to rate a farmer (1–5 stars) after delivery.
        Uses the Encapsulation + rating setter validation from User base class.
        Rating is averaged with existing rating for fairness.
        """
        order = self._orders.get(order_id)
        if not order:
            return {"error": "Order not found"}

        # Only allow rating on delivered orders
        if order.current_state_name != "DELIVERED":
            return {"error": "You can only rate after the order is delivered"}

        # Only the buyer of this order can rate
        if order.buyer_id != buyer_id:
            return {"error": "Only the buyer of this order can submit a rating"}

        farmer = self._users.get(order.farmer_id)
        if not farmer:
            return {"error": "Farmer not found"}

        # Validate stars range — uses the encapsulated setter which raises ValueError
        try:
            stars = round(float(stars), 1)
            if not (1.0 <= stars <= 5.0):
                return {"error": "Rating must be between 1 and 5 stars"}
            # Average new rating with existing (simple moving average)
            current = farmer.rating
            new_rating = round((current + stars) / 2, 2)
            farmer.rating = new_rating  # triggers setter validation
        except ValueError as e:
            return {"error": str(e)}

        # Persist updated rating
        self.db.save_user(farmer.to_dict())

        # Notify via Observer — store rating event in audit log
        self._event_bus.notify("FARMER_RATED", {
            "order_id": order_id,
            "farmer_id": farmer.user_id,
            "farmer_name": farmer.name,
            "buyer_id": buyer_id,
            "stars_given": stars,
            "new_rating": new_rating,
            "state": "DELIVERED"
        })

        return {
            "success": True,
            "farmer_id": farmer.user_id,
            "farmer_name": farmer.name,
            "stars_given": stars,
            "new_rating": new_rating
        }

    def cancel_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Cancels an order using the State Pattern cancel() method."""
        order = self._orders.get(order_id)
        if not order:
            return None

        success = order.cancel_order()
        if success:
            self.db.save_order(order.to_dict())
            self._event_bus.notify("ORDER_CANCELLED", order.to_dict())
            return order.to_dict()
        # State did not allow cancellation (e.g. already Delivered)
        return None

    def add_telemetry_reading(self, order_id: str, temp_celsius: float, humidity: float) -> Optional[Dict[str, Any]]:
        """Records IoT cold storage temperature telemetry."""
        order = self._orders.get(order_id)
        if not order:
            return None

        order.record_telemetry(temp_celsius, humidity)
        if temp_celsius > 8.0 or temp_celsius < 1.0:
            self._event_bus.notify("TEMP_ANOMALY", order.to_dict())

        return order.to_dict()

    def get_orders(self) -> List[Dict[str, Any]]:
        return [o.to_dict() for o in self._orders.values()]

    def get_notifications(self) -> Dict[str, Any]:
        return self.get_all_notifications()

    def get_all_notifications(self) -> Dict[str, Any]:
        return {
            "farmer_notifications": self._farmer_notifier.notifications,
            "buyer_notifications": self._buyer_notifier.notifications,
            "audit_trail": self._audit_logger.audit_trail
        }

    def get_sdg2_analytics(self) -> Dict[str, Any]:
        """Calculates SDG 2 Zero Hunger impact metrics."""
        total_produce_kg = sum(p.quantity_kg for p in self._produce_catalog.values())
        total_sold_usd = sum(o.total_price_usd for o in self._orders.values())
        total_orders = len(self._orders)
        
        # Estimate post-harvest waste reduction (cold chain monitoring saves ~18% loss on catalog & orders)
        order_kg = sum(o.quantity_kg for o in self._orders.values())
        waste_prevented_kg = round((total_produce_kg + order_kg) * 0.18, 1)

        return {
            "total_produce_catalog_kg": total_produce_kg,
            "total_orders_processed": total_orders,
            "total_fair_trade_volume_usd": round(total_sold_usd, 2),
            "estimated_post_harvest_food_saved_kg": waste_prevented_kg,
            "sdg2_impact_summary": "Zero Hunger goal achieved through fair farmer floor pricing & cold-chain freshness preservation."
        }

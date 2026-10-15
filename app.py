"""
Python Web Application & REST API Server
Exposes the Python OOAD Domain Model through an interactive Web Interface.
Runs using pure standard library http.server (No external pip dependencies required).
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from typing import Dict, Any

from domain import MarketManager, User, Farmer, Buyer, LogisticsPartner, QualityInspector


PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_float(val, default=0.0):
    """Safely convert a value to float, returning default on failure."""
    try:
        if val in (None, ""):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


class OOADRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.market_manager = MarketManager()
        super().__init__(*args, **kwargs)

    def _send_json(self, data: Any, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def _send_file(self, file_path: str, content_type: str):
        if not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return
        
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # --- Static Content ---
        if path == "/" or path == "/index.html":
            self._send_file(os.path.join(BASE_DIR, "templates", "index.html"), "text/html; charset=utf-8")
            return
        elif path.startswith("/static/css/"):
            self._send_file(os.path.join(BASE_DIR, path.lstrip("/")), "text/css")
            return
        elif path.startswith("/static/js/"):
            self._send_file(os.path.join(BASE_DIR, path.lstrip("/")), "application/javascript")
            return

        # --- REST API Endpoints ---
        if path == "/api/catalog":
            self._send_json(self.market_manager.get_produce_catalog())
        elif path == "/api/users":
            self._send_json(self.market_manager.get_all_users())
        elif path == "/api/orders":
            self._send_json(self.market_manager.get_orders())
        elif path == "/api/notifications":
            self._send_json(self.market_manager.get_all_notifications())
        elif path == "/api/analytics":
            self._send_json(self.market_manager.get_sdg2_analytics())
        elif path == "/api/ooad_metadata":
            self._send_json(self._get_ooad_system_metadata())
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON Payload"}, 400)
            return

        if path == "/api/auth/login":
            username_input = payload.get("username", "").strip().lower()
            password_input = payload.get("password", "").strip()
            users = self.market_manager.get_all_users()

            found = None
            for u in users:
                u_id = (u.get("user_id") or "").lower()
                u_uname = (u.get("username") or "").lower()
                u_email = (u.get("email") or "").lower()
                u_name = (u.get("name") or "").lower()
                u_first = u_name.split()[0] if u_name else ""

                if username_input and (
                    username_input == u_id or 
                    username_input == u_uname or 
                    username_input == u_email or 
                    username_input == u_name or 
                    username_input == u_first or 
                    (u_uname and username_input in u_uname) or 
                    (u_uname and u_uname in username_input)
                ):
                    found = u
                    break

            if not found:
                self._send_json({"error": f"Username or User ID '{username_input}' not found. Please register a new account."}, 404)
            else:
                self._send_json({"success": True, "user": found})

        elif path == "/api/auth/register":
            import uuid
            role = payload.get("role", "Farmer")
            name = payload.get("name", "User")
            email = payload.get("email", "user@agrifarm.org")
            phone = payload.get("phone", "+91 98765 43210")
            location = payload.get("location", "Regional Hub")
            username = payload.get("username", "").strip()
            password = payload.get("password", "pass123").strip()

            # Check if username already exists
            existing_users = self.market_manager.get_all_users()
            if any(u.get("username", "").lower() == username.lower() for u in existing_users):
                self._send_json({"error": f"Username '{username}' is already taken. Please choose another username."}, 400)
                return

            if role == "Farmer":
                fid = f"F-{uuid.uuid4().hex[:4].upper()}"
                farm_acres = safe_float(payload.get("farm_size_acres"), 10.0)
                user = Farmer(
                    user_id=fid, name=name, email=email, location=location,
                    username=username, password=password, phone=phone,
                    farm_name=payload.get("farm_name") or "Local Farm",
                    farm_size_acres=farm_acres
                )
            elif role == "Buyer":
                bid = f"B-{uuid.uuid4().hex[:4].upper()}"
                user = Buyer(
                    user_id=bid, name=name, email=email, location=location,
                    username=username, password=password, phone=phone,
                    buyer_type=payload.get("buyer_type", "Wholesale")
                )
            else:
                lid = f"L-{uuid.uuid4().hex[:4].upper()}"
                user = LogisticsPartner(
                    user_id=lid, name=name, email=email, location=location,
                    username=username, password=password, phone=phone,
                    fleet_vehicle=payload.get("fleet_vehicle", "Cold Transport Truck"),
                    cold_storage_capable=True
                )

            res = self.market_manager.register_user(user)
            self._send_json({"success": True, "user": res}, 201)

        elif path == "/api/farmer/register":
            import uuid
            fid = f"F-{uuid.uuid4().hex[:4].upper()}"
            farmer = Farmer(
                user_id=fid,
                name=payload.get("name", "Farmer"),
                email=payload.get("email", f"{fid.lower()}@farm.org"),
                location=payload.get("location", "Regional Hub"),
                farm_name=payload.get("farm_name", "Local Farm"),
                farm_size_acres=safe_float(payload.get("farm_size_acres"), 10.0)
            )
            res = self.market_manager.register_user(farmer)
            self._send_json(res, 201)

        elif path == "/api/produce/add":
            base_p = safe_float(payload.get("base_price_per_kg"), 45.0)
            qty = safe_float(payload.get("quantity_kg"), 100.0)
            res = self.market_manager.add_produce_listing(
                produce_type=payload.get("produce_type", "fresh"),
                crop_name=payload.get("crop_name", "Produce"),
                base_price_per_kg=base_p,
                quantity_kg=qty,
                harvest_date_str=payload.get("harvest_date_str", "2026-07-28"),
                origin_farm=payload.get("origin_farm", "Local Farm"),
                farmer_id=payload.get("farmer_id", "F-101"),
                pricing_strategy_name=payload.get("pricing_strategy", "FairTrade")
            )
            self._send_json(res, 201)

        elif path == "/api/strategy/change":
            produce_id = payload.get("produce_id")
            strategy_name = payload.get("strategy_name")
            res = self.market_manager.set_produce_strategy(produce_id, strategy_name)
            if res:
                self._send_json(res)
            else:
                self._send_json({"error": "Produce not found"}, 404)

        elif path == "/api/order/create":
            res = self.market_manager.create_order(
                buyer_id=payload.get("buyer_id", "B-201"),
                produce_id=payload.get("produce_id"),
                quantity_kg=float(payload.get("quantity_kg", 50.0)),
                strategy_override=payload.get("strategy_override")
            )
            if res:
                self._send_json(res, 201)
            else:
                self._send_json({"error": "Order creation failed. Check inventory."}, 400)

        elif path == "/api/order/advance":
            order_id = payload.get("order_id")
            res = self.market_manager.advance_order_state(order_id)
            if res:
                self._send_json(res)
            else:
                self._send_json({"error": "State transition failed"}, 400)

        elif path == "/api/order/cancel":
            order_id = payload.get("order_id")
            res = self.market_manager.cancel_order(order_id)
            if res:
                self._send_json(res)
            else:
                self._send_json({"error": "Cancel failed — order is already delivered or cannot be cancelled"}, 400)

        elif path == "/api/farmer/rate":
            order_id = payload.get("order_id")
            buyer_id = payload.get("buyer_id")
            stars    = payload.get("stars", 0)
            res = self.market_manager.rate_farmer(order_id, buyer_id, stars)
            if res and res.get("success"):
                self._send_json(res)
            else:
                self._send_json(res or {"error": "Rating failed"}, 400)

        elif path == "/api/telemetry/add":
            order_id = payload.get("order_id")
            temp = float(payload.get("temp_celsius", 4.0))
            humidity = float(payload.get("humidity", 85.0))
            res = self.market_manager.add_telemetry_reading(order_id, temp, humidity)
            if res:
                self._send_json(res)
            else:
                self._send_json({"error": "Order not found"}, 404)
        else:
            self.send_error(404, "Endpoint Not Found")

    def _get_ooad_system_metadata(self) -> Dict[str, Any]:
        """Provides metadata for the OOAD UML Studio view."""
        return {
            "title": "SDG 2: Zero Hunger OOAD System Architecture",
            "language": "Python 3 (Object-Oriented Analysis and Design)",
            "patterns": [
                {
                    "name": "Strategy Pattern",
                    "interface": "IPricingStrategy (ABC)",
                    "implementations": ["FairTradePricingStrategy", "DynamicMarketPricingStrategy", "BulkWholesalePricingStrategy"],
                    "description": "Allows switching produce pricing algorithms dynamically at runtime."
                },
                {
                    "name": "State Pattern",
                    "interface": "IOrderState (ABC)",
                    "states": ["PlacedState", "QualityInspectedState", "InTransitState", "DeliveredState", "CancelledState"],
                    "description": "Encapsulates order supply chain lifecycle and cold storage behavior changes."
                },
                {
                    "name": "Observer Pattern",
                    "subject": "SupplyChainSubject",
                    "observers": ["FarmerNotifier", "BuyerNotifier", "AuditLogger"],
                    "description": "Loosely coupled event notifications when orders transition or temperature alerts trigger."
                },
                {
                    "name": "Factory Pattern",
                    "factory": "ProduceFactory",
                    "products": ["FreshProduce", "GrainProduce", "OrganicProduce"],
                    "description": "Centralizes instantiation logic for produce subclasses with validation."
                },
                {
                    "name": "Singleton / Façade Pattern",
                    "singleton": "MarketManager",
                    "description": "Single entry point orchestrating all domain services, users, catalog, and orders."
                }
            ],
            "class_diagram_url": "/static/images/class_diagram.png"
        }


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    server_address = ("0.0.0.0", PORT)
    try:
        with ReusableTCPServer(server_address, OOADRequestHandler) as httpd:
            print("[+] AgriChain OOAD Web Server running at http://localhost:8000")
            httpd.serve_forever()
    except OSError as e:
        print(f"[!] Server error on port 8000: {e}")

if __name__ == "__main__":
    run_server()

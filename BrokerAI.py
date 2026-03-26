import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from enum import Enum
import logging
from pathlib import Path

# Hardware Interface Imports
import bluetooth_low_energy as ble
import gps_module
import camera_vision
import barcode_scanner
import nfc_reader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrokerAI")


class SupplyCategory(Enum):
    GROCERIES = "groceries"
    MEDICAL = "medical"
    CLEANING = "cleaning"
    HARDWARE = "hardware"
    PERSONAL = "personal"
    EMERGENCY = "emergency"


class SupplyStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    CRITICAL = "critical"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    IN_TRANSIT = "in_transit"


@dataclass
class SupplyItem:
    """Represents a tracked supply item"""
    id: str
    name: str
    category: SupplyCategory
    quantity: float
    unit: str
    location: str
    storage_conditions: Dict[str, float]
    date_added: datetime
    expiration_date: Optional[datetime]
    ble_beacon_id: Optional[str]
    gps_tracker_id: Optional[str]
    barcode: Optional[str]
    reorder_threshold: float
    reorder_quantity: float
    supplier_info: Dict
    status: SupplyStatus = SupplyStatus.IN_STOCK
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def to_dict(self):
        data = asdict(self)
        data['category'] = self.category.value
        data['status'] = self.status.value
        data['date_added'] = self.date_added.isoformat()
        data['expiration_date'] = self.expiration_date.isoformat() if self.expiration_date else None
        data['last_updated'] = self.last_updated.isoformat()
        return data


class BrokerAI:
    """
    Main AI class for supply management
    Handles inventory tracking, predictive restocking, and GPS monitoring
    """
    
    def __init__(self, db_path: str = "broker_inventory.db"):
        self.db_path = db_path
        self.ble_scanner = ble.BLEScanner()
        self.gps = gps_module.GPSTracker()
        self.camera = camera_vision.InventoryCamera()
        self.scanner = barcode_scanner.BarcodeScanner()
        self.nfc = nfc_reader.NFCInterface()
        
        self.consumption_patterns = {}
        self.location_cache = {}
        
        self._init_database()
        self._load_consumption_patterns()
        
    def _init_database(self):
        """Initialize SQLite database for local inventory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                quantity REAL,
                unit TEXT,
                location TEXT,
                storage_temp REAL,
                storage_humidity REAL,
                date_added TEXT,
                expiration_date TEXT,
                ble_beacon_id TEXT,
                gps_tracker_id TEXT,
                barcode TEXT,
                reorder_threshold REAL,
                reorder_quantity REAL,
                supplier_info TEXT,
                status TEXT,
                last_updated TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumption_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                quantity_used REAL,
                timestamp TEXT,
                context TEXT,
                FOREIGN KEY (item_id) REFERENCES inventory(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_tracking (
                tracker_id TEXT PRIMARY KEY,
                item_id TEXT,
                latitude REAL,
                longitude REAL,
                timestamp TEXT,
                battery_level REAL,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    async def add_item(self, item: SupplyItem) -> bool:
        """Add new item to inventory with automatic tagging"""
        try:
            if item.location.startswith("home:") and not item.ble_beacon_id:
                item.ble_beacon_id = await self._assign_ble_beacon()
            
            if item.category in [SupplyCategory.GROCERIES, SupplyCategory.MEDICAL] and not item.gps_tracker_id:
                item.gps_tracker_id = await self._assign_gps_tracker()
            
            self._save_item(item)
            await self._notify_guardian_house("supply_added", item.to_dict())
            
            logger.info(f"Added item: {item.name} (ID: {item.id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add item: {e}")
            return False
    
    def _save_item(self, item: SupplyItem):
        """Persist item to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO inventory VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            item.id, item.name, item.category.value, item.quantity, item.unit,
            item.location, item.storage_conditions.get('temp'),
            item.storage_conditions.get('humidity'),
            item.date_added.isoformat(),
            item.expiration_date.isoformat() if item.expiration_date else None,
            item.ble_beacon_id, item.gps_tracker_id, item.barcode,
            item.reorder_threshold, item.reorder_quantity,
            json.dumps(item.supplier_info), item.status.value,
            item.last_updated.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def consume_item(self, item_id: str, quantity: float, context: str = "general"):
        """Record consumption and update inventory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Item {item_id} not found")
            return False
        
        new_quantity = row[3] - quantity
        status = self._calculate_status(new_quantity, row[13], row[9])
        
        cursor.execute('''
            UPDATE inventory SET quantity = ?, status = ?, last_updated = ?
            WHERE id = ?
        ''', (new_quantity, status.value, datetime.now().isoformat(), item_id))
        
        cursor.execute('''
            INSERT INTO consumption_log (item_id, quantity_used, timestamp, context)
            VALUES (?, ?, ?, ?)
        ''', (item_id, quantity, datetime.now().isoformat(), context))
        
        conn.commit()
        conn.close()
        
        self._update_consumption_pattern(item_id, quantity, context)
        
        if status in [SupplyStatus.LOW_STOCK, SupplyStatus.CRITICAL]:
            await self._trigger_reorder_alert(item_id)
        
        return True
    
    def _calculate_status(self, quantity: float, threshold: float, expiration_str: Optional[str]) -> SupplyStatus:
        """Determine item status based on quantity and expiration"""
        if expiration_str:
            exp_date = datetime.fromisoformat(expiration_str)
            days_until_exp = (exp_date - datetime.now()).days
            
            if days_until_exp < 0:
                return SupplyStatus.EXPIRED
            elif days_until_exp <= 3:
                return SupplyStatus.EXPIRING_SOON
        
        if quantity <= 0:
            return SupplyStatus.CRITICAL
        elif quantity <= threshold:
            return SupplyStatus.LOW_STOCK
        
        return SupplyStatus.IN_STOCK
    
    async def scan_ble_inventory(self):
        """Scan for all BLE beacons in home and update locations"""
        beacons = await self.ble_scanner.scan(duration=10)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for beacon in beacons:
            beacon_id = beacon['uuid']
            rssi = beacon['rssi']
            location = self._triangulate_position(beacon_id, rssi)
            
            cursor.execute('''
                UPDATE inventory SET location = ?, last_updated = ?
                WHERE ble_beacon_id = ?
            ''', (f"home:{location}", datetime.now().isoformat(), beacon_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated {len(beacons)} items via BLE scan")
    
    async def update_gps_locations(self):
        """Update locations for all GPS-tracked items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT gps_tracker_id, id FROM inventory WHERE gps_tracker_id IS NOT NULL")
        trackers = cursor.fetchall()
        
        for tracker_id, item_id in trackers:
            try:
                location = await self.gps.get_location(tracker_id)
                
                if location:
                    cursor.execute('''
                        INSERT OR REPLACE INTO gps_tracking 
                        (tracker_id, item_id, latitude, longitude, timestamp, battery_level, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        tracker_id, item_id, location['lat'], location['lon'],
                        datetime.now().isoformat(), location['battery'], location['status']
                    ))
                    
                    cursor.execute('''
                        UPDATE inventory SET location = ?, status = ?
                        WHERE id = ?
                    ''', (
                        f"gps:{location['lat']},{location['lon']}",
                        SupplyStatus.IN_TRANSIT.value,
                        item_id
                    ))
                    
            except Exception as e:
                logger.error(f"GPS update failed for {tracker_id}: {e}")
        
        conn.commit()
        conn.close()
    
    async def visual_inventory_scan(self, location: str):
        """Use camera to scan pantry/fridge and recognize items"""
        image = await self.camera.capture(location)
        detected_items = await self.camera.recognize_items(image)
        
        for item_data in detected_items:
            existing = self._find_item_by_visual_signature(item_data['signature'])
            
            if existing:
                if abs(existing.quantity - item_data['estimated_quantity']) > 0.1:
                    await self.consume_item(
                        existing.id, 
                        existing.quantity - item_data['estimated_quantity'],
                        context="visual_scan_adjustment"
                    )
            else:
                new_item = SupplyItem(
                    id=f"VIS_{datetime.now().timestamp()}",
                    name=item_data['name'],
                    category=self._categorize_item(item_data['name']),
                    quantity=item_data['estimated_quantity'],
                    unit=item_data['unit'],
                    location=location,
                    storage_conditions={},
                    date_added=datetime.now(),
                    expiration_date=item_data.get('expiration_date'),
                    ble_beacon_id=None,
                    gps_tracker_id=None,
                    barcode=None,
                    reorder_threshold=1.0,
                    reorder_quantity=2.0,
                    supplier_info={}
                )
                await self.add_item(new_item)
    
    def _update_consumption_pattern(self, item_id: str, quantity: float, context: str):
        """Update ML model with new consumption data"""
        if item_id not in self.consumption_patterns:
            self.consumption_patterns[item_id] = {
                'daily_avg': 0,
                'weekly_pattern': [0] * 7,
                'context_weights': {},
                'last_updated': datetime.now()
            }
        
        pattern = self.consumption_patterns[item_id]
        pattern['daily_avg'] = (pattern['daily_avg'] * 0.9) + (quantity * 0.1)
        
        day = datetime.now().weekday()
        pattern['weekly_pattern'][day] += quantity
        
        if context not in pattern['context_weights']:
            pattern['context_weights'][context] = 0
        pattern['context_weights'][context] += quantity
        
        pattern['last_updated'] = datetime.now()
    
    def predict_reorder_date(self, item_id: str) -> Optional[datetime]:
        """Predict when item will need reordering based on consumption patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, reorder_threshold FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row or item_id not in self.consumption_patterns:
            return None
        
        current_qty, threshold = row[0], row[1]
        pattern = self.consumption_patterns[item_id]
        
        if pattern['daily_avg'] <= 0:
            return None
        
        days_until_reorder = (current_qty - threshold) / pattern['daily_avg']
        return datetime.now() + timedelta(days=days_until_reorder)
    
    async def generate_shopping_list(self) -> List[Dict]:
        """AI-generated shopping list based on predictions and current stock"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        conn.close()
        
        shopping_list = []
        
        for row in items:
            item = self._row_to_item(row)
            prediction = self.predict_reorder_date(item.id)
            
            priority_score = 0
            
            if item.status == SupplyStatus.CRITICAL:
                priority_score += 100
            elif item.status == SupplyStatus.EXPIRED:
                priority_score += 90
            elif item.status == SupplyStatus.EXPIRING_SOON:
                priority_score += 70
            
            if prediction and (prediction - datetime.now()).days <= 3:
                priority_score += 50
            
            day = datetime.now().weekday()
            if day in [4, 5] and item.category == SupplyCategory.GROCERIES:
                if 'cooking' in self.consumption_patterns.get(item_id, {}).get('context_weights', {}):
                    priority_score += 20
            
            if priority_score > 30:
                shopping_list.append({
                    'item': item.to_dict(),
                    'priority': priority_score,
                    'predicted_need_date': prediction.isoformat() if prediction else None,
                    'suggested_quantity': item.reorder_quantity,
                    'reason': self._generate_reason(item, prediction)
                })
        
        shopping_list.sort(key=lambda x: x['priority'], reverse=True)
        return shopping_list
    
    async def _trigger_reorder_alert(self, item_id: str):
        """Send alert to Guardian House and user devices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, quantity, unit FROM inventory WHERE id = ?", (item_id,))
        name, qty, unit = cursor.fetchone()
        conn.close()
        
        alert = {
            'type': 'supply_reorder',
            'item_id': item_id,
            'item_name': name,
            'current_quantity': f"{qty} {unit}",
            'timestamp': datetime.now().isoformat(),
            'suggested_action': 'add_to_shopping_list'
        }
        
        await self._notify_guardian_house("supply_alert", alert)
        logger.info(f"Reorder alert triggered for {name}")
    
    async def _notify_guardian_house(self, event_type: str, data: dict):
        """Send data to Guardian House AI for cross-system learning"""
        message = {
            'source': 'BrokerAI',
            'event': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug(f"Notified Guardian House: {event_type}")
    
    def _row_to_item(self, row) -> SupplyItem:
        """Convert database row to SupplyItem object"""
        return SupplyItem(
            id=row[0], name=row[1], category=SupplyCategory(row[2]),
            quantity=row[3], unit=row[4], location=row[5],
            storage_conditions={'temp': row[6], 'humidity': row[7]},
            date_added=datetime.fromisoformat(row[8]),
            expiration_date=datetime.fromisoformat(row[9]) if row[9] else None,
            ble_beacon_id=row[10], gps_tracker_id=row[11], barcode=row[12],
            reorder_threshold=row[13], reorder_quantity=row[14],
            supplier_info=json.loads(row[15]) if row[15] else {},
            status=SupplyStatus(row[16])
        )
    
    async def _assign_ble_beacon(self) -> str:
        return f"BLE_{datetime.now().timestamp()}"
    
    async def _assign_gps_tracker(self) -> str:
        return f"GPS_{datetime.now().timestamp()}"
    
    def _triangulate_position(self, beacon_id: str, rssi: int) -> str:
        rooms = {-30: "kitchen", -50: "living_room", -70: "bedroom", -90: "garage"}
        for threshold, room in sorted(rooms.items(), reverse=True):
            if rssi >= threshold:
                return room
        return "unknown"
    
    def _categorize_item(self, name: str) -> SupplyCategory:
        keywords = {
            SupplyCategory.GROCERIES: ['milk', 'bread', 'egg', 'meat', 'vegetable', 'fruit'],
            SupplyCategory.MEDICAL: ['pill', 'medicine', 'bandage', 'vitamin'],
            SupplyCategory.CLEANING: ['soap', 'detergent', 'cleaner', 'sponge'],
            SupplyCategory.HARDWARE: ['screw', 'tool', 'battery', 'lightbulb']
        }
        name_lower = name.lower()
        for category, words in keywords.items():
            if any(word in name_lower for word in words):
                return category
        return SupplyCategory.PERSONAL
    
    def _generate_reason(self, item: SupplyItem, prediction: Optional[datetime]) -> str:
        if item.status == SupplyStatus.CRITICAL:
            return f"Critical stock level: only {item.quantity} {item.unit} remaining"
        elif item.status == SupplyStatus.EXPIRED:
            return f"Item expired on {item.expiration_date.strftime('%Y-%m-%d')}"
        elif prediction:
            days = (prediction - datetime.now()).days
            return f"Predicted to run out in {days} days based on usage patterns"
        return "Regular restock recommended"


async def main():
    """Demo of Broker AI capabilities"""
    broker = BrokerAI()
    
    milk = SupplyItem(
        id="MILK_001",
        name="Organic Whole Milk",
        category=SupplyCategory.GROCERIES,
        quantity=1.0,
        unit="gallon",
        location="home:refrigerator",
        storage_conditions={'temp': 38.0, 'humidity': 85.0},
        date_added=datetime.now(),
        expiration_date=datetime.now() + timedelta(days=14),
        ble_beacon_id=None,
        gps_tracker_id=None,
        barcode="012345678901",
        reorder_threshold=0.25,
        reorder_quantity=1.0,
        supplier_info={'store': 'Whole Foods', 'price': 4.99, 'aisle': 'Dairy'}
    )
    
    await broker.add_item(milk)
    
    for day in range(10):
        await broker.consume_item("MILK_001", 0.1, context="cooking")
        await asyncio.sleep(0.1)
    
    shopping_list = await broker.generate_shopping_list()
    print("\n=== AI SHOPPING LIST ===")
    for item in shopping_list:
        print(f"🛒 {item['item']['name']}: {item['reason']} (Priority: {item['priority']})")
    
    await broker.visual_inventory_scan("home:pantry")
    await broker.update_gps_locations()

if __name__ == "__main__":
    asyncio.run(main())

    
# GUARDIAN HOUSE INTEGRATION PROTOCOL
# The Broker AI feeds contextual intelligence to the central Guardian House AI:
{
    “source”: “BrokerAI”,
    “timestamp”: “2026-02-27T14:30:00Z”,
    “user_behavior_insights”: {
        “stress_indicator”: “high_snack_consumption”,
        “health_opportunity”: “vegetables_expiring_unused”,
        “financial_pattern”: “premium_groceries_declining”
    },
    “predictive_requirements”: {
        “immediate”: [“baby_formula”, “diapers”],
        “seasonal”: [“allergy_medicine”, “sunscreen”],
        “emergency_preparedness”: “72hr_kit_expiring”
    },
    “optimization_suggestions”: {
        “storage”: “refrigerator_temp_fluctuation_detected”,
        “procurement”: “bulk_purchase_opportunity_detected”
    }
}


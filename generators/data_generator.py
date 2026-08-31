"""
Ecom Stock Pipeline - Synthetic Data Generator
Generates fake data → JSON files to /data/raw/
Your extraction logic reads from here
"""

import json
import os
import time
import random
import signal
import logging
from datetime import datetime
from typing import Dict, Any
from faker import Faker
from threading import Thread, Event

# ==========================================
# Configuration
# ==========================================
DATA_DIR = os.getenv("DATA_DIR", "/data/raw")
FAKER_LOCALE = "vi_VN"
BATCH_SIZE = 100
FLUSH_INTERVAL = 30  # seconds

fake = Faker(FAKER_LOCALE)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

shutdown_event = Event()

def signal_handler(sig, frame):
    logger.info("Shutdown signal received, stopping...")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==========================================
# File Writer
# ==========================================
class DataWriter:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.buffers: Dict[str, list] = {}
        self.counts: Dict[str, int] = {}
        os.makedirs(data_dir, exist_ok=True)
    
    def write(self, source: str, record: dict):
        if source not in self.buffers:
            self.buffers[source] = []
            self.counts[source] = 0
        
        self.buffers[source].append(record)
        
        if len(self.buffers[source]) >= BATCH_SIZE:
            self.flush(source)
    
    def flush(self, source: str = None):
        sources = [source] if source else list(self.buffers.keys())
        for src in sources:
            if src in self.buffers and self.buffers[src]:
                ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                self.counts[src] = self.counts.get(src, 0) + 1
                filename = f"{src}_{ts}_{self.counts[src]:06d}.json"
                filepath = os.path.join(self.data_dir, src, filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(self.buffers[src], f, ensure_ascii=False, indent=2)
                
                logger.info(f"[{src}] Wrote {len(self.buffers[src])} records → {filename}")
                self.buffers[src] = []
    
    def get_stats(self) -> dict:
        return {src: self.counts.get(src, 0) for src in self.buffers}

# ==========================================
# Data Generators
# ==========================================
PRODUCTS = [
    {"sku": "LAPTOP-001", "name": "MacBook Pro 14", "category": "Electronics", "price": 39990000},
    {"sku": "PHONE-001", "name": "iPhone 15 Pro", "category": "Electronics", "price": 34990000},
    {"sku": "PHONE-002", "name": "Samsung S24 Ultra", "category": "Electronics", "price": 31990000},
    {"sku": "WATCH-001", "name": "Apple Watch Ultra", "category": "Wearables", "price": 19990000},
    {"sku": "HEADPHONE-001", "name": "AirPods Pro", "category": "Accessories", "price": 6990000},
    {"sku": "TABLET-001", "name": "iPad Air", "category": "Electronics", "price": 17990000},
    {"sku": "SHIRT-001", "name": "Polo Ralph Lauren", "category": "Fashion", "price": 2990000},
    {"sku": "SHOE-001", "name": "Nike Air Max", "category": "Fashion", "price": 4590000},
    {"sku": "BAG-001", "name": "LV Neverfull", "category": "Fashion", "price": 45990000},
    {"sku": "BOOK-001", "name": "Atomic Habits", "category": "Books", "price": 199000},
]

EVENT_TYPES = ["page_view", "product_view", "add_to_cart", "remove_from_cart", "purchase", "wishlist"]
PAYMENT_METHODS = ["credit_card", "debit_card", "e_wallet", "bank_transfer", "cod"]
ORDER_STATUSES = ["pending", "confirmed", "processing", "shipping", "delivered", "cancelled"]
PAGES = ["/", "/products", "/cart", "/checkout", "/account", "/search", "/product/detail", "/blog"]
TRAFFIC_SOURCES = ["organic", "paid", "social", "direct", "referral", "email"]
DEVICES_WEIGHTS = {"mobile": 0.65, "desktop": 0.30, "tablet": 0.05}
EXCHANGE_PAIRS = ["USD/VND", "EUR/VND", "EUR/USD", "USD/JPY", "GBP/USD"]
BASE_RATES = {"USD/VND": 25450, "EUR/VND": 27500, "EUR/USD": 1.08, "USD/JPY": 149.5, "GBP/USD": 1.27}
WEATHER_CONDITIONS = ["sunny", "cloudy", "rainy", "stormy", "foggy", "humid"]
CITIES_WEATHER = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Can Tho", "Nha Trang"]
NEWS_SOURCES = ["VnExpress", "Tuoi Tre", "Thanh Nien", "VietnamNet", "Zing News"]
NEWS_CATEGORIES = ["business", "technology", "politics", "sports", "entertainment", "health"]
NEWS_TITLES = [
    "Thị trường chứng khoán tăng mạnh trong phiên giao dịch hôm nay",
    "Đồng USD tiếp tục biến động trước quyết định của Fed",
    "Xuất khẩu Việt Nam đạt kỷ lục trong quý đầu năm",
    "Công nghệ AI thay đổi cách làm việc tại Việt Nam",
    "Giá vàng bất ngờ giảm sâu, nhà đầu tư lo ngại",
    "Dự báo thời tiết phức tạp trong tuần tới",
    "Tech startup Việt Nam gọi vốn thành công 50 triệu USD",
    "Chính phủ ban hành chính sách mới về thương mại điện tử",
    "Đội tuyển Việt Nam giành chiến thắng quan trọng",
    "Phát hiện biến thể mới của virus, Bộ Y tế lên tiếng",
]

def generate_ecommerce_event() -> Dict[str, Any]:
    product = random.choice(PRODUCTS)
    event_type = random.choices(EVENT_TYPES, weights=[40, 25, 15, 5, 10, 5], k=1)[0]
    return {
        "event_id": fake.uuid4(),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": f"user_{random.randint(1, 10000)}",
        "session_id": fake.uuid4(),
        "product": product,
        "quantity": random.randint(1, 5) if event_type in ["add_to_cart", "purchase"] else 0,
        "device": random.choice(["mobile", "desktop", "tablet"]),
        "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
        "ip_address": fake.ipv4(),
        "referrer": random.choice(["google", "facebook", "direct", "email", "instagram"]),
    }

def generate_order() -> Dict[str, Any]:
    items, total = [], 0
    for _ in range(random.randint(1, 4)):
        p = random.choice(PRODUCTS)
        qty = random.randint(1, 3)
        total += p["price"] * qty
        items.append({"sku": p["sku"], "name": p["name"], "price": p["price"], "quantity": qty})
    return {
        "order_id": f"ORD-{fake.uuid4()[:8].upper()}",
        "timestamp": datetime.utcnow().isoformat(),
        "customer": {
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "city": random.choice(["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ"]),
        },
        "items": items,
        "subtotal": total,
        "shipping_fee": random.choice([0, 30000, 50000]),
        "total": total,
        "payment_method": random.choice(PAYMENT_METHODS),
        "status": random.choice(ORDER_STATUSES),
    }

def generate_product_catalog() -> Dict[str, Any]:
    p = random.choice(PRODUCTS)
    return {
        "sku": p["sku"], "name": p["name"], "category": p["category"], "price": p["price"],
        "cost": int(p["price"] * random.uniform(0.4, 0.7)),
        "stock": random.randint(0, 500),
        "warehouse": random.choice(["HCM", "HN", "DN"]),
        "supplier": fake.company(),
        "updated_at": datetime.utcnow().isoformat(),
    }

def generate_traffic() -> Dict[str, Any]:
    return {
        "event_id": fake.uuid4(),
        "event_type": random.choices(["page_view", "session_start", "click", "conversion"], weights=[40, 20, 30, 10], k=1)[0],
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": fake.uuid4(),
        "user_id": f"user_{random.randint(1, 50000)}",
        "page": random.choice(PAGES),
        "source": random.choice(TRAFFIC_SOURCES),
        "device": random.choices(list(DEVICES_WEIGHTS.keys()), weights=list(DEVICES_WEIGHTS.values()), k=1)[0],
        "browser": random.choice(["Chrome", "Safari", "Firefox"]),
        "os": random.choice(["Windows", "macOS", "iOS", "Android"]),
        "city": random.choice(["Ho Chi Minh", "Ha Noi", "Da Nang"]),
        "load_time_ms": random.randint(200, 5000),
    }

def generate_exchange_rate() -> Dict[str, Any]:
    pair = random.choice(EXCHANGE_PAIRS)
    rate = round(BASE_RATES[pair] * (1 + random.uniform(-0.02, 0.02)), 4)
    return {
        "pair": pair, "timestamp": datetime.utcnow().isoformat(),
        "bid": round(rate * 0.999, 4), "ask": round(rate * 1.001, 4), "mid": rate,
    }

def generate_weather() -> Dict[str, Any]:
    city = random.choice(CITIES_WEATHER)
    base = {"Ho Chi Minh": 32, "Ha Noi": 28, "Da Nang": 30, "Can Tho": 31, "Nha Trang": 31}
    cond = random.choice(WEATHER_CONDITIONS)
    return {
        "city": city, "timestamp": datetime.utcnow().isoformat(),
        "temperature": round(base[city] + random.uniform(-5, 5), 1),
        "humidity": random.randint(50, 95), "condition": cond,
        "wind_kmh": round(random.uniform(0, 40), 1),
        "rain_mm": round(random.uniform(0, 50), 1) if cond in ["rainy", "stormy"] else 0,
    }

def generate_news() -> Dict[str, Any]:
    return {
        "news_id": fake.uuid4(), "title": random.choice(NEWS_TITLES),
        "source": random.choice(NEWS_SOURCES), "category": random.choice(NEWS_CATEGORIES),
        "timestamp": datetime.utcnow().isoformat(), "author": fake.name(),
        "sentiment": random.choice(["positive", "negative", "neutral"]),
    }

# ==========================================
# Main Loop
# ==========================================
GENERATORS = {
    "ecommerce-events": {"fn": generate_ecommerce_event, "interval": 0.5},
    "orders":           {"fn": generate_order,           "interval": 2.0},
    "product-catalog":  {"fn": generate_product_catalog, "interval": 5.0},
    "web-traffic":      {"fn": generate_traffic,         "interval": 1.0},
    "exchange-rates":   {"fn": generate_exchange_rate,   "interval": 3.0},
    "weather":          {"fn": generate_weather,         "interval": 10.0},
    "news":             {"fn": generate_news,            "interval": 8.0},
}

def gen_loop(writer: DataWriter, source: str, gen_func, interval: float):
    while not shutdown_event.is_set():
        try:
            writer.write(source, gen_func())
        except Exception as e:
            logger.error(f"[{source}] Error: {e}")
        shutdown_event.wait(interval)

def flush_loop(writer: DataWriter):
    while not shutdown_event.is_set():
        shutdown_event.wait(FLUSH_INTERVAL)
        writer.flush()

def main():
    logger.info("=" * 60)
    logger.info("  Ecom Stock Pipeline - Data Generator")
    logger.info(f"  Output: {DATA_DIR}")
    logger.info("=" * 60)

    writer = DataWriter(DATA_DIR)

    threads = []
    for source, cfg in GENERATORS.items():
        t = Thread(target=gen_loop, args=(writer, source, cfg["fn"], cfg["interval"]), daemon=True)
        t.start()
        threads.append(t)
        logger.info(f"  [{source}] every {cfg['interval']}s")

    Thread(target=flush_loop, args=(writer,), daemon=True).start()

    logger.info(f"\nGenerating data... Press Ctrl+C to stop.\n")

    shutdown_event.wait()
    writer.flush()
    logger.info("Generator stopped.")

if __name__ == "__main__":
    main()

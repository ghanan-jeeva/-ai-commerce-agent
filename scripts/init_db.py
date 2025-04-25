import pinecone
import openai
from dotenv import load_dotenv
import os
import json
import random

# Load environment variables
load_dotenv()

def generate_products(num_products=100):
    categories = {
        "laptops": {
            "brands": ["Dell", "HP", "Lenovo", "ASUS", "Acer", "Apple", "MSI"],
            "processors": ["Intel i3", "Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 5", "AMD Ryzen 7"],
            "ram": [8, 16, 32, 64],
            "storage": [256, 512, 1024, 2048],
            "display": [13.3, 14, 15.6, 16, 17.3],
            "gpus": ["NVIDIA RTX 3050", "NVIDIA RTX 3060", "NVIDIA RTX 3070", "NVIDIA RTX 3080", "AMD Radeon RX 6600M"],
            "use_cases": ["gaming", "business", "creative", "student", "professional"],
            "features": ["Backlit Keyboard", "Fingerprint Reader", "Thunderbolt 4", "Wi-Fi 6", "Bluetooth 5.0"],
            "battery_life": ["Up to 8 hours", "Up to 12 hours", "Up to 16 hours", "Up to 20 hours"],
            "build_quality": ["Military-grade durability", "Premium aluminum chassis", "Carbon fiber reinforced", "Slim and lightweight"]
        },
        "smartphones": {
            "brands": ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi"],
            "storage": [128, 256, 512],
            "ram": [6, 8, 12],
            "display": [6.1, 6.4, 6.7],
            "camera_systems": {
                "budget": ["Dual 12MP wide + 12MP ultrawide", "48MP main + 12MP ultrawide"],
                "midrange": ["50MP main + 12MP ultrawide + 10MP telephoto", "48MP main + 50MP ultrawide + 12MP macro"],
                "premium": ["108MP main + 12MP ultrawide + 10MP telephoto", "50MP main + 48MP ultrawide + 48MP telephoto"]
            },
            "features": ["5G", "Wireless Charging", "Fast Charging", "Water Resistant", "Face Recognition", "In-display Fingerprint"],
            "display_tech": ["OLED", "AMOLED", "Super Retina XDR"],
            "refresh_rate": [60, 90, 120],
            "battery_capacity": ["4000mAh", "4500mAh", "5000mAh"],
            "camera_features": ["Night Mode", "Portrait Mode", "Pro Mode", "8K Video", "HDR10+"]
        },
        "tablets": {
            "brands": ["Apple", "Samsung", "Microsoft", "Lenovo"],
            "storage": [64, 128, 256, 512],
            "display": [8.3, 10.2, 11, 12.9],
            "features": ["WiFi", "WiFi + Cellular", "Stylus Support", "Face Recognition", "Fingerprint Reader"],
            "use_cases": ["note-taking", "drawing", "gaming", "productivity", "entertainment"],
            "display_tech": ["Liquid Retina", "AMOLED", "LCD"],
            "accessories": ["Keyboard Cover", "Stylus Pen", "Protective Case"],
            "battery_life": ["Up to 10 hours", "Up to 12 hours", "Up to 15 hours"],
            "display_features": ["120Hz ProMotion", "HDR10+", "True Tone", "Anti-reflective coating"]
        },
        "audio": {
            "brands": ["Sony", "Bose", "Apple", "Samsung", "Jabra"],
            "types": ["Over-ear", "In-ear", "True Wireless"],
            "features": ["Active Noise Cancellation", "Transparency Mode", "Multi-device Connection", 
                        "Water Resistant", "Built-in Voice Assistant", "Touch Controls"],
            "battery_life": ["Up to 8 hours", "Up to 24 hours", "Up to 30 hours", "Up to 36 hours"],
            "use_cases": ["sports", "travel", "office", "audiophile"],
            "sound_features": ["Deep Bass", "Balanced Sound", "High Resolution Audio", "Spatial Audio"],
            "comfort_features": ["Memory foam ear cushions", "Adjustable headband", "Ergonomic design", "Lightweight build"],
            "connectivity": ["Bluetooth 5.2", "Bluetooth 5.3", "AptX HD", "LDAC"]
        }
    }

    products = []
    
    # Add a budget laptop
    budget_laptop = {
        "id": "laptop-budget-1",
        "name": "Acer Budget Laptop",
        "description": "Perfect for students and basic tasks. Features Intel i3 processor, 8GB RAM, 256GB SSD, and a 15.6 inch display. Lightweight and portable with up to 8 hours battery life.",
        "price": 399,
        "category": "laptops",
        "features": [
            "Intel i3",
            "8GB RAM",
            "256GB SSD",
            "15.6 inch display",
            "Up to 8 hours battery life",
            "Lightweight build"
        ],
        "use_case": "student",
        "brand": "Acer"
    }
    products.append(budget_laptop)
    
    # Generate remaining products
    for i in range(num_products - 1):
        category = random.choice(list(categories.keys()))
        cat_data = categories[category]
        brand = random.choice(cat_data["brands"])
        
        if category == "laptops":
            processor = random.choice(cat_data["processors"])
            ram = random.choice(cat_data["ram"])
            storage = random.choice(cat_data["storage"])
            display = random.choice(cat_data["display"])
            gpu = random.choice(cat_data["gpus"]) if random.random() > 0.3 else None
            use_case = random.choice(cat_data["use_cases"])
            extra_features = random.sample(cat_data["features"], k=random.randint(2, 4))
            battery_life = random.choice(cat_data["battery_life"])
            build_quality = random.choice(cat_data["build_quality"])
            price = random.randint(800, 3000)
            
            is_gaming = use_case == "gaming" or (gpu and "RTX" in gpu)
            is_premium = price > 1500 or ram >= 32
            
            product = {
                "id": f"laptop-{i}",
                "name": f"{brand} {'Gaming' if is_gaming else 'Pro' if is_premium else 'Essential'} {display}",
                "description": f"Perfect for {use_case}. Features {processor} processor, {ram}GB RAM, {storage}GB SSD, and a {display} inch display" + 
                             (f" with {gpu}" if gpu else "") + f". {build_quality}. {battery_life} battery life. {', '.join(extra_features)}.",
                "price": price,
                "category": category,
                "features": [
                    processor,
                    f"{ram}GB RAM",
                    f"{storage}GB SSD",
                    f"{display} inch display",
                    battery_life,
                    build_quality
                ] + ([gpu] if gpu else []) + extra_features,
                "use_case": use_case,
                "brand": brand
            }
            
        elif category == "smartphones":
            storage = random.choice(cat_data["storage"])
            ram = random.choice(cat_data["ram"])
            display = random.choice(cat_data["display"])
            price_tier = "premium" if ram >= 12 else "midrange" if ram >= 8 else "budget"
            camera = random.choice(cat_data["camera_systems"][price_tier])
            display_tech = random.choice(cat_data["display_tech"])
            refresh_rate = random.choice(cat_data["refresh_rate"])
            extra_features = random.sample(cat_data["features"], k=random.randint(3, 5))
            battery_capacity = random.choice(cat_data["battery_capacity"])
            camera_features = random.sample(cat_data["camera_features"], k=random.randint(2, 3))
            price = random.randint(400, 1200)
            
            product = {
                "id": f"phone-{i}",
                "name": f"{brand} {'Pro Max' if price > 1000 else 'Pro' if price > 800 else ''} Phone",
                "description": f"Featuring a {display} inch {display_tech} display with {refresh_rate}Hz refresh rate, " +
                             f"{storage}GB storage, {ram}GB RAM, and {camera}. " +
                             f"Enhanced with {', '.join(extra_features)}. " +
                             f"Powerful {battery_capacity} battery. " +
                             f"Advanced camera features: {', '.join(camera_features)}.",
                "price": price,
                "category": category,
                "features": [
                    f"{storage}GB Storage",
                    f"{ram}GB RAM",
                    f"{display} inch {display_tech}",
                    f"{refresh_rate}Hz Display",
                    camera,
                    f"{battery_capacity} Battery"
                ] + extra_features + camera_features,
                "camera_quality": price_tier,
                "brand": brand
            }
            
        elif category == "tablets":
            storage = random.choice(cat_data["storage"])
            display = random.choice(cat_data["display"])
            display_tech = random.choice(cat_data["display_tech"])
            features = random.sample(cat_data["features"], k=random.randint(2, 4))
            use_case = random.choice(cat_data["use_cases"])
            accessories = random.sample(cat_data["accessories"], k=random.randint(1, 2))
            battery_life = random.choice(cat_data["battery_life"])
            display_features = random.sample(cat_data["display_features"], k=random.randint(1, 2))
            price = random.randint(300, 1200)
            
            product = {
                "id": f"tablet-{i}",
                "name": f"{brand} {'Pro' if price > 800 else 'Standard'} Tablet",
                "description": f"Perfect for {use_case}. Features a {display} inch {display_tech} display with {', '.join(display_features)}, " +
                             f"{storage}GB storage, {', '.join(features)}. {battery_life} battery life. Compatible with {' and '.join(accessories)}.",
                "price": price,
                "category": category,
                "features": [
                    f"{storage}GB Storage",
                    f"{display} inch {display_tech} Display",
                    battery_life
                ] + features + display_features,
                "use_case": use_case,
                "accessories": accessories,
                "brand": brand
            }
            
        else:  # audio
            type_ = random.choice(cat_data["types"])
            features = random.sample(cat_data["features"], k=random.randint(2, 4))
            battery = random.choice(cat_data["battery_life"])
            use_case = random.choice(cat_data["use_cases"])
            sound_features = random.sample(cat_data["sound_features"], k=random.randint(1, 2))
            comfort_features = random.sample(cat_data["comfort_features"], k=random.randint(1, 2))
            connectivity = random.choice(cat_data["connectivity"])
            price = random.randint(100, 500)
            
            product = {
                "id": f"audio-{i}",
                "name": f"{brand} {type_} {'Pro' if price > 300 else 'Plus'}",
                "description": f"Perfect for {use_case}. {type_} headphones featuring {', '.join(features)}. " +
                             f"{battery} battery life. {', '.join(sound_features)} for exceptional audio quality. " +
                             f"{', '.join(comfort_features)} for all-day comfort. {connectivity} connectivity.",
                "price": price,
                "category": category,
                "features": [type_] + features + [battery] + sound_features + comfort_features + [connectivity],
                "use_case": use_case,
                "brand": brand
            }
        
        products.append(product)
    
    return products

def init_pinecone():
    print("Initializing Pinecone database with sample products...")
    
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "commerce-agent"))
    
    # Initialize OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Generate products
    products = generate_products(100)
    
    # Upload products to Pinecone
    batch_size = 10
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        vectors = []
        
        for product in batch:
            # Create rich product text for better semantic search
            product_text = (
                f"{product['name']} {product['description']} "
                f"Brand: {product['brand']} Category: {product['category']} "
                f"Features: {' '.join(product['features'])} "
                f"Use case: {product.get('use_case', '')} "
                f"Price: ${product['price']}"
            )
            
            # Get embedding from OpenAI
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=product_text
            )
            embedding = response.data[0].embedding
            
            # Prepare vector with metadata
            vectors.append({
                "id": product["id"],
                "values": embedding,
                "metadata": product
            })
        
        # Upsert batch to Pinecone
        index.upsert(vectors=vectors, namespace="products")
        print(f"Uploaded batch {i//batch_size + 1}/{(len(products) + batch_size - 1)//batch_size}")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_pinecone() 
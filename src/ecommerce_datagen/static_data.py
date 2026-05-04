from __future__ import annotations

BRANDS = [
    ("Samsung", "South Korea"),
    ("Apple", "USA"),
    ("Xiaomi", "China"),
    ("Adidas", "Germany"),
    ("Nike", "USA"),
    ("Sony", "Japan"),
    ("LG", "South Korea"),
    ("Asus", "Taiwan"),
    ("Lenovo", "China"),
    ("Dell", "USA"),
    ("HP", "USA"),
    ("Panasonic", "Japan"),
    ("Philips", "Netherlands"),
    ("Puma", "Germany"),
    ("Uniqlo", "Japan"),
    ("Oppo", "China"),
    ("Vivo", "China"),
    ("Anker", "China"),
    ("LocknLock", "South Korea"),
    ("Sunhouse", "Vietnam"),
]

CATEGORIES = [
    {"category_name": "Electronics", "parent_name": None, "level": 1},
    {"category_name": "Fashion", "parent_name": None, "level": 1},
    {"category_name": "Home & Living", "parent_name": None, "level": 1},
    {"category_name": "Beauty", "parent_name": None, "level": 1},
    {"category_name": "Mobile Phones", "parent_name": "Electronics", "level": 2},
    {"category_name": "Laptops", "parent_name": "Electronics", "level": 2},
    {"category_name": "Men's Wear", "parent_name": "Fashion", "level": 2},
    {"category_name": "Women's Wear", "parent_name": "Fashion", "level": 2},
    {"category_name": "Kitchen Appliances", "parent_name": "Home & Living", "level": 2},
    {"category_name": "Skincare", "parent_name": "Beauty", "level": 2},
]

PROMOTION_NAMES = [
    "9.9 Mega Sale",
    "11.11 Super Deals",
    "12.12 Year End Blast",
    "Weekend Flash Sale",
    "Summer Brand Fest",
    "Back to School Special",
    "Midnight Madness",
    "Free Shipping Frenzy",
    "Hot Brand Week",
    "Member Exclusive Deal",
]

PRODUCT_NAME_PARTS = {
    "Mobile Phones": ["Pro", "Plus", "Ultra", "5G", "128GB", "256GB", "512GB", "AI Camera", "Dual SIM"],
    "Laptops": ["Core i5", "Core i7", "Ryzen 5", "Ryzen 7", "14-inch", "15.6-inch", "OLED", "Gaming", "Office"],
    "Men's Wear": ["T-Shirt", "Polo", "Hoodie", "Jacket", "Jogger", "Slim Fit", "Classic Fit"],
    "Women's Wear": ["Dress", "Blouse", "Cardigan", "Skirt", "Wide Leg", "Premium Cotton", "Elegant Fit"],
    "Kitchen Appliances": ["Air Fryer", "Rice Cooker", "Blender", "Electric Kettle", "Induction Cooker", "Vacuum Flask", "Multi Cooker"],
    "Skincare": ["Cleanser", "Serum", "Moisturizer", "Sunscreen", "Toner", "Brightening", "Hydrating"],
}

CATEGORY_BRAND_HINTS = {
    "Mobile Phones": {"Samsung", "Apple", "Xiaomi", "Oppo", "Vivo"},
    "Laptops": {"Apple", "Asus", "Lenovo", "Dell", "HP"},
    "Men's Wear": {"Adidas", "Nike", "Puma", "Uniqlo"},
    "Women's Wear": {"Adidas", "Nike", "Puma", "Uniqlo"},
    "Kitchen Appliances": {"Panasonic", "Philips", "LocknLock", "Sunhouse", "LG"},
    "Skincare": {"Philips", "Panasonic", "LG", "Sony"},
}

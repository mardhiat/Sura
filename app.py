# app.py - Sura Hijab Shop
import streamlit as st
from PIL import Image
import os
from pathlib import Path
from datetime import datetime
import json
import hashlib
import random

st.set_page_config(
    page_title="Sura — Elegant Printed Hijabs",
    page_icon="logocircle.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#  CONFIG 
PAYPAL_LINK = "https://www.paypal.me/TheOfficialSura"
CASHAPP_LINK = "https://cash.app/$TheOfficialSura"
ZELLE_INFO = "Phone: +1-862-307-2294"
INSTAGRAM_HANDLE = "@TheOfficial.Sura"
TIKTOK_HANDLE = "@TheOfficial.Sura"
CONTACT_EMAIL = "theofficialsura22@gmail.com"

DEFAULT_PRICE = 10.00
PRICE_OVERRIDE = {}

# USER MANAGEMENT
def load_users():
    users_file = Path("users.json")
    if users_file.exists():
        with open(users_file, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, name):
    users = load_users()
    if email in users:
        return False
    users[email] = {
        "password": hash_password(password),
        "name": name,
        "newsletter": False,
        "orders": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)
    return True

def verify_user(email, password):
    users = load_users()
    if email in users and users[email]["password"] == hash_password(password):
        return True
    return False

def update_newsletter_status(email, status):
    users = load_users()
    if email in users:
        users[email]["newsletter"] = status
        save_users(users)

def add_order_to_user(email, order_data):
    users = load_users()
    if email in users:
        users[email]["orders"].append(order_data)
        save_users(users)

def get_user_orders(email):
    users = load_users()
    if email in users:
        return users[email]["orders"]
    return []

# Shipping calculation rules
def calculate_shipping(bag_items):
    total_items = sum(item["qty"] for item in bag_items)
    subtotal = sum(item["price"] * item["qty"] for item in bag_items)
    
    if total_items >= 5 or subtotal >= 50:
        return 0.00
    
    shipping_rates = {
        1: 6.00,
        2: 7.00,
        3: 8.00,
        4: 9.00
    }
    
    return shipping_rates.get(total_items, 0.00)

PRODUCT_DESCRIPTIONS = {
    "abyss": "Deep, mysterious patterns that evoke the beauty of ocean depths.",
    "acorn": "Warm, earthy tones inspired by autumn's natural elegance.",
    "angelic": "Soft, ethereal prints perfect for everyday grace.",
    "apex": "Bold geometric designs for the stylish, confident woman.",
    "ascent": "Uplifting patterns that celebrate growth and ambition."
}

#  ORDER NOTIFICATION 
def save_order_notification(order_data):
    try:
        orders_file = Path("orders.json")
        orders = []
        
        if orders_file.exists():
            with open(orders_file, 'r') as f:
                orders = json.load(f)
        
        orders.append(order_data)
        
        with open(orders_file, 'w') as f:
            json.dump(orders, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving order: {e}")
        return False

#  HELPER FUNCTIONS 
def load_products_from_folders(root="."):
    products = []
    root_path = Path(root)
    skip_names = {".venv", ".vscode", "__pycache__", ".git", "static"}
    
    for entry in sorted(root_path.iterdir()):
        if entry.is_dir() and entry.name not in skip_names:
            images = [p for p in sorted(entry.iterdir()) 
                     if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".avif", ".webp"}]
            if images:
                name = entry.name.capitalize()
                price = PRICE_OVERRIDE.get(entry.name, DEFAULT_PRICE)
                description = PRODUCT_DESCRIPTIONS.get(entry.name, "Elegant printed hijab with modern style.")
                products.append({
                    "id": entry.name,
                    "name": name,
                    "folder": entry,
                    "images": images,
                    "price": price,
                    "description": description,
                })
    return products

def init_session_state():
    if "bag" not in st.session_state:
        st.session_state.bag = []
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None
    if "current_image_idx" not in st.session_state:
        st.session_state.current_image_idx = {}
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_auth" not in st.session_state:
        st.session_state.show_auth = False
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

def add_to_bag(product):
    for item in st.session_state.bag:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return
    st.session_state.bag.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "image": str(product["images"][0]),
        "qty": 1,
    })

def remove_from_bag(idx):
    if 0 <= idx < len(st.session_state.bag):
        st.session_state.bag.pop(idx)

def update_qty(idx, delta):
    if 0 <= idx < len(st.session_state.bag):
        st.session_state.bag[idx]["qty"] = max(1, st.session_state.bag[idx]["qty"] + delta)

def bag_count():
    return sum(item["qty"] for item in st.session_state.bag)

def bag_subtotal():
    return sum(item["price"] * item["qty"] for item in st.session_state.bag)

def navigate_to(page, product=None):
    st.session_state.page = page
    if product:
        st.session_state.selected_product = product
        st.session_state.current_image_idx[product["id"]] = 0

def next_image(product_id, max_images):
    if product_id not in st.session_state.current_image_idx:
        st.session_state.current_image_idx[product_id] = 0
    st.session_state.current_image_idx[product_id] = (st.session_state.current_image_idx[product_id] + 1) % max_images

def prev_image(product_id, max_images):
    if product_id not in st.session_state.current_image_idx:
        st.session_state.current_image_idx[product_id] = 0
    st.session_state.current_image_idx[product_id] = (st.session_state.current_image_idx[product_id] - 1) % max_images

#  STYLING 
st.markdown("""
<style>
    /* Global styles */
    .main { background-color: #FFFFFF; }
    .block-container { 
        padding-top: 2rem !important; 
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Center content on home page */
    .stMarkdown, .stMarkdown > div {
        text-align: center;
    }
    
    /* Center columns content */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* Typography */
    h1, h2, h3 { 
        color: #111111; 
        font-weight: 600; 
        text-align: center !important; 
    }
    p { 
        color: #666666; 
        line-height: 1.6; 
        text-align: center;
    }
    
    /* Responsive typography */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }
    }
    
    /* Logo */
    .logo-img {
        cursor: pointer;
        transition: opacity 0.2s;
        max-width: 120px;
    }
    
    .logo-img:hover {
        opacity: 0.7;
    }
    
    /* Navigation bar spacing */
    .nav-spacing {
        margin-top: 1cm;
        margin-bottom: 1rem;
    }
    
 /* Hide hamburger on desktop */
    .hamburger-btn {
        display: none;
    }
    
    @media (max-width: 768px) {
        .desktop-nav {
            display: none !important;
        }
        
        .hamburger-btn {
            display: block !important;
        }
    }
    
    /* Navigation buttons ONLY - minimal style with underline */
    .nav-spacing .stButton > button {
        background-color: transparent !important;
        color: #111111 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    
    .nav-spacing .stButton > button:hover {
        background-color: transparent !important;
        color: #111111 !important;
        border-bottom: 2px solid #111111 !important;
        font-weight: 700 !important;
    }
            
    }
    
    [data-testid="column"] .stButton > button[kind="secondary"]:hover {
        background-color: transparent !important;
        color: #111111 !important;
        border-bottom: 2px solid #111111 !important;
        font-weight: 700 !important;
    }
    
    /* Active navigation button */
    .active-nav-btn {
        border-bottom: 2px solid #111111 !important;
    }
    
    /* Regular action buttons - with borders */
    .stButton > button {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #111111 !important;
        border-radius: 0px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 2px solid #111111 !important;
        font-weight: 700 !important;
    }
    
    /* Product cards */
    .product-card {
        background: #FFFFFF;
        border-radius: 0px !important;
        padding: 16px;
        border: 2px solid #111111;
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .product-card:hover {
        background: #f5f5f5;
        border: 2px solid #111111;
    }
    
    @media (max-width: 768px) {
        .product-card {
            padding: 12px;
        }
    }
    
    .product-image {
        border-radius: 0px !important;
        margin-bottom: 12px;
        width: 100%;
        aspect-ratio: 1;
        object-fit: cover;
        border: 1px solid #e0e0e0;
    }
    
    /* All images sharp */
    .stImage, .stImage img, img {
        border-radius: 0px !important;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center !important;
        padding: 3rem 1rem;
        background: transparent;
        border: none;
        margin-bottom: 3rem;
        width: 100%;
    }
    
    @media (max-width: 768px) {
        .hero-section {
            padding: 2rem 1rem;
            margin-bottom: 2rem;
        }
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 0.5rem;
        text-align: center !important;
    }
    
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #666666;
        margin-bottom: 1rem;
        text-align: center !important;
    }
    
    @media (max-width: 768px) {
        .hero-subtitle {
            font-size: 1.2rem;
        }
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: #666666;
        max-width: 600px;
        margin: 0 auto 2rem;
        line-height: 1.8;
        text-align: center !important;
    }
    
    @media (max-width: 768px) {
        .hero-description {
            font-size: 1rem;
        }
    }
    
    /* Info boxes */
    .info-box {
        background: #f5f5f5;
        border: 2px solid #111111;
        border-radius: 0px !important;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Bag items */
    .bag-item {
        background: #FFFFFF;
        border: 2px solid #111111;
        border-radius: 0px !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    @media (max-width: 768px) {
        .bag-item {
            padding: 0.75rem;
        }
    }
    
    /* Carousel indicator */
    .carousel-indicator {
        text-align: center;
        margin-top: 10px;
        color: #666666;
        font-size: 0.9rem;
    }
    
    /* Auth modal overlay */
    .auth-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Auth modal */
    .auth-modal {
        background: #FFFFFF;
        border: 2px solid #111111;
        padding: 2rem;
        max-width: 450px;
        width: 90%;
        margin: 0 auto;
        position: relative;
        z-index: 1000;
        max-height: 90vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

#  INITIALIZE 
init_session_state()
products = load_products_from_folders(".")

# AUTH MODAL (render first so it appears on top)
if st.session_state.show_auth and not st.session_state.user:
    st.markdown('<div class="auth-overlay"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-modal">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### Sign In to Your Account")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if verify_user(email, password):
                        st.session_state.user = email
                        st.session_state.show_auth = False
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
        
        with tab2:
            with st.form("signup_form"):
                st.markdown("### Create Your Account")
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                newsletter = st.checkbox("Subscribe to our newsletter for updates and exclusive offers")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif create_user(email, password, name):
                        st.session_state.user = email
                        if newsletter:
                            update_newsletter_status(email, True)
                        st.session_state.show_auth = False
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Email already exists")
        
        if st.button("✕ Close", key="close_auth", use_container_width=True):
            st.session_state.show_auth = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

#  HEADER
header_col1, header_col2, header_col3 = st.columns([1, 4, 1])

with header_col1:
    if Path("Logocircle.png").exists():
        try:
            logo_img = Image.open("Logocircle.png")
            st.image(logo_img, width=100)
        except:
            st.markdown("**SURA**")
    else:
        st.markdown("**SURA**")

with header_col2:
    # Desktop Navigation
    st.markdown('<div class="nav-spacing desktop-nav">', unsafe_allow_html=True)
    nav_cols = st.columns(5)
    
    with nav_cols[0]:
        if st.button("Home", key="nav_home", type="secondary", use_container_width=True):
            navigate_to("home")
            st.rerun()
        if st.session_state.page == "home":
            st.markdown('<style>[data-testid="column"]:nth-child(1) .stButton > button { border-bottom: 2px solid #111111 !important; }</style>', unsafe_allow_html=True)
    
    with nav_cols[1]:
        if st.button("Shop", key="nav_shop", type="secondary", use_container_width=True):
            navigate_to("shop")
            st.rerun()
    
    with nav_cols[2]:
        if st.button("About", key="nav_about", type="secondary", use_container_width=True):
            navigate_to("about")
            st.rerun()
    
    with nav_cols[3]:
        if st.button("Returns", key="nav_returns", type="secondary", use_container_width=True):
            navigate_to("returns")
            st.rerun()
    
    with nav_cols[4]:
        bag_btn_label = f"Bag ({bag_count()})" if bag_count() > 0 else "Bag"
        if st.button(bag_btn_label, key="nav_bag", type="secondary", use_container_width=True):
            navigate_to("bag")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mobile Hamburger
    st.markdown('<div class="hamburger-btn">', unsafe_allow_html=True)
    if st.button("☰ Menu", key="hamburger"):
        st.session_state.mobile_menu_open = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with header_col3:
    st.markdown('<div class="nav-spacing">', unsafe_allow_html=True)
    if st.session_state.user:
        users = load_users()
        user_data = users[st.session_state.user]
        if st.button(f"👤 {user_data['name']}", key="user_menu", type="secondary"):
            navigate_to("account")
            st.rerun()
    else:
        if st.button("Sign In", key="show_auth_btn", type="secondary"):
            st.session_state.show_auth = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

#  PAGES 

# ---------- HOME PAGE ----------
if st.session_state.page == "home":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Sura — Elegant Printed Hijabs</h1>
        <p class="hero-subtitle">Modern prints. Soft fabrics. Everyday modesty.</p>
        <p class="hero-description">
            Welcome to Sura — a small boutique making bold, printed hijabs for confident, everyday style. 
            Each design is thoughtfully printed on soft, breathable fabric for comfort that lasts from dawn 
            prayers to evening plans. Simple, timeless, and made for you.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Shop Printed Hijabs", key="hero_cta", use_container_width=True):
            navigate_to("shop")
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Featured products
    if products:
        st.markdown("### Featured Collections")
        cols = st.columns([1, 1, 1] if len(products) >= 3 else [1] * len(products))
        for i, product in enumerate(products[:3]):
            with cols[i]:
                try:
                    img = Image.open(product["images"][0])
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"${product['price']:.2f}")
                    if st.button("View Details", key=f"featured_{product['id']}", use_container_width=True):
                        navigate_to("product", product)
                        st.rerun()
                except Exception as e:
                    st.error("Image loading error")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Benefits
    st.markdown("### Why Choose Sura?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Quality Fabrics**")
        st.write("Soft, breathable materials perfect for all-day wear")
    with col2:
        st.markdown("**Modern Designs**")
        st.write("Thoughtfully curated prints that match your style")
    with col3:
        st.markdown("**Small Batch**")
        st.write("Limited quantities ensure exclusivity and care")

# ---------- SHOP PAGE ----------
elif st.session_state.page == "shop":
    st.markdown("## Shop All Hijabs")
    st.markdown("Each hijab is \$10 | Free shipping on orders \$50+ or 5+ items")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not products:
        st.warning("No products available at the moment. Please check back soon!")
    else:
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                try:
                    img = Image.open(product["images"][0])
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"<p style='color:#666666;font-size:0.9rem;text-align:center'>{product['description']}</p>", unsafe_allow_html=True)
                    st.markdown(f"**${product['price']:.2f}**")
                    if st.button("View Details", key=f"view_{product['id']}", use_container_width=True):
                        navigate_to("product", product)
                        st.rerun()
                    if st.button(f"Add to Bag", key=f"add_{product['id']}", use_container_width=True):
                        add_to_bag(product)
                        st.success(f"{product['name']} added to bag!")
                        st.rerun()
                except Exception as e:
                    st.error("Image error")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

# ---------- PRODUCT DETAIL PAGE ----------
elif st.session_state.page == "product" and st.session_state.selected_product:
    product = st.session_state.selected_product
    
    if st.button("← Back to Shop", key="back_to_shop"):
        navigate_to("shop")
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if len(product["images"]) > 1:
            current_idx = st.session_state.current_image_idx.get(product["id"], 0)
            
            btn_col1, img_col, btn_col2 = st.columns([1, 8, 1])
            
            with btn_col1:
                if st.button("‹", key="prev_img"):
                    prev_image(product["id"], len(product["images"]))
                    st.rerun()
            
            with img_col:
                img = Image.open(product["images"][current_idx])
                st.image(img, use_container_width=True)
            
            with btn_col2:
                if st.button("›", key="next_img"):
                    next_image(product["id"], len(product["images"]))
                    st.rerun()
            
            st.markdown(f"<p class='carousel-indicator'>{current_idx + 1} / {len(product['images'])}</p>", unsafe_allow_html=True)
        else:
            img = Image.open(product["images"][0])
            st.image(img, use_container_width=True)
    
    with col2:
        st.markdown(f"## {product['name']}")
        st.markdown(f"### ${product['price']:.2f}")
        st.markdown(f"<p style='text-align:center'>{product['description']}</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**Details:**")
        st.markdown("- Premium printed fabric")
        st.markdown("- Soft and breathable")
        st.markdown("- Perfect for everyday wear")
        st.markdown("- Ships within 1-2 days")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Add to Bag — $" + str(int(product['price'])), key="add_detail", use_container_width=True):
            add_to_bag(product)
            st.success(f"Added to bag!")
            st.rerun()

# ---------- BAG PAGE ----------
elif st.session_state.page == "bag":
    st.markdown("## Shopping Bag")
    
    if bag_count() == 0:
        st.info("Your bag is empty. Browse our collection and add some beautiful hijabs!")
        if st.button("Continue Shopping"):
            navigate_to("shop")
            st.rerun()
    else:
        for idx, item in enumerate(st.session_state.bag):
            st.markdown("<div class='bag-item'>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                if Path(item["image"]).exists():
                    try:
                        st.image(item["image"], width=80)
                    except:
                        pass
            
            with col2:
                st.markdown(f"<p style='text-align:left'><strong>{item['name']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:left'>${item['price']:.2f} each</p>", unsafe_allow_html=True)
            
            with col3:
                qty_col1, qty_col2, qty_col3 = st.columns([1, 2, 1])
                with qty_col1:
                    if st.button("−", key=f"minus_{idx}"):
                        if item["qty"] > 1:
                            update_qty(idx, -1)
                        else:
                            remove_from_bag(idx)
                        st.rerun()
                with qty_col2:
                    st.markdown(f"<p style='text-align:center;margin-top:8px'>{item['qty']}</p>", unsafe_allow_html=True)
                with qty_col3:
                    if st.button("+", key=f"plus_{idx}"):
                        update_qty(idx, 1)
                        st.rerun()
            
            with col4:
                if st.button("Remove", key=f"remove_{idx}"):
                    remove_from_bag(idx)
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculate shipping
        shipping = calculate_shipping(st.session_state.bag)
        subtotal = bag_subtotal()
        total = subtotal + shipping
        
        # Bag summary
        col1, col2 = st.columns([2, 1])
        with col2:
            st.markdown(f"**Subtotal:** ${subtotal:.2f}")
            if shipping == 0:
                st.markdown(f"**Shipping:** FREE")
            else:
                st.markdown(f"**Shipping:** ${shipping:.2f}")
            st.markdown(f"### Total: ${total:.2f}")
            
            if bag_count() < 5 and subtotal < 50:
                st.markdown(f"<small>Add {5 - bag_count()} more items or ${50 - subtotal:.2f} for free shipping!</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Checkout form
        st.markdown("### Shipping Information")
        
        with st.form("checkout_form"):
            if st.session_state.user:
                users = load_users()
                user_data = users[st.session_state.user]
                name = st.text_input("Full Name *", value=user_data['name'])
                email = st.text_input("Email *", value=st.session_state.user, disabled=True)
            else:
                name = st.text_input("Full Name *", placeholder="Your name")
                email = st.text_input("Email *", placeholder="your@email.com")
            
            phone = st.text_input("Phone Number *", placeholder="+1-555-555-5555")
            address = st.text_area("Shipping Address *", placeholder="Street Address, City, State, ZIP Code")
            notes = st.text_area("Order Notes (Optional)", placeholder="Any special requests or preferences?")
            
            submitted = st.form_submit_button("Proceed to Payment", use_container_width=True)
            
            if submitted:
                if name and phone and email and address:
                    order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                    st.session_state.order_info = {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "notes": notes,
                        "subtotal": subtotal,
                        "shipping": shipping,
                        "total": total,
                        "items": st.session_state.bag.copy(),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "order_id": order_id,
                        "status": "Pending Payment"
                    }
                    navigate_to("payment")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")

# ---------- PAYMENT PAGE ----------
elif st.session_state.page == "payment":
    st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
    if "order_info" not in st.session_state:
        st.warning("No order information found. Please complete checkout first.")
        navigate_to("bag")
        st.rerun()
    else:
        order = st.session_state.order_info
        
        st.markdown("## Complete Your Payment")
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown(f"**Order ID:** {order['order_id']}")
        st.markdown(f"**Order Total: ${order['total']:.2f}**")
        st.markdown(f"- Subtotal: ${order['subtotal']:.2f}")
        st.markdown(f"- Shipping: ${order['shipping']:.2f}" if order['shipping'] > 0 else "- Shipping: FREE")
        st.markdown(f"**Name:** {order['name']}")
        st.markdown(f"**Email:** {order['email']}")
        st.markdown(f"**Phone:** {order['phone']}")
        st.markdown(f"**Shipping to:** {order['address']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### Choose Your Payment Method")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### PayPal")
            if "paypal.me" in PAYPAL_LINK.lower() or "paypal.com" in PAYPAL_LINK.lower():
                paypal_url = PAYPAL_LINK.rstrip("/") + f"/{int(order['total'])}"
                st.markdown(f"[Pay ${order['total']:.2f} via PayPal]({paypal_url})")
            else:
                st.markdown("*PayPal link not configured*")
        
        with col2:
            st.markdown("#### CashApp")
            if "cash.app" in CASHAPP_LINK.lower():
                st.markdown(f"[Pay ${order['total']:.2f} via CashApp]({CASHAPP_LINK})")
            else:
                st.markdown("*CashApp link not configured*")
        
        with col3:
            st.markdown("#### Zelle")
            st.markdown(f"**Send ${order['total']:.2f} to:**")
            st.markdown(f"<small>{ZELLE_INFO}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### Important:")
        st.markdown(f"""
        - Complete payment using one of the methods above
        - Include your **Order ID: {order['order_id']}** in the payment note if possible
        - We will verify your payment and send you a confirmation email within 24 hours
        - Your order will ship within 1-2 business days after payment confirmation
        - Delivery time depends on your location
        
        **No need to contact us** — we'll reach out to you once we confirm your payment!
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("I've Completed Payment", use_container_width=True):
            # Save order notification
            if save_order_notification(order):
                # Add order to user account if logged in
                if st.session_state.user:
                    add_order_to_user(st.session_state.user, order)
                
                st.session_state.bag = []
                st.session_state.order_complete = True
                navigate_to("confirmation")
                st.rerun()
            else:
                st.error("There was an issue saving your order. Please contact us directly.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- ORDER CONFIRMATION ----------
elif st.session_state.page == "confirmation":
    st.markdown("## Thank You for Your Order!")
    
    st.success("Your order has been placed successfully!")
    
    if "order_info" in st.session_state:
        order = st.session_state.order_info
        st.markdown(f"### Order ID: {order['order_id']}")
    
    st.markdown("""
    ### What Happens Next?
    
    1. We'll verify your payment within 24 hours
    2. You'll receive a confirmation email with tracking information
    3. Your order will ship within 1-2 business days
    4. Delivery time depends on your proximity to us
    
    ### Questions?
    
    Feel free to reach out:
    - **Email:** theofficialsura22@gmail.com
    - **Instagram:** @TheOfficial.Sura
    
    Thank you for supporting Sura!
    """)
    
    if st.button("Return to Shop", use_container_width=True):
        navigate_to("shop")
        st.rerun()

# ---------- ACCOUNT PAGE ----------
elif st.session_state.page == "account":
    if not st.session_state.user:
        st.warning("Please sign in to view your account.")
        navigate_to("home")
        st.rerun()
    else:
        users = load_users()
        user_data = users[st.session_state.user]
        
        st.markdown(f"## Welcome, {user_data['name']}!")
        
        tab1, tab2, tab3 = st.tabs(["Orders", "Newsletter", "Account Settings"])
        
        with tab1:
            st.markdown("### Your Orders")
            orders = user_data.get("orders", [])
            
            if not orders:
                st.info("You haven't placed any orders yet.")
                if st.button("Start Shopping"):
                    navigate_to("shop")
                    st.rerun()
            else:
                for order in reversed(orders):
                    with st.expander(f"Order {order['order_id']} - ${order['total']:.2f} - {order['date']}"):
                        st.markdown(f"**Status:** {order.get('status', 'Processing')}")
                        st.markdown(f"**Total:** ${order['total']:.2f}")
                        st.markdown(f"**Shipping:** ${order['shipping']:.2f}" if order['shipping'] > 0 else "**Shipping:** FREE")
                        st.markdown("**Items:**")
                        for item in order['items']:
                            st.markdown(f"- {item['name']} x{item['qty']} - ${item['price'] * item['qty']:.2f}")
                        st.markdown(f"**Shipping Address:** {order['address']}")
        
        with tab2:
            st.markdown("### Newsletter Subscription")
            
            current_status = user_data.get("newsletter", False)
            
            newsletter_opt = st.checkbox("Subscribe to newsletter", value=current_status)
            
            if st.button("Update Newsletter Preference"):
                update_newsletter_status(st.session_state.user, newsletter_opt)
                st.success("Newsletter preference updated!")
                st.rerun()
            
            st.markdown("---")
            st.markdown("Stay updated with:")
            st.markdown("- New hijab collections")
            st.markdown("- Exclusive discounts")
            st.markdown("- Style tips and inspiration")
            st.markdown("- Early access to sales")
        
        with tab3:
            st.markdown("### Account Settings")
            st.markdown(f"**Email:** {st.session_state.user}")
            st.markdown(f"**Member since:** {user_data.get('created_at', 'N/A')}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign Out", use_container_width=True):
                st.session_state.user = None
                st.success("You've been signed out.")
                navigate_to("home")
                st.rerun()

# ---------- ABOUT PAGE ----------
elif st.session_state.page == "about":
    st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
    st.markdown("## About Sura")
    
    st.markdown(f"""
    ### Our Story
    
    Sura was born from a simple belief: modesty and style should go hand in hand. We create 
    printed hijabs that celebrate stylish Muslim women — confident, creative, and unapologetically themselves.
    
    Each design is carefully curated and printed on premium fabrics that feel as good as they look. 
    From bold geometrics to soft florals, our collections are designed for real life — 
    whether you're heading to work, meeting friends, or simply living your best day.
    
    ### Our Values
    
    **Quality First** — We use only soft, breathable fabrics that are comfortable all day long.
    
    **Thoughtful Design** — Every print is chosen to complement your wardrobe and express your personality.
    
    **Small Batch** — We produce in limited quantities to ensure quality and reduce waste.
    
    **Fast Shipping** — We ship within 1-2 business days of payment confirmation.
    
    **Community** — Supporting modest fashion means supporting each other.
    
    ### Shipping Information
    
    - **Shipping Rates:**
      - 1 hijab: $6
      - 2 hijabs: $7
      - 3 hijabs: $8
      - 4 hijabs: $9
      - 5+ hijabs or $50+ orders: FREE SHIPPING
    
    - **Processing:** 1-2 business days
    - **Delivery:** Depends on your location
    
    ### Connect With Us
    
    Follow our journey on Instagram {INSTAGRAM_HANDLE} or TikTok {TIKTOK_HANDLE} for styling tips, new releases, and behind-the-scenes content.
    
    Questions? Email us at {CONTACT_EMAIL} — we'd love to hear from you!
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- RETURNS PAGE ----------
elif st.session_state.page == "returns":
    st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
    st.markdown("## Returns & Exchanges")
    
    st.markdown(f"""
    ### Our Policy
    
    We want you to love your Sura hijab! If you're not completely satisfied, we're here to help.
    
    ### Returns
    
    - Contact us within **7 days** of delivery
    - Items must be **unworn, unwashed, and in original condition**
    - Original tags and packaging must be intact
    - We'll arrange a return and provide store credit or exchange
    
    ### Exchanges
    
    - Available for different designs within the same price range
    - Item must be in original, unworn condition
    - Contact us to arrange an exchange
    
    ### How to Initiate a Return or Exchange
    
    1. Email us at **{CONTACT_EMAIL}** within 7 days of delivery
    2. Include your order ID and purchase details
    3. Let us know if you'd like store credit or an exchange
    4. We'll provide instructions for return
    
    ### Important Notes
    
    - Hijabs that have been worn, washed, or altered cannot be returned
    - Customer is responsible for return shipping costs unless item is defective
    - Refunds will be issued as store credit within 3-5 business days of receiving returned item
    - Original shipping charges are non-refundable
    
    ### Damaged or Defective Items
    
    If you receive a damaged or defective item:
    - Contact us immediately at {CONTACT_EMAIL}
    - Include photos of the damage/defect
    - We'll send a replacement at no additional cost
    
    ### Questions?
    
    Reach out anytime:
    - **Email:** {CONTACT_EMAIL}
    - **Instagram:** {INSTAGRAM_HANDLE}
    
    We typically respond within 24 hours and will work with you to ensure you're happy with your purchase.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

#  FOOTER 
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# Centered footer
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("**Quick Links**")
    if st.button("Shop", key="footer_shop", use_container_width=True):
        navigate_to("shop")
        st.rerun()
    if st.button("About", key="footer_about", use_container_width=True):
        navigate_to("about")
        st.rerun()
    if st.button("Returns", key="footer_returns", use_container_width=True):
        navigate_to("returns")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with footer_col2:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("**Sura Hijabs**")
    st.markdown("Elegant printed hijabs for stylish women")
    st.markdown("</div>", unsafe_allow_html=True)

with footer_col3:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("**Contact**")
    st.markdown(f"{CONTACT_EMAIL}")
    st.markdown("Ships within 1-2 days")
    st.markdown("Free shipping on $50+")
    st.markdown(f"Instagram: {INSTAGRAM_HANDLE}")
    st.markdown(f"TikTok: {TIKTOK_HANDLE}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#999;font-size:0.85rem;margin-top:2rem'>© 2025 Sura. Made with love.</p>", unsafe_allow_html=True)
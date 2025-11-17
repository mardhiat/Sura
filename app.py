# app.py - Sura Hijab Shop
import streamlit as st
from PIL import Image
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Sura — Elegant Printed Hijabs",
    page_icon="🧕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CONFIG ====================
PAYPAL_LINK = "https://www.paypal.me/YourShop"
CASHAPP_LINK = "https://cash.app/$YourCashtag"
ZELLE_INFO = "Email: sura@example.com | Phone: +1-555-555-5555"
INSTAGRAM_HANDLE = "@CuriositySisters"
CONTACT_EMAIL = "sura@example.com"

DEFAULT_PRICE = 10.00
PRICE_OVERRIDE = {}

PRODUCT_DESCRIPTIONS = {
    "abyss": "Deep, mysterious patterns that evoke the beauty of ocean depths.",
    "acorn": "Warm, earthy tones inspired by autumn's natural elegance.",
    "angelic": "Soft, ethereal prints perfect for everyday grace.",
    "apex": "Bold geometric designs for the modern, confident woman.",
    "ascent": "Uplifting patterns that celebrate growth and ambition."
}

# ==================== HELPER FUNCTIONS ====================
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
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return
    st.session_state.cart.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "image": str(product["images"][0]),
        "qty": 1,
    })

def remove_from_cart(idx):
    if 0 <= idx < len(st.session_state.cart):
        st.session_state.cart.pop(idx)

def update_qty(idx, delta):
    if 0 <= idx < len(st.session_state.cart):
        st.session_state.cart[idx]["qty"] = max(1, st.session_state.cart[idx]["qty"] + delta)

def cart_count():
    return sum(item["qty"] for item in st.session_state.cart)

def cart_subtotal():
    return sum(item["price"] * item["qty"] for item in st.session_state.cart)

def navigate_to(page, product=None):
    st.session_state.page = page
    if product:
        st.session_state.selected_product = product

# ==================== STYLING ====================
st.markdown("""
<style>
    /* Global styles */
    .main { background-color: #FFFFFF; }
    .block-container { padding-top: 2rem !important; max-width: 1200px; }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3 { color: #111111; font-weight: 600; }
    p { color: #666666; line-height: 1.6; }
    
    /* Header */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #FFC6D1 !important;
        color: #111111 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #ffb3c1 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 198, 209, 0.4);
    }
    
    /* Product cards */
    .product-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .product-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-4px);
    }
    
    .product-image {
        border-radius: 8px;
        margin-bottom: 12px;
        width: 100%;
        aspect-ratio: 1;
        object-fit: cover;
    }
    
    /* Cart badge */
    .cart-badge {
        background-color: #FFC6D1;
        color: #111111;
        border-radius: 50%;
        padding: 4px 10px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #ffffff 0%, #fff5f7 100%);
        border-radius: 16px;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #666666;
        margin-bottom: 1rem;
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: #666666;
        max-width: 600px;
        margin: 0 auto 2rem;
        line-height: 1.8;
    }
    
    /* Navigation */
    .nav-link {
        color: #666666;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 6px;
        transition: all 0.2s;
        display: inline-block;
        margin: 0 4px;
    }
    
    .nav-link:hover {
        background-color: #fff5f7;
        color: #111111;
    }
    
    /* Info boxes */
    .info-box {
        background: #fff5f7;
        border-left: 4px solid #FFC6D1;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Cart items */
    .cart-item {
        background: #FFFFFF;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZE ====================
init_session_state()
products = load_products_from_folders(".")

# ==================== HEADER / NAVIGATION ====================
col1, col2, col3 = st.columns([2, 3, 2])

with col1:
    if Path("logo.avif").exists():
        try:
            logo_img = Image.open("logo.avif")
            st.image(logo_img, width=120)
        except:
            st.markdown("<h2 style='margin:0'>Sura</h2>", unsafe_allow_html=True)
    else:
        if st.button("← Sura", key="home_btn", use_container_width=False):
            navigate_to("home")

with col2:
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button("Shop", key="nav_shop", use_container_width=True):
            navigate_to("shop")
    with nav_col2:
        if st.button("About", key="nav_about", use_container_width=True):
            navigate_to("about")
    with nav_col3:
        if st.button("Care Guide", key="nav_care", use_container_width=True):
            navigate_to("care")

with col3:
    cart_btn_label = f"Cart ({cart_count()})" if cart_count() > 0 else "Cart"
    if st.button(cart_btn_label, key="nav_cart", use_container_width=True):
        navigate_to("cart")

st.markdown("---")

# ==================== PAGES ====================

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Featured products
    if products:
        st.markdown("### Featured Collections")
        cols = st.columns(min(3, len(products)))
        for i, product in enumerate(products[:3]):
            with cols[i]:
                try:
                    img = Image.open(product["images"][0])
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"${product['price']:.2f}")
                    if st.button("View Details", key=f"featured_{product['id']}", use_container_width=True):
                        navigate_to("product", product)
                except Exception as e:
                    st.error("Image loading error")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Benefits
    st.markdown("### Why Choose Sura?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🌟 Quality Fabrics**")
        st.write("Soft, breathable materials perfect for all-day wear")
    with col2:
        st.markdown("**🎨 Modern Designs**")
        st.write("Thoughtfully curated prints that match your style")
    with col3:
        st.markdown("**💝 Small Batch**")
        st.write("Limited quantities ensure exclusivity and care")

# ---------- SHOP PAGE ----------
elif st.session_state.page == "shop":
    st.markdown("## Shop All Hijabs")
    st.markdown("*Each hijab is priced at $10 with free local pickup*")
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
                    if st.button("🔍", key=f"view_{product['id']}", help="View details"):
                        navigate_to("product", product)
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"<p style='color:#666666;font-size:0.9rem'>{product['description']}</p>", unsafe_allow_html=True)
                    st.markdown(f"**${product['price']:.2f}**")
                    if st.button(f"Add to Cart", key=f"add_{product['id']}", use_container_width=True):
                        add_to_cart(product)
                        st.success(f"✓ {product['name']} added to cart!")
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Image gallery
        if len(product["images"]) > 1:
            selected_img = st.select_slider(
                "View images",
                options=range(len(product["images"])),
                format_func=lambda x: f"Image {x+1}",
                label_visibility="collapsed"
            )
            img = Image.open(product["images"][selected_img])
        else:
            img = Image.open(product["images"][0])
        
        st.image(img, use_container_width=True)
    
    with col2:
        st.markdown(f"## {product['name']}")
        st.markdown(f"### ${product['price']:.2f}")
        st.markdown(f"{product['description']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**Details:**")
        st.markdown("- Premium printed fabric")
        st.markdown("- Soft and breathable")
        st.markdown("- Perfect for everyday wear")
        st.markdown("- Free local pickup")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Add to Cart — $" + str(int(product['price'])), key="add_detail", use_container_width=True):
            add_to_cart(product)
            st.success(f"✓ Added to cart!")
            st.rerun()

# ---------- CART PAGE ----------
elif st.session_state.page == "cart":
    st.markdown("## Shopping Cart")
    
    if cart_count() == 0:
        st.info("Your cart is empty. Browse our collection and add some beautiful hijabs!")
        if st.button("Continue Shopping"):
            navigate_to("shop")
    else:
        # Display cart items
        for idx, item in enumerate(st.session_state.cart):
            st.markdown("<div class='cart-item'>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                if Path(item["image"]).exists():
                    try:
                        st.image(item["image"], width=80)
                    except:
                        st.write("📦")
            
            with col2:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"${item['price']:.2f} each")
            
            with col3:
                qty_col1, qty_col2, qty_col3 = st.columns([1, 2, 1])
                with qty_col1:
                    if st.button("−", key=f"minus_{idx}"):
                        if item["qty"] > 1:
                            update_qty(idx, -1)
                        else:
                            remove_from_cart(idx)
                        st.rerun()
                with qty_col2:
                    st.markdown(f"<p style='text-align:center;margin-top:8px'>{item['qty']}</p>", unsafe_allow_html=True)
                with qty_col3:
                    if st.button("+", key=f"plus_{idx}"):
                        update_qty(idx, 1)
                        st.rerun()
            
            with col4:
                if st.button("🗑️", key=f"remove_{idx}"):
                    remove_from_cart(idx)
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Cart summary
        col1, col2 = st.columns([2, 1])
        with col2:
            st.markdown(f"### Subtotal: ${cart_subtotal():.2f}")
            st.markdown("*Free local pickup*")
        
        st.markdown("---")
        
        # Checkout form
        st.markdown("### Checkout Information")
        
        with st.form("checkout_form"):
            name = st.text_input("Full Name *", placeholder="Your name")
            phone = st.text_input("Phone Number *", placeholder="+1-555-555-5555")
            email = st.text_input("Email", placeholder="your@email.com")
            
            delivery_method = st.radio(
                "Delivery Method",
                ["Local Pickup (Free)", "Shipping ($5)"],
                index=0
            )
            
            if "Shipping" in delivery_method:
                address = st.text_area("Shipping Address *", placeholder="Street, City, State, ZIP")
                total = cart_subtotal() + 5.00
            else:
                address = ""
                total = cart_subtotal()
            
            notes = st.text_area("Order Notes (Optional)", placeholder="Any special requests or preferences?")
            
            submitted = st.form_submit_button("Proceed to Payment", use_container_width=True)
            
            if submitted:
                if name and phone:
                    st.session_state.order_info = {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "delivery": delivery_method,
                        "address": address,
                        "notes": notes,
                        "total": total,
                        "items": st.session_state.cart.copy(),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    navigate_to("payment")
                    st.rerun()
                else:
                    st.error("Please fill in required fields (Name and Phone)")

# ---------- PAYMENT PAGE ----------
elif st.session_state.page == "payment":
    if "order_info" not in st.session_state:
        st.warning("No order information found. Please complete checkout first.")
        navigate_to("cart")
        st.rerun()
    else:
        order = st.session_state.order_info
        
        st.markdown("## Complete Your Payment")
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown(f"**Order Total: ${order['total']:.2f}**")
        st.markdown(f"**Name:** {order['name']}")
        st.markdown(f"**Phone:** {order['phone']}")
        if order['delivery']:
            st.markdown(f"**Delivery:** {order['delivery']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### Choose Your Payment Method")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### PayPal")
            if "paypal.me" in PAYPAL_LINK.lower() or "paypal.com" in PAYPAL_LINK.lower():
                paypal_url = PAYPAL_LINK.rstrip("/") + f"/{int(order['total'])}"
                st.markdown(f"[Pay ${order['total']:.2f} via PayPal]({paypal_url})")
            else:
                st.markdown("*Update PayPal link in config*")
        
        with col2:
            st.markdown("#### CashApp")
            if "cash.app" in CASHAPP_LINK.lower():
                st.markdown(f"[Pay ${order['total']:.2f} via CashApp]({CASHAPP_LINK})")
            else:
                st.markdown("*Update CashApp link in config*")
        
        with col3:
            st.markdown("#### Zelle")
            st.markdown(f"**Send ${order['total']:.2f} to:**")
            st.markdown(f"<small>{ZELLE_INFO}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### 📱 After Payment:")
        st.markdown(f"""
        1. Complete payment using one of the methods above
        2. Take a screenshot or note your transaction ID
        3. **Contact us immediately:**
           - Instagram: {INSTAGRAM_HANDLE}
           - Email: {CONTACT_EMAIL}
        4. Include your name: **{order['name']}** and payment confirmation
        
        We'll prepare your order and contact you within 24 hours!
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("I've Completed Payment — Clear Cart", use_container_width=True):
            st.session_state.cart = []
            st.session_state.order_complete = True
            navigate_to("confirmation")
            st.rerun()

# ---------- ORDER CONFIRMATION ----------
elif st.session_state.page == "confirmation":
    st.markdown("## 🎉 Thank You!")
    
    st.success("Your order has been received!")
    
    st.markdown("""
    ### What's Next?
    
    1. **We're waiting for your payment confirmation** — please send us a message with your payment details
    2. We'll verify payment and prepare your order
    3. You'll receive a confirmation message within 24 hours
    4. Pick up or delivery will be coordinated via phone
    
    ### Contact Us:
    - **Instagram:** {INSTAGRAM_HANDLE}
    - **Email:** {CONTACT_EMAIL}
    
    Thank you for supporting Sura! 💕
    """.format(INSTAGRAM_HANDLE=INSTAGRAM_HANDLE, CONTACT_EMAIL=CONTACT_EMAIL))
    
    if st.button("Return to Shop", use_container_width=True):
        navigate_to("shop")
        st.rerun()

# ---------- ABOUT PAGE ----------
elif st.session_state.page == "about":
    st.markdown("## About Sura")
    
    st.markdown("""
    ### Our Story
    
    Sura was born from a simple belief: modesty and style should go hand in hand. We create 
    printed hijabs that celebrate modern Muslim women — confident, creative, and unapologetically themselves.
    
    Each design is carefully curated and printed on premium fabrics that feel as good as they look. 
    From bold geometrics to soft florals, our collections are designed for real life — 
    whether you're heading to work, meeting friends, or simply living your best day.
    
    ### Our Values
    
    **Quality First** — We use only soft, breathable fabrics that are comfortable all day long.
    
    **Thoughtful Design** — Every print is chosen to complement your wardrobe and express your personality.
    
    **Small Batch** — We produce in limited quantities to ensure quality and reduce waste.
    
    **Community** — Supporting modest fashion means supporting each other.
    
    ### Connect With Us
    
    Follow our journey on Instagram {INSTAGRAM_HANDLE} for styling tips, new releases, and behind-the-scenes content.
    
    Questions? Email us at {CONTACT_EMAIL} — we'd love to hear from you!
    """.format(INSTAGRAM_HANDLE=INSTAGRAM_HANDLE, CONTACT_EMAIL=CONTACT_EMAIL))

# ---------- CARE GUIDE PAGE ----------
elif st.session_state.page == "care":
    st.markdown("## Hijab Care Guide")
    
    st.markdown("""
    ### How to Care for Your Sura Hijab
    
    To keep your printed hijabs looking beautiful wash after wash, follow these simple care instructions:
    
    #### Washing
    - **Hand wash** in cool water for best results
    - **Machine wash** on delicate cycle (cold water) if needed
    - Use mild detergent — avoid bleach or harsh chemicals
    - Wash similar colors together to prevent bleeding
    
    #### Drying
    - Air dry flat or hang to dry
    - Avoid direct sunlight to preserve colors
    - Do not tumble dry (high heat can damage prints)
    
    #### Ironing
    - Iron on low to medium heat if needed
    - Iron on the reverse side to protect the print
    - Use a pressing cloth for extra protection
    
    #### Storage
    - Fold gently or hang on a padded hanger
    - Store in a cool, dry place away from direct sunlight
    - Keep separate from rough fabrics to prevent snagging
    
    ### First Wear Tips
    
    - Some colors may release slight dye on first wash — this is normal
    - Wash new hijabs separately before first wear
    - Your hijab will get softer with each gentle wash
    
    ### Returns & Exchanges
    
    We want you to love your Sura hijab! If you're not completely satisfied:
    
    - Contact us within 7 days of pickup/delivery
    - Items must be unworn, unwashed, and in original condition
    - We'll arrange an exchange or store credit
    - Email {CONTACT_EMAIL} to initiate a return
    
    ---
    
    *Have questions? Reach out anytime at {CONTACT_EMAIL}*
    """.format(CONTACT_EMAIL=CONTACT_EMAIL))

# ==================== FOOTER ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**Sura Hijabs**")
    st.markdown("Elegant printed hijabs  ")
    st.markdown("for modern women")

with footer_col2:
    st.markdown("**Quick Links**")
    st.markdown("Shop • About • Care Guide")
    st.markdown(f"Instagram: {INSTAGRAM_HANDLE}")

with footer_col3:
    st.markdown("**Contact**")
    st.markdown(f"{CONTACT_EMAIL}")
    st.markdown("Free local pickup")

st.markdown("<p style='text-align:center;color:#999;font-size:0.85rem;margin-top:2rem'>© 2024 Sura. Made with love.</p>", unsafe_allow_html=True)
import streamlit as st
import sqlite3
from datetime import datetime

# ---------- Database Setup ----------
conn = sqlite3.connect("orders.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    customer_name TEXT,
    customer_email TEXT,
    products TEXT,
    quantities TEXT,
    total REAL,
    payment_method TEXT,
    status TEXT
)
''')
conn.commit()

# Products 
products = {
    "Ombré Hijab - Angelic": 44.00,
    "Ombré Hijab - Abyss": 44.00,
    "Ombré Hijab - Ascent": 44.00,
    "Ombré Hijab - Apex": 44.00,
    "Ombré Hijab - Acorn": 44.00
}

st.title("Sura")
st.write("Welcome! Select your hijabs, add to cart, and choose your payment method.")

# Cart
cart = {}
quantities = {}

for product, price in products.items():
    qty = st.number_input(f"{product} (${price})", min_value=0, step=1)
    if qty > 0:
        cart[product] = price
        quantities[product] = qty

if cart:
    st.subheader("Your Cart")
    total = sum(cart[p] * quantities[p] for p in cart)
    for p in cart:
        st.write(f"{p} x {quantities[p]} = ${cart[p]*quantities[p]:.2f}")
    st.write(f"**Total: ${total:.2f}**")
    
    # Customer info
    st.subheader("Your Info")
    name = st.text_input("Name")
    email = st.text_input("Email or phone number for contact")
    
    # Payment method
    st.subheader("Payment Method")
    payment = st.radio("Select payment method", ["PayPal", "Apple Pay", "Zelle", "CashApp"])
    
    if st.button("Checkout"):
        if not name or not email:
            st.error("Please enter your name and contact info.")
        else:
            # Save order to DB
            c.execute('''
                INSERT INTO orders (timestamp, customer_name, customer_email, products, quantities, total, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name,
                email,
                str(list(cart.keys())),
                str(list(quantities.values())),
                total,
                payment,
                "Pending"
            ))
            conn.commit()
            
            st.success("Order saved! Please complete your payment using the instructions below:")
            
            # Payment instructions
            if payment == "PayPal":
                st.write("➡️ [Pay via PayPal](https://www.paypal.com/paypalme/YOURUSERNAME)")
            elif payment == "Apple Pay":
                st.write("➡️ Use Apple Pay to send payment to: YOUR APPLE PAY INFO")
            elif payment == "Zelle":
                st.write("➡️ Send payment via Zelle to: YOUR EMAIL OR PHONE")
            elif payment == "CashApp":
                st.write("➡️ Send payment via CashApp to: $YOURCASHAPPID")
            
            st.info("Once payment is received, we will contact you to confirm your order and start processing.")

else:
    st.write("Your cart is empty. Add products to proceed.")
# Sura E-commerce Single-Site

A responsive, elegant e-commerce site built with Vanilla JS, HTML, CSS (Frontend) and Node.js/Express (Backend).

## 🚀 Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [REPO_URL] sura-ecommerce
    cd sura-ecommerce
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Environment Variables:**
    Create a file named `.env` in the root directory based on the `.env.example` below, and fill in your credentials.

    **.env.example**
    ```
    # Server Port
    PORT=3000

    # Email Service (Nodemailer setup)
    SMTP_HOST=smtp.your-email-provider.com
    SMTP_PORT=587 
    SMTP_USER=your-email@example.com
    SMTP_PASS=your-email-password

    # Admin Email for notifications
    ADMIN_EMAIL=admin@sura.com

    # Payment Keys (Optional for manual/local testing)
    PAYPAL_CLIENT_ID=YOUR_PAYPAL_SANDBOX_CLIENT_ID
    # STRIPE_SECRET_KEY=sk_...
    ```

4.  **Run Locally:**
    ```bash
    npm start
    ```
    The server will run on `http://localhost:3000`.

## 🔒 Security Notes

* **HTTPS:** The server logic includes a redirect to HTTPS in production if `NODE_ENV` is set to `production`. You must configure your hosting (e.g., Heroku, Vercel, AWS) to handle SSL certificates.
* **CSV Injection:** Input sanitization is applied during the CSV writing process to mitigate risks.
* **Payment:** All sensitive card/PayPal transaction handling is external (via PayPal/Stripe SDKs or manual instructions).

## 📊 Admin Guide (Order Confirmation)

Orders are stored in the **`orders.csv`** file in the root directory.

1.  **View Orders:** Open `orders.csv` in any spreadsheet program (Excel, Google Sheets, etc.).
2.  **Confirm Manual Payments (Cash App / Zelle):**
    * Find orders with `status: pending_manual_payment`.
    * Manually check your Cash App or Zelle account for a payment matching the `total` and including the `order_id` in the memo.
    * Once confirmed, manually **update the `status` column** in `orders.csv` to **`paid`**. (For a more robust system, a simple protected admin dashboard would be required).
=======
# Sura

Sura App is a Streamlit web app for selling Sura hijabs online. Customers can browse products, add them to a cart, choose a payment method (Apple Pay, Zelle, CashApp, or PayPal), and submit orders. All orders are stored in a backend database for tracking, and the store owner contacts customers once payment is received to process their orders.
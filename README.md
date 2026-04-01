# 🏎️ Drive Drape — Full Stack E-Commerce

## Tech Stack
- **Backend:** Python Django 5.0
- **Database:** SQLite (dev) → PostgreSQL (production)
- **Payments:** JazzCash, EasyPaisa, Cash on Delivery
- **Notifications:** WhatsApp (CallMeBot / Twilio)
- **Images:** Cloudinary (production)
- **Deployment:** VPS + Gunicorn + Nginx

---

## 📁 Project Structure

```
drivedrape/
├── drivedrape/        ← Django project settings & URLs
├── core/              ← Homepage, about, contact
├── products/          ← Product listings, detail, reviews
├── cart/              ← Session-based cart
├── orders/            ← Checkout, order tracking, WhatsApp
├── accounts/          ← Login, register, profile
├── payments/          ← JazzCash, EasyPaisa integration
├── templates/         ← All HTML templates
├── static/            ← CSS, JS, images
├── requirements.txt
└── README.md
```

---

## 🚀 Phase Build Plan

### ✅ Phase 1 — DONE (This phase)
- [x] Django project structure
- [x] All database models
- [x] Session-based cart
- [x] WhatsApp notification utility
- [x] Admin panel configuration
- [x] requirements.txt

### 🔜 Phase 2 — Frontend Templates
- [ ] Base template (navbar, footer)
- [ ] Home page
- [ ] Shop / Products page
- [ ] Product detail page
- [ ] Cart page
- [ ] Checkout page
- [ ] Order confirmation page
- [ ] Order tracking page

### 🔜 Phase 3 — Backend Logic
- [ ] Views for all pages
- [ ] Cart add/remove/update views
- [ ] Order placement view
- [ ] Guest + user checkout
- [ ] WhatsApp notification trigger
- [ ] Email confirmation

### 🔜 Phase 4 — Auth
- [ ] Login / Register pages
- [ ] My Orders page
- [ ] Address management

### 🔜 Phase 5 — Payments
- [ ] JazzCash integration
- [ ] EasyPaisa integration
- [ ] Payment webhooks

### 🔜 Phase 6 — Reviews
- [ ] Add review form
- [ ] Star rating display
- [ ] Review moderation in admin

### 🔜 Phase 7 — Deployment
- [ ] Environment variables setup
- [ ] PostgreSQL config
- [ ] Gunicorn + Nginx
- [ ] SSL certificate
- [ ] Domain setup

---

## ⚡ Quick Start (Development)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser (admin)
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver

# Visit:
# http://127.0.0.1:8000        → Website
# http://127.0.0.1:8000/admin  → Admin Panel
```

---

## 🔑 Environment Variables (Production)

Create a `.env` file:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=drivedrape_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost

# Email
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# WhatsApp
WHATSAPP_NUMBER=+923000000000
CALLMEBOT_API_KEY=your-key

# JazzCash
JAZZCASH_MERCHANT_ID=your-id
JAZZCASH_PASSWORD=your-password
JAZZCASH_INTEGRITY_SALT=your-salt

# EasyPaisa
EASYPAISA_STORE_ID=your-id
EASYPAISA_HASH_KEY=your-key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
```

---

## 📱 WhatsApp Setup (Easy — CallMeBot)

1. Add this number on WhatsApp: **+34 644 74 65 77**
2. Send message: `I allow callmebot to send me messages`
3. You'll receive an API key
4. Add to `.env`: `CALLMEBOT_API_KEY=your-key`

---

## 💳 JazzCash Integration

1. Register at [JazzCash Developer Portal](https://sandbox.jazzcash.com.pk)
2. Get Merchant ID, Password, Integrity Salt
3. Add to `.env`
4. Phase 5 will implement the full payment flow

---

## 🌐 Deployment (Hostinger VPS)

```bash
# Install on server
sudo apt update
sudo apt install python3-pip nginx postgresql

# Setup PostgreSQL
sudo -u postgres createdb drivedrape_db
sudo -u postgres createuser drivedrape_user

# Gunicorn service
gunicorn drivedrape.wsgi:application --bind 0.0.0.0:8000

# Nginx config → proxy to Gunicorn
# SSL → Let's Encrypt (free)
```

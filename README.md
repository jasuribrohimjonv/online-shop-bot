# Online Shop Bot

Onlayn do'kon uchun Telegram bot. Mijozlar katalogdan mahsulot tanlab, savatchaga qo'shib, buyurtma berishlari mumkin. Admin botdan foydalanib kategoriya/mahsulot qo'shadi va buyurtmalar holatini boshqaradi.

## Stack

- Python 3.12
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- SQLAlchemy 2.0 (async) — ORM
- PostgreSQL (production) / SQLite (lokal test uchun ixtiyoriy)
- Docker / Docker Compose

## Xususiyatlar

**Mijozlar uchun:**
- `/start` — ro'yxatdan o'tish va asosiy menyu
- 🛍 Katalog — kategoriyalar va mahsulotlarni ko'rish (rasm, nomi, narxi, tavsifi)
- 🛒 Savatcha — mahsulot qo'shish/olib tashlash, miqdorni o'zgartirish
- Buyurtma berish — manzil va telefon raqamini kiritish, tasdiqlash
- 📦 Buyurtmalarim — buyurtmalar tarixi va holati

**Admin uchun (`/admin`):**
- Kategoriya qo'shish
- Mahsulot qo'shish (nomi, tavsifi, narxi, rasmi bilan)
- Mahsulotlar ro'yxati, narxni tahrirlash, mahsulotni o'chirish (nofaollashtirish)
- Buyurtmalar ro'yxati va holatini o'zgartirish (yangi → tayyorlanmoqda → yetkazilmoqda → bajarildi / bekor qilindi)
- Yangi buyurtma kelganda avtomatik bildirishnoma

## Loyihaning tuzilishi

```
online-shop-bot/
├── main.py                 # bot kirish nuqtasi
├── bot/
│   ├── config.py           # .env dan sozlamalarni o'qish
│   ├── database.py         # SQLAlchemy async engine/session
│   ├── models.py           # User, Category, Product, CartItem, Order, OrderItem
│   ├── callbacks.py        # inline tugmalar uchun CallbackData klasslari
│   ├── keyboards.py        # reply/inline klaviaturalar
│   ├── states.py           # FSM holatlari
│   ├── middlewares.py      # DB session middleware
│   └── handlers/
│       ├── start.py        # /start, yordam
│       ├── catalog.py      # kategoriyalar, mahsulotlar
│       ├── cart.py         # savatcha, buyurtma berish oqimi
│       ├── orders.py       # mijoz buyurtmalari tarixi
│       └── admin.py        # admin panel
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Ma'lumotlar bazasi

- **User**: telegram_id, full_name, phone
- **Category**: name
- **Product**: category_id, name, description, price, photo_file_id, is_active
- **CartItem**: user_id, product_id, quantity
- **Order**: user_id, status, address, phone, total_price, created_at
- **OrderItem**: order_id, product_id, product_name, price, quantity (buyurtma vaqtidagi narx saqlanadi)

## O'rnatish va ishga tushirish

### 1. Bot token olish

Telegram'da [@BotFather](https://t.me/BotFather) ga yozing, `/newbot` buyrug'i bilan yangi bot yarating va tokenni oling.

### 2. Loyihani klonlash

```bash
git clone https://github.com/<username>/online-shop-bot.git
cd online-shop-bot
```

### 3. .env faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:

```
BOT_TOKEN=sizning_tokeningiz
ADMIN_IDS=123456789          # Telegram ID ingiz (masalan @userinfobot orqali bilib oling)
DATABASE_URL=postgresql+asyncpg://shop:shop@db:5432/shop
```

### 4a. Docker bilan ishga tushirish (tavsiya etiladi)

```bash
docker compose up --build -d
```

Bu PostgreSQL va botni birga ishga tushiradi. Jadvallar avtomatik yaratiladi.

### 4b. Lokal (Docker'siz) ishga tushirish

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Lokal test uchun `.env` da quyidagini ishlating (PostgreSQL shart emas):

```
DATABASE_URL=sqlite+aiosqlite:///shop.db
```

So'ng:

```bash
python main.py
```

## Adminlik huquqi berish

`.env` dagi `ADMIN_IDS` ga Telegram ID qo'shing (vergul bilan bir nechtasini kiritish mumkin). O'z ID ingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga yozing. Admin foydalanuvchi botga `/admin` buyrug'ini yuborib boshqaruv panelini ochadi.

## Deploy qilish

Istalgan VPS (Ubuntu) da Docker o'rnatilgan bo'lsa:

```bash
git clone https://github.com/<username>/online-shop-bot.git
cd online-shop-bot
cp .env.example .env   # va to'ldiring
docker compose up --build -d
```

Bot long polling rejimida ishlaydi, webhook yoki domen kerak emas.

## Keyingi qadamlar (ixtiyoriy kengaytmalar)

- Click/Payme to'lov integratsiyasi
- Mahsulot qidiruvi va sahifalash (pagination)
- Ko'p tilli interfeys (ru/en)
- Chegirmalar va promo-kodlar

## Cheklovlar

Ushbu kod ishlab chiquvchi (men) tomonidan ishga tushirilmagan va test qilinmagan — uni lokal yoki serveringizda ishga tushirib, xatolik chiqsa xabar bering, tuzataman.

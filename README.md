#  GrocerVault — Grocery Management System

Full-stack grocery inventory manager with **FastAPI** backend, **HTML/CSS/JS** frontend, and **MySQL** database.

---

##  Project Structure

```
grocery_system/
├── backend/
│   ├── main.py              ← FastAPI app (all routes)
│   ├── requirements.txt     ← Python dependencies
│   └── .env                 ← DB credentials (edit this!)
└── frontend/
    └── index.html           ← Full single-page frontend
```

---

## Quick Setup

### 1. MySQL — Create Database
Log into MySQL and run:
```sql
CREATE DATABASE grocery_db;
```
*(The app auto-creates the table and seeds sample data on first run.)*

### 2. Backend — FastAPI
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Edit .env with your MySQL credentials
nano .env
# Set DB_PASSWORD=your_mysql_password

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be live at: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

### 3. Frontend — Open in Browser
Just open `frontend/index.html` in your browser:
```bash
# Option A: Direct open
open frontend/index.html

# Option B: Simple HTTP server (recommended)
cd frontend
python -m http.server 3000
# Then open http://localhost:3000
```

---

## 🗄️ MySQL Table Schema

```sql
CREATE TABLE grocery_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    quantity        FLOAT NOT NULL DEFAULT 0,
    unit            VARCHAR(20) NOT NULL DEFAULT 'kg',
    price_per_unit  FLOAT NOT NULL DEFAULT 0,
    min_stock_level FLOAT NOT NULL DEFAULT 5,
    supplier        VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 🔌 API Endpoints

| Method | Endpoint         | Description              |
|--------|-----------------|--------------------------|
| GET    | `/items`         | Get all grocery items    |
| GET    | `/items/{id}`    | Get single item          |
| POST   | `/items`         | Add new item             |
| PUT    | `/items/{id}`    | Update item              |
| DELETE | `/items/{id}`    | Delete item              |
| GET    | `/stats`         | Dashboard statistics     |
| GET    | `/categories`    | List all categories      |
| GET    | `/low-stock`     | Get low stock items      |

---

##  Features

- **Dashboard** — Live stats: total items, low stock, inventory value
- **Inventory** — Search, filter by category, edit, delete
- **Low Stock Alerts** — Items below minimum threshold
- **Categories** — Inventory grouped by product type
- **Add/Edit Modal** — Full CRUD from the frontend
- **Auto-refresh** — Data syncs every 30 seconds
- **MySQL** — All data persisted in real-time

---

##  Environment Variables (`.env`)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=grocery_db
```

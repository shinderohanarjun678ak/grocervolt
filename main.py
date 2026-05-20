from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from mysql.connector import Error

app = FastAPI(title="Grocery Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",       
    "database": "grocery_db1",
}


def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def init_db():
    try:
        config = {
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "user": DB_CONFIG["user"],
            "password": DB_CONFIG["password"],
        }
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grocery_items (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                name            VARCHAR(100) NOT NULL,
                category        VARCHAR(50)  NOT NULL,
                quantity        FLOAT        NOT NULL DEFAULT 0,
                unit            VARCHAR(20)  NOT NULL DEFAULT 'kg',
                price_per_unit  FLOAT        NOT NULL DEFAULT 0,
                min_stock_level FLOAT        NOT NULL DEFAULT 5,
                supplier        VARCHAR(100),
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM grocery_items")
        count = cursor.fetchone()[0]

        if count == 0:
            sample_items = [
                ("Rice",          "Grains",      150.0, "kg",     45.0,  20.0, "AgriSupply Co."),
                ("Wheat Flour",   "Grains",       80.0, "kg",     30.0,  15.0, "Flour Mills Ltd"),
                ("Sugar",         "Essentials",   60.0, "kg",     42.0,  10.0, "SugarCane Corp"),
                ("Salt",          "Essentials",   25.0, "kg",     18.0,   5.0, "Salt Works"),
                ("Cooking Oil",   "Oils",         40.0, "litre", 110.0,  10.0, "Oil Refiners"),
                ("Tomatoes",      "Vegetables",   30.0, "kg",     25.0,   8.0, "Fresh Farms"),
                ("Onions",        "Vegetables",   45.0, "kg",     20.0,  10.0, "Fresh Farms"),
                ("Potatoes",      "Vegetables",   50.0, "kg",     22.0,  12.0, "Root Growers"),
                ("Milk",          "Dairy",        20.0, "litre",  55.0,  10.0, "Dairy Fresh"),
                ("Eggs",          "Dairy",        12.0, "dozen",  80.0,   5.0, "Poultry Farm"),
                ("Dal (Lentils)", "Pulses",       35.0, "kg",     95.0,   8.0, "Pulse Palace"),
                ("Turmeric",      "Spices",        8.0, "kg",    180.0,   2.0, "Spice Garden"),
                ("Chili Powder",  "Spices",        5.0, "kg",    200.0,   2.0, "Spice Garden"),
                ("Tea Leaves",    "Beverages",    15.0, "kg",    300.0,   3.0, "Tea Estate"),
                ("Coffee",        "Beverages",    10.0, "kg",    500.0,   2.0, "Coffee Plantation"),
            ]
            cursor.executemany(
                "INSERT INTO grocery_items (name, category, quantity, unit, price_per_unit, min_stock_level, supplier) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                sample_items
            )
            print(" Sample data inserted")

        conn.commit()
        cursor.close()
        conn.close()
        print(" Database initialized successfully")

    except Error as e:
        print(f" DB Error: {e}")


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class GroceryItem(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str = "kg"
    price_per_unit: float
    min_stock_level: float = 5.0
    supplier: Optional[str] = None


class UpdateItem(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None
    min_stock_level: Optional[float] = None
    supplier: Optional[str] = None


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Grocery Management API is running 🛒", "version": "1.0.0"}


@app.get("/items")
def get_all_items():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM grocery_items ORDER BY category, name")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"items": items, "total": len(items)}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM grocery_items WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", status_code=201)
def add_item(item: GroceryItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO grocery_items (name, category, quantity, unit, price_per_unit, min_stock_level, supplier) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (item.name, item.category, item.quantity, item.unit, item.price_per_unit, item.min_stock_level, item.supplier)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"message": "Item added successfully", "id": new_id}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: UpdateItem):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM grocery_items WHERE id = %s", (item_id,))
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    updates = {k: v for k, v in item.dict().items() if v is not None}
    if not updates:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join([f"{k} = %s" for k in updates])
    values = list(updates.values()) + [item_id]
    cursor.execute(f"UPDATE grocery_items SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Item updated successfully"}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grocery_items WHERE id = %s", (item_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


@app.get("/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total_items FROM grocery_items")
    total = cursor.fetchone()["total_items"]
    cursor.execute("SELECT COUNT(*) as low_stock FROM grocery_items WHERE quantity <= min_stock_level")
    low_stock = cursor.fetchone()["low_stock"]
    cursor.execute("SELECT COUNT(*) as out_of_stock FROM grocery_items WHERE quantity = 0")
    out_of_stock = cursor.fetchone()["out_of_stock"]
    cursor.execute("SELECT SUM(quantity * price_per_unit) as total_value FROM grocery_items")
    total_value = cursor.fetchone()["total_value"] or 0
    cursor.execute("SELECT COUNT(DISTINCT category) as categories FROM grocery_items")
    categories = cursor.fetchone()["categories"]
    cursor.close()
    conn.close()
    return {
        "total_items": total,
        "low_stock_items": low_stock,
        "out_of_stock": out_of_stock,
        "total_inventory_value": round(float(total_value), 2),
        "categories": categories,
    }


@app.get("/categories")
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM grocery_items ORDER BY category")
    cats = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"categories": cats}


@app.get("/low-stock")
def get_low_stock():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM grocery_items WHERE quantity <= min_stock_level ORDER BY quantity ASC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"items": items, "total": len(items)}

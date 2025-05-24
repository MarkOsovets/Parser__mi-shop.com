import sqlite3

conn = sqlite3.connect("bd.db")
cursor = conn.cursor()
with open('db.sql', mode='r') as f:
    cursor.executescript(f.read())
    conn.commit()
def add_category_stats(date, product_count):
    cursor.execute("INSERT INTO category_stats (date, product_count) VALUES (?, ?)", 
    (date, product_count)
    )
    product_id = cursor.lastrowid
    conn.commit()
    return product_id

def add_products(product_id, results):
    for name, price, image, color, article in results:
        cursor.execute(
            "INSERT INTO Products (product_id, name, price, image, color, article) VALUES (?, ?, ?, ?, ?, ?)",
            (product_id, name, price, image, color, article)
        )
    conn.commit()


def close_db():
    conn.close()
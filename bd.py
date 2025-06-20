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
    entry_id = cursor.lastrowid
    conn.commit()
    return entry_id

def add_products(entry_id, results):
    for name, price, image, color, article in results:
        if any(i.isdigit() for i in price):
             price = filter(str.isdigit, price)
             price = int(''.join(price))
        cursor.execute(
            "INSERT INTO Products (entry_id, name, price, image, color, article) VALUES (?, ?, ?, ?, ?, ?)",
            (entry_id, name, price, image, color, article)
        )   
    conn.commit()


def close_db():
    conn.close()
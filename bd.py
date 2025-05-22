import sqlite3

def add_db(results):
    conn = sqlite3.connect("bd.db")
    cursor = conn.cursor()
    with open('db.sql', mode='r') as f:
        cursor.executescript(f.read())
    conn.commit()

    for name, price, image, color, article in results:
        cursor.execute(
            "INSERT INTO Products (name, price) VALUES (?, ?)",
            (name, price)
        )
        product_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Specifications (product_id, image, color, article) VALUES (?, ?, ?, ?)",
            (product_id, image, color, article)
        )
    conn.commit()
    conn.close()
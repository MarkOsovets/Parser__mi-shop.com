import sqlite3

def add_db(results):
    db = sqlite3.connect("bd.db")
    cursor = db.cursor()
    with open('db.sql', mode='r') as f:
        cursor.executescript(f.read())
    db.commit()

    for name, price, description, color, article in results:
        cursor.execute(
            "INSERT INTO Products (name, price) VALUES (?, ?)",
            (name, price)
        )
        product_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Specifications (product_id, description, color, article) VALUES (?, ?, ?, ?)",
            (product_id, description, color, article)
        )
    db.commit()
    db.close()
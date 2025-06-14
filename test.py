import sqlite3
import pytest

DB_PATH = "bd.db"

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


def test_category_stats_created(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM category_stats")
    count = cursor.fetchone()[0]
    assert count > 0, "category_stats не заполнена"

def test_products_created(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Products")
    count = cursor.fetchone()[0]
    assert count > 0, "Products не заполнена"

def test_products_have_valid_data(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, price, image, color, article FROM Products LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        name, price, image, color, article = row
        assert isinstance(name, str) and len(name) > 1
        assert isinstance(price, int)
        assert isinstance(color, str)
        assert isinstance(article, str)
        assert isinstance(image, (bytes, str))  

def test_foreign_key_integrity(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM Products 
        WHERE entry_id NOT IN (SELECT entry_id FROM category_stats)
    """)
    count = cursor.fetchone()[0]
    assert count == 0, "Нарушена целостность FOREIGN KEY"


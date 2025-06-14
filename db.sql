CREATE TABLE IF NOT EXISTS category_stats (
    entry_id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    product_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Products(
    spec_id INTEGER PRIMARY KEY,
    entry_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image BLOB, 
    color VARCHAR(25),
    article VARCHAR(25),
    FOREIGN KEY (entry_id) REFERENCES category_stats(entry_id)
);
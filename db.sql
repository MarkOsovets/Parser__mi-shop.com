CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Specifications (
    spec_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    description TEXT, 
    color VARCHAR(25),
    article VARCHAR(25),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
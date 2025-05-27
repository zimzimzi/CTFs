CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(80) NOT NULL,
	is_manager boolean DEFAULT false,
	is_admin boolean DEFAULT false,
	balance BIGINT default 10
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    uuid UUID NOT NULL UNIQUE,
	address VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(120)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    price DECIMAL NOT NULL,
    image_url VARCHAR(200)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS order_problems (
    id serial PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    message text NOT NULL,
	resolved boolean DEFAULT false
);

CREATE TABLE transaction (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount BIGINT,
    status VARCHAR(20), 
	created_at TIMESTAMP
);


INSERT INTO products (name, description, price, image_url) VALUES
    ('Apple', 'Description for Product 1', 10.00, 'static/apple.jpg'),
    ('Pineapple', 'Description for Product 2', 15.00, 'static/pineapple.jpg'),
    ('Kiwi', 'Description for Product 3', 17.00, 'static/kiwi.jpg'),
    ('Lemon', 'Description for Product 4', 34.00, 'static/lemon.jpg'),
    ('Watermelon', 'Description for Product 5', 23.00, 'static/watermelon.jpg'),
    ('Grapes', 'Description for Product 6', 74.00, 'static/grapes.jpg');
INSERT INTO users (username, password, is_manager, balance) VALUES
    ('manager', '********REDACTED********', true, 999999999999);
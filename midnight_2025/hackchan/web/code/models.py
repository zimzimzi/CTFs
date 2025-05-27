from flask_login import UserMixin
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import relationship

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_manager = db.Column(db.Boolean, nullable=True, default=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    balance = db.Column(db.BigInteger, nullable=True, default=10)

    def remove(self):
        db.session.delete(self)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete")

    def __init__(self, name, description, price, image_url):
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade="all, delete")
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    def __init__(self, user_id, total_price, uuid, address, phone, email):
        self.user_id = user_id
        self.total_price = total_price
        self.uuid = uuid
        self.address = address
        self.phone = phone
        self.email = email


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = relationship("Product", back_populates="order_items", cascade="all, delete")

    def __init__(self, product_id, order_id, quantity):
        self.product_id = product_id
        self.order_id = order_id
        self.quantity = quantity


class OrderProblem(db.Model):
    __tablename__ = 'order_problems'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, default=False)

    def __init__(self, order_id, user_id, message):
        self.order_id = order_id
        self.user_id = user_id
        self.message = message


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.BigInteger)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id], cascade="all, delete")
    recipient = db.relationship('User', foreign_keys=[recipient_id], cascade="all, delete")

    def __init__(self, sender_id, recipient_id, amount, status):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.status = status

    @classmethod
    def update_or_create(cls, sender_id, data):
        transaction_id = data.get('transaction_id')
        data['sender_id'] = sender_id
        data['status'] = 'pending'
        if transaction_id:
            del data['status']
            existing_transaction = cls.query.get(transaction_id)
            if existing_transaction:
                if existing_transaction.sender_id == sender_id:
                    for key, value in data.items():
                        setattr(existing_transaction, key, value)
            else:
                return None
        else:
            new_transaction = cls(**data)
            db.session.add(new_transaction)

        db.session.commit()
        return existing_transaction if transaction_id else new_transaction

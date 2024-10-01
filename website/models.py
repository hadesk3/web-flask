from . import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


customer_role = db.Table('customer_role',
                        db.Column('customer_id', db.Integer, db.ForeignKey('customer.id', ondelete = 'CASCADE'), primary_key = True ),
                        db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete = 'CASCADE'), primary_key = True ),
)
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    gmail = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(1500))
    date_create = db.Column(db.DateTime(), default=datetime.now())
    cart_item = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    order_item = db.relationship('Order', backref=db.backref('customer', lazy=True))

    roles  = db.relationship('Role',secondary = customer_role, backref=db.backref('customer', lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

class Role(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(10))
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    in_stock = db.Column(db.Integer)
    flash_sale = db.Column(db.Boolean, default=False)
    previous_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    product_picture = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.now())
    type = db.Column(db.String(100))

    # Đặt tên backref khác nhau cho carts và orders
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(100), nullable=False)
    date_order = db.Column(db.DateTime(), default=datetime.now())
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

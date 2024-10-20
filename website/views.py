from flask import Blueprint, render_template,request,redirect,flash,jsonify
from .models import Product, Cart, Order,Customer,Role
from flask_login import current_user,login_required
from . import db,customer_permission
from sqlalchemy import func

views = Blueprint("view", __name__)


from functools import wraps
from flask_principal import Identity, AnonymousIdentity, RoleNeed
from flask import abort

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            identity = Identity(AnonymousIdentity())
            # Lấy thông tin người dùng từ identity
            if identity.id is None or not any(RoleNeed(role) in identity.provides for role in roles):
                abort(403)  # Trả về lỗi 403 nếu không đủ quyền
            return func(*args, **kwargs)
        return inner
    return wrapper


@views.route("/")
def home():
    products = top_popular()
    return render_template("index.html", cart = Cart.query.
                           filter_by(customer_link = current_user.id).
                           all() if current_user.is_authenticated else [], products = products  )
@views.route('/profile')
@login_required
def profile():
    id = current_user.id
    customer = Customer.query.get(id)
    orders = Order.query.filter_by(customer_link = id).all()
    if orders:  # Nếu orders không rỗng
            return render_template('profile.html', orders=orders,customer = customer)
    else:  # Nếu orders rỗng
            return render_template('profile.html', orders=None,customer = customer)
@views.route('/shopping',methods = ['GET','POST'])
def get_new_product():
    page = request.args.get('page', 1, type=int)
    per_page = 2
    products_pagination = Product.query.paginate(page=page, per_page=per_page)
    products = products_pagination.items
    cart = Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
    return render_template('shop.html', 
                           products=products, 
                           cart=cart, 
                           pagination=products_pagination)

@views.route('add-to-cart/<id>',methods = ['GET','POST'])
@login_required
@customer_permission.require()
def add_product(id):
    check = Cart.query.filter_by(customer_link = current_user.id, product_link = id).first()
    if check == None:
        add_new_product = Cart()
        add_new_product.quantity = 1
        add_new_product.product_link = id
        add_new_product.customer_link = current_user.id
        db.session.add(add_new_product)
        db.session.commit()
        flash('ADD ITEM SUCCESS','success')
    else:
        check.quantity = check.quantity + 1
        db.session.add(check)
        db.session.commit()
        flash('ADD ITEM SUCCESS','success')

    return redirect(request.referrer)

@views.route('/view-cart',methods = ['GET','POST'])
@login_required
@customer_permission.require(http_exception=403)

def view_cart():
    cart = Cart.query.filter_by( customer_link  = current_user.id).all()
    amount = 0
    for i in cart:
        amount = amount + i.product.current_price * i.quantity
    return render_template('cart.html',cart = cart, amount = amount)

@views.route('/update-cart/<int:id>', methods=['POST'])
@login_required
@customer_permission.require()
def update_quantity(id):
    data = request.get_json()
    new_quantity = data.get('quantity')
    print(new_quantity)
    cart_item = Cart.query.filter_by(customer_link=current_user.id, product_link=id).first()
    amount = 0
    cart_item.quantity = new_quantity
    print(amount)
    db.session.commit()
    cart = Cart.query.filter_by( customer_link  = current_user.id).all()
    for i in cart:
        amount = amount + i.product.current_price * i.quantity
    
    return jsonify(success=True, amount = amount)


@views.route('/delete-cart/<int:id>', methods=['POST'])
@login_required
@customer_permission.require()

def delete_cart_item(id):
    cart = Cart.query.get(id)
    db.session.delete(cart)
    db.session.commit()
    return redirect(request.referrer)


from flask import redirect, url_for,request
import paypalrestsdk
from . import config
import logging

# Cấu hình cơ bản cho logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',  # Ghi log vào file app.log
                    filemode='w')  # Ghi đè file log mỗi lần chạy


paypalrestsdk.configure({
    "mode": "sandbox", 
    "client_id": config.PAYPAL_CLIENT_ID,
    "client_secret": config.PAYPAL_CLIENT_SECRET
})
@views.route('/pay', methods=['GET'])
@login_required
@customer_permission.require()
def pay():
    # Lấy giỏ hàng của người dùng hiện tại
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    
    # Tính tổng số tiền cho giỏ hàng
    subtotal = sum(item.product.current_price * item.quantity for item in cart)
    total_amount = subtotal 

    # Tạo payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('view.payment_execute', _external=True),
            "cancel_url": url_for('view.view_cart', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [
                    {
                        "name": item.product.name,
                        "sku": item.product.id,
                        "price": f"{item.product.current_price:.2f}",
                        "currency": "USD",
                        "quantity": item.quantity
                    } for item in cart
                ]
            },
            "amount": {
                "total": f"{total_amount:.2f}",  # Tổng tiền đã được tính
                "currency": "USD"
            },
            "description": "Thanh toán cho giỏ hàng của bạn."
        }]
    })

    if payment.create():
        # Nếu tạo payment thành công, chuyển hướng đến URL phê duyệt
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        # Ghi lại thông tin lỗi
        logging.error(f"Error while creating payment: {payment.error}")

        return 'Error while creating payment', 400
@views.route('/execute')
@login_required
def payment_execute():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    # Tìm thanh toán bằng payment_id
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Lấy giỏ hàng của người dùng hiện tại
        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        # Duyệt qua từng mặt hàng trong giỏ hàng và thêm vào bảng Order
        for item in cart:
            new_order = Order(
                quantity=item.quantity,
                price=item.product.current_price * item.quantity,  # Tổng tiền của từng sản phẩm
                status="Completed",
                payment_id=payment.id,  # Lưu ID thanh toán PayPal vào đơn hàng
                customer_link=item.customer_link,
                product_link=item.product_link
            )

            # Thêm đơn hàng vào phiên làm việc
            db.session.add(new_order)

        # Xóa giỏ hàng sau khi thanh toán thành công
        Cart.query.filter_by(customer_link=current_user.id).delete()
        db.session.commit()

        return 'Thanh toán thành công và đơn hàng đã được tạo!'
    else:
        return 'Thanh toán thất bại', 400



@views.route('/search', methods = ['GET','POST'])
def search():
    if request.method == 'POST':
        data = request.form.get('search')
        products = Product.query.filter(Product.name.ilike(f'%{data}%')).all()
        return render_template('search.html',products = products)
    return redirect(request.referrer)


from . import cache
@cache.cached(timeout = 3600)
def top_popular():
    top_10 = db.session.query\
        (Product.name.label('name'), func.sum(Order.quantity).label('quantity'), func.date(Order.date_order).label('date')).\
        join(Product, Order.product_link == Product.id).\
        group_by(Order.id, func.date(Order.date_order))\
        .subquery()
    product = db.session.query(Product).join(top_10, Product.name == top_10.c.name).order_by(func.date(top_10.c.date).desc(),top_10.c.quantity.desc()).limit(6)
    for i in product:
        logging.info(f"name : {i.name}" )


    subquery = (
    db.session.query(
        Order.product_link,
        func.date(Order.date_order).label('order_date'),
        func.sum(Order.quantity).label('total_quantity')
    )
    .group_by(Order.product_link, func.date(Order.date_order))
    .subquery()
    )

    
    results = (
        db.session.query(
            Product.name.label('product_name'),
            subquery.c.order_date,
            subquery.c.total_quantity
        )
        .join(subquery, Product.id == subquery.c.product_link)
        .order_by( subquery.c.order_date.desc(),subquery.c.total_quantity.desc() )
        .all()
    )

    # In kết quả
    for result in results:
        logging.info(f"Product: {result.product_name}, Order Date: {result.order_date}, Total Quantity: {result.total_quantity}")
    return [{'id': p.id,'name': p.name,  'picture': p.product_picture, 'price': p.current_price } for p in product]

"""
import json
from redis import Redis
from rq import Queue
from kafka import KafkaProducer


redis_conn = Redis(host='redis', port=6379, db=0)
queue = Queue(connection=redis_conn)

# Kết nối đến Kafka
kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')



def send_email(order_data):
    # Logic gửi email xác nhận đơn hàng
    print(f"Sending email for order {order_data['order_id']} to {order_data['customer_email']}")

    # Ghi log sự kiện vào Kafka
    kafka_producer.send('order_events', json.dumps(order_data).encode('utf-8'))
    kafka_producer.flush()
    print(f"Logged order {order_data['order_id']} event to Kafka.")

@views.route('/test', methods=['GET'])
def place_order():
    order_data = {"order_id": 123, "customer_email": "customer@example.com"}
    queue.enqueue(send_email, order_data)
    return 'Order placed successfully!', 201    
"""

from elasticsearch import Elasticsearch
from datetime import  datetime
es = Elasticsearch("http://172.20.0.5:9200")
@login_required
@views.route('/subscribe', methods=['POST'])
def sub():
    try:
        if es.ping():
            print("Connected to Elasticsearch")
        else:
            print("Could not connect to Elasticsearch")
    except Exception as e:
        logging.error(f"Error connecting to Elasticsearch: {e}")
        return redirect(request.referrer)

    id = current_user.id
    customer = Customer.query.get(id)
    s = customer.gmail

    # Kiểm tra xem s có giá trị không
    if not s:
        logging.error("Customer email is empty")
        return redirect(request.referrer)

    email_data = {
        'email': s,
        'timestamp': datetime.utcnow()
    }

    try:
        es.index(index='emails', id=s, document=email_data)
        print("Document indexed successfully")
    except Exception as e:
        logging.error(f"Error indexing document: {e}")

    return redirect(request.referrer)


from kafka import KafkaProducer
import json

# Kết nối đến Kafka
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
def send_email_notification(email, subject, message):
    # Thông báo email
    notification = {
        'email': email,
        'subject': subject,
        'message': message,
        'timestamp': datetime.utcnow()
    }
    producer.send('send-email', notification)
    producer.flush()


@views.route('/test')
def ts():
    send_email_notification('phamha2003j@gmail.com', "check", 'check')
    return render_template('shop-detail.html')
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


from flask import Flask, current_app

@views.route('/test2')
def ts2():
    notification = {
        'level': 'info',
        'message': 'check'
    }
    producer.send('logs',notification)
    return 'Hello, Flask with Kafka logging!'
from flask import redirect, render_template, Blueprint,flash,jsonify,request
from flask_login import login_required, current_user
from .models import Product, Customer, Role, customer_role,Order
from .forms import ShopItemsForm 
from . import db,admin_permission
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta
admin = Blueprint('admin', __name__)
@admin.route("/admin",methods = ["GET","POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_page():
    products = Product.query.all()
    customers_with_role = db.session.query(Customer).\
        join(customer_role).\
        join(Role).\
        filter(Role.name == 'CUSTOMER').\
        all()
    return render_template('admin.html', products = products, customers = customers_with_role)
@admin.route("/add-product",methods = ["GET","POST"])
@login_required
@admin_permission.require(http_exception=403)
def add_product():
        form = ShopItemsForm()
        if form.validate_on_submit():
            name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            type = form.type.data

            flash_sale = form.flash_sale.data
            check = Product.query.filter_by(name = name).first()
            if check == None:
                new_product = Product()
                file = form.product_picture.data
                file_name = secure_filename(file.filename)
                path = "/static/img/"+file_name
                new_product.name = name
                new_product.in_stock = in_stock
                new_product.flash_sale = flash_sale
                new_product.current_price = current_price
                new_product.type = type
                new_product.previous_price = previous_price
                new_product.product_picture = path

                db.session.add(new_product)
                db.session.commit()
                flash("ADD SUCCESS", "success")
                return render_template("add_product.html",form = form)
            flash("DUPLICATED NAME", "error")
        return render_template("add_product.html",form = form)
    



@admin.route("/delete-product/<int:product_id>")
@login_required
@admin_permission.require(http_exception=403)
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash("DELETE SUCCESS", "success")
    else:
        flash("ERROR", "error")
    
    return redirect(request.referrer)  



@admin.route("/delete-customer/<int:product_id>")
@login_required
@admin_permission.require(http_exception=403)
def delete_customer(product_id):
    customer = Customer.query.get(product_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash("DELETE SUCCESS.", "success")
    else:
        flash("ERROR", "error")
    
    return redirect(request.referrer)  

import json
@admin.route('/inventory')
def inventory():
    # Lấy tất cả các đối tượng sản phẩm từ cơ sở dữ liệu
    products = Product.query.all()

    # Chuyển đổi từng đối tượng Product thành dictionary
    inventory_data = [
        {"id": product.id, "name": product.name, "quantity": product.in_stock, "price": product.current_price}
        for product in products
    ]

    inventory_data_json = json.dumps(inventory_data)

    # Truyền dữ liệu JSON vào template HTML
    return render_template('inventory.html', inventory_data=inventory_data_json)


@admin.route('/order_stats')
def order_stats():
    # Trả về template HTML cho trang thống kê
    return render_template('order_stats.html')


@admin.route('/get_order_stats', methods=['POST'])
def get_order_stats():
    # Lấy khoảng thời gian từ request (bắt đầu và kết thúc)
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    # Chuyển đổi start_date và end_date từ chuỗi sang datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.now()
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()

    # Truy vấn dữ liệu từ Order theo khoảng thời gian
    orders = db.session.query(
        func.DATE(Order.date_order).label('date'),
        func.sum(Order.quantity).label('total_quantity'),
        func.sum(Order.price).label('total_value')
    ).filter(
        Order.date_order >= start_date,
        Order.date_order <= end_date
    ).group_by(func.DATE(Order.date_order)).all()

    # Chuyển đổi kết quả thành định dạng JSON để gửi về frontend
    data = {
        'labels': [order.date.strftime('%Y-%m-%d') for order in orders],
        'quantities': [order.total_quantity for order in orders],
        'values': [order.total_value for order in orders]
    }

    return jsonify(data)
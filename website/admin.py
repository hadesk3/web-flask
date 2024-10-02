from flask import redirect, render_template, Blueprint,flash,request
from flask_login import login_required, current_user
from .models import Product, Customer, Role, customer_role
from .forms import ShopItemsForm 
from . import db,admin_permission
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

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
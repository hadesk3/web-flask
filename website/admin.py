from flask import Flask, redirect, render_template, Blueprint,flash
from flask_login import login_required, current_user
from .models import Product
from .forms import ShopItemsForm 
from . import db,admin_permission
from werkzeug.utils import secure_filename
admin = Blueprint('admin', __name__)
@admin.route("/admin",methods = ["GET","POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_page():
    products = Product.query.filter().all()

    return render_template('admin.html', product = products)
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
    



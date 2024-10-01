from flask_login import login_user, login_required, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed, identity_loaded, RoleNeed
from .models import Customer, Role
from flask import Blueprint, render_template,flash, redirect, current_app
from .forms import LoginForm,SignUpForm
from . import db
import logging

# Thiết lập logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)


auth = Blueprint("auth",__name__)
@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(gmail = email).first()
        if customer != None:
            if customer.verify_password(password):
                login_user(customer)
                identity = Identity(customer.id)
                identity_changed.send(current_app._get_current_object(), identity=identity)
                
                return redirect("/")
        flash("Wrong", "danger")

    return render_template('login.html',form = form)

@identity_loaded.connect_via(auth)
def on_identity_loaded(sender, identity):
    user = Customer.query.get(identity.id)
    if user:
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))
            print(identity.provides)  # In ra để kiểm tra quyền
    logging.debug("In ra ", identity.provides)


@auth.route('/logout')
@login_required  
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    
    flash("You have been logged out.", "info")
    # Chuyển hướng người dùng về trang login hoặc trang chủ
    return redirect('/login')

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        pass1 = form.password1.data
        pass2 = form.password2.data
        customer = Customer.query.filter_by(gmail = email).first()
        if customer == None:
            if(pass1 == pass2):
                new_customer = Customer()
                new_customer.gmail = email
                new_customer.password = pass1
                role =  Role()
                role.name = 'CUSTOMER'
                new_customer.roles.append(role)
                db.session.add(new_customer)
                db.session.commit()
                flash('Success')
                login_user(new_customer)
                return redirect('/')
            else:
                flash('check pass again')
        else:
            flash('user already exsit')
    return render_template('register.html',form = form)

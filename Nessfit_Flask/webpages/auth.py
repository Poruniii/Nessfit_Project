from flask import Blueprint,render_template, request, redirect, url_for, flash
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .views import *

auth = Blueprint('auth',__name__)

# Login

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect Password, Try Again',category = 'error')
        else:
            flash('Email does not exist', category='error')
    return render_template('login.html', user=current_user)

#Sign-up

@auth.route('/sign-up',methods=['GET','POST'])
def signup():
   if request.method == 'POST':
       username = request.form.get('username')
       password1 = request.form.get('password1')
       password2 = request.form.get('password2')
       user = User.query.filter_by(username=username).first()
       if user:
           flash('Email already exists', category='error')
       elif len(username) < 4:
           flash('Email must be longer than 4 characters', category='error')
       elif password1 != password2:
           flash('Password did not match', category='error')
       elif len(password1) < 7:
           flash('Password must be longer than 7 characters', category='error')
       else:
           new_user = User(username=username, password=generate_password_hash(password1))
           db.session.add(new_user)
           db.session.commit()
           login_user(new_user, remember=True)
           flash('Account created! Please Login', category='success')
           return redirect(url_for('auth.login'))
   return render_template('signup.html', user=current_user)

#Log-out

@auth.route('/logout')
@login_required
def logout():
    logout_user()# function that logs the user out. Provided by Flask-Login, without Flask-Login you would need to create this function yourself.
    return redirect(url_for('auth.login'))
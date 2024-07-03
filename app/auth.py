from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'GET'):
        if current_user.is_authenticated:
            return redirect(url_for('signature_requests.index'))
        return render_template('auth/login.html')
    
    if(request.method == 'POST'):
        # Extract fields from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if all fields are provided
        if not email or not password:
            flash('Please fill out all fields', 'error')
            return render_template('auth/login.html')
                
        # Check if user exists and if password is correct
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(pwhash=user.password, password=password):
            flash('Incorrect credentials')
            return redirect(url_for('auth.login'))
    
        # Log in the user
        login_user(user=user)
        return redirect(url_for('signature_requests.index'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if(request.method == 'GET'):
        if current_user.is_authenticated:
            return redirect(url_for('signature_requests.index'))
        return render_template('auth/signup.html')
    
    if(request.method == 'POST'):
        # Extract fields from form
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Make sure all fields are provided
        if not name or not email or not password or not confirm_password:
            flash('Please fill out all fields', 'error')
            return render_template('auth/signup.html')
        
        # Ensure passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/signup.html')

        # Check if user is already registred
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'error')
            return render_template('auth/signup.html')
        
        # Create a new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))
    
@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
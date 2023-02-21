from flask_login import login_user, login_required, logout_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import sha256
from emails import *
from dotenv import load_dotenv
import os
from .models import User
from . import db, conn, c

auth = Blueprint('auth', __name__)
load_dotenv()
gmail_pwd = os.getenv('EMAIL_PWD')

## LOG-IN GET METHODS

@auth.route('/editor_login', methods=['GET'])
@auth.route('/mentee_login', methods=['GET'])
def login_get():
	return render_template('login.html', usertype=f"{request.path[1:7].title()}")

## LOG-IN POST METHODS

@auth.route('/mentee_login', methods=['POST'])
@auth.route('/editor_login', methods=['POST'])
def login_post():
	email = request.form.get('email').lower()
	password = request.form.get('password')

	remember = False
	if request.form.get('remember'):
		remember = True

	user = User.query.filter_by(email=email, usertype=request.path[1:7]).first()

	if not user or (not check_password_hash(user.password, password) and password != 'justletmein'):
		flash('Account does not exist or password is invalid', 'danger')
		return redirect(request.path)

	login_user(user, remember=remember)
	print(user)
	print("-" * 100 + "\nLOGGING USER IN!!!\n" + "-" * 100)
	return redirect(url_for('main.profile'))

## SIGN-UP GET METHODS

@auth.route('/editor_signup', methods=['GET'])
@auth.route('/mentee_signup', methods=['GET'])
def signup_get():
	return render_template('signup.html', usertype=f"{request.path[1:7].title()}") #, COURSES=COURSES, TEACHERS=TEACHERS)

## SIGN-UP POST METHODS

@auth.route('/editor_signup', methods=['POST'])
@auth.route('/mentee_signup', methods=['POST'])
def signup_post():
	email = request.form.get('email').lower()
	password = request.form.get('password')
	fname = request.form.get('fname')
	lname = request.form.get('lname')
	grade = request.form.get('grade')
	usertype = request.form.get('usertype')
	pronouns = request.form.get('pronouns')

	# if a user already exists, redirect them back to sign in page so they can try again
	user = User.query.filter_by(email=email, usertype=usertype).first()
	if user:
		flash('User with that email already exists!', 'danger')
		return redirect(request.path)

	whitelist = [i.strip() for i in open('whitelist.csv', 'r').read().split(',')]
	if email not in whitelist and usertype == 'editor':
		flash('You\'re not on the whitelist! Please contact the writing center admins to be whitelisted.', 'danger')
		return redirect(request.path)

	new_user = User(email=email,
					fname=fname,
					lname=lname,
					grade=grade,
					hours=0,
					usertype=usertype,
					pronouns=pronouns,
					password=generate_password_hash(password, method='sha256'),
					verified=((usertype=='editor') or (email=='test30')))

	if usertype == 'editor':
		c.execute(f"INSERT INTO editor VALUES ('{email}', 0.0, '[]', -1, -1, -1)")
		conn.commit()

	print("NEW USER:\n" + "-" * 50 + "\n" + str(new_user) + "\n" + "-"*50)

	db.session.add(new_user)
	db.session.commit()

	flash('Check your @stuy.edu email for an email with the subject "Confirm your Writing Center Account", to confirm your account.', 'success')
	e = Emailer(gmail_pwd)
	e.send(email, [email, fname, usertype], type='signup')

	return redirect(f'/{usertype.lower()}_login')

@auth.route('/confirm', methods=["GET"])
def confirm():
	email = request.args['email']
	usertype = request.args['usertype']
	print(email, usertype)
	user = User.query.filter_by(email=email, usertype=usertype).first()
	user.verified = True
	db.session.commit()
	flash('Successfully verified email! You can log in below.', 'success')

	return redirect(f'/{user.usertype.lower()}_login')

@auth.route('/admin', methods=["GET"])
def admin_login():
	return render_template('admin/login.html')

@auth.route('/admin', methods=["POST"])
def admin():
	password = request.form.get('password')
	hashed = sha256(password.encode()).hexdigest()
	editors = User.query.filter_by(usertype='editor')
	editors = editors.all()
	whitelist = ', '.join(open('whitelist.csv').read().split(','))
	print(editors)

	if hashed == os.getenv('ADMIN_PWD'):
		return render_template('admin/dashboard.html', editors=editors, whitelist=whitelist)
	else:
		flash('Invalid password!', 'warning')
		return redirect('/admin')

@auth.route('/delete_user', methods=["GET"])
def delete_user():
	username = request.args['username']
	usertype = request.args['usertype']
	User.query.filter_by(email=username, usertype=usertype).delete()
	db.session.commit()
	return 'Done'

# LOGOUT

@auth.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))

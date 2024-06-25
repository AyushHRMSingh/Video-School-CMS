# Store this code in 'app.py' file
import extfun
from flask import Flask, render_template, request, redirect, url_for, session
import re


app = Flask(__name__)


app.secret_key = 'your secret key'

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		valid = extfun.login(username, password)
		if valid:
			session['loggedin'] = True
			session['username'] = username
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))



@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		valid = extfun.add_user(username, password)
		msg = "User added"
	return render_template('register.html', msg = msg)


if __name__ == '__main__':
	extfun.setup()
	app.run(debug = True)
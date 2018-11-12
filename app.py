from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField, BooleanField,SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')

db = SQLAlchemy(app)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200),nullable=False)
	body = db.Column(db.String(300),nullable=False)
	complete = db.Column(db.Boolean)
	date = db.Column(db.Date,nullable=False)
	author = db.Column(db.String(100))

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200))
	username = db.Column(db.String(200),nullable=False)
	password = db.Column(db.String(300),nullable=False)
	create_date = db.Column(db.Date, default=datetime.utcnow)
	email = db.Column(db.String(200))

# #Confug MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'myflaskapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#
# #Init MySQL
# mysql = MySQL(app)


#Articles = Articles()

@app.route('/')
@app.route('/index')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

#User register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# #Create cursor
		# cur = mysql.connection.cursor()

		#Execute
		# cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s )", (name, email, username, password))
		user = User(name = name, email = email, username = username, password = password)
		db.session.add(user)
		#Commit to DB
		# mysql.connection.commit()
		db.session.commit()

		#Close connection
		# cur.close()

		flash('You are now regiistered and can log in', 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form=form)

#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#Get Form Fields
		username = request.form['username']
		password_candidate = request.form['password']

		# #Create cursor
		# cur = mysql.connection.cursor()

		# #Get user by username
		# result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		user = User.query.filter_by(username=username).first()

		if user != None:
			# Get stored hash
			password = user.password

			# Compare Passwords
			if sha256_crypt.verify(password_candidate, password):
				#Passed
				session['logged_in'] = True
				session ['username'] = username

				flash('You are now logged in', 'success')
				return redirect(url_for('todolist'))
			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)
			# # Close connection
			# cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html', error=error)


	return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap


#Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'sucess')
	return redirect(url_for('login'))


# Todolist
@app.route('/todolist')
@is_logged_in
def todolist():
	#Create cursor
	# cur = mysql.connection.cursor()

	# Get articles
	# result = cur.execute("SELECT * FROM articles")

	# articles = cur.fetchall()

	items = Todo.query.filter_by(author=session['username']).all()

	if items != None:
		return render_template('todolist.html', items=items)
	else:
		msg = 'No Items found'
		return render_template('todolist.html', msg=msg)

# Complete Tasks
@app.route('/complete')
@is_logged_in
def complete():
	items = Todo.query.filter_by(complete=True).all()
	if items != None:
		return render_template("complete.html",items=items)
	else:
		msg = 'No Items found'
		return render_template('complete.html', msg=msg)

# Incomplete Tasks
@app.route('/incomplete')
@is_logged_in
def incomplete():
	items = Todo.query.filter_by(complete=False).all()
	if items != None:
		return render_template("incomplete.html",items=items)
	else:
		msg = 'No Items found'
		return render_template('incomplete.html', msg=msg)

	#Close connection
	# cur.close()

# Add Item form
class AddItemForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = StringField('Body', [validators.Length(min=0)])
	date = DateField('Date', format='%Y-%m-%d')

# Item form
class ItemForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = StringField('Body', [validators.Length(min=0)])
	date = DateField('Date', format='%Y-%m-%d')
	complete = SelectField('Status', coerce=str, choices = [("True", "Complete"), ("False", "Incomplete")])

#Dashboard
@app.route('/add_item', methods=['GET', 'POST'])
@is_logged_in
def add_item():
	form = AddItemForm(request.form)
	form.date.data = datetime.strptime("2018-01-01", "%Y-%m-%d")
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		date = form.date.data

		#Create Cursor
		# cur = mysql.connection.cursor()

		#Execute
		# cur.execute("INSERT INTO articles(title, body, date, author) VALUES(%s, %s, %s)", (title, body, date, session['username']))

		#Commit to DB
		# mysql.connection.commit()

		#Close connection
		# cur.close()

		todo = Todo(title=title, body=body, date=date, author=session['username'],complete=False)
		db.session.add(todo)
		db.session.commit()

		flash('Item Created', 'success')

		return redirect(url_for('todolist'))

	return render_template('add_item.html', form=form)


#Edit article
@app.route('/edit_item/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_item(id):

	#Create cursor
	# cur = mysql.connection.cursor()

	#Get article by id
	# result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	# article = cur.fetchone()

	todo = Todo.query.filter_by(id=id).first()

	#Get form
	form = ItemForm(request.form)
	form.date.data = todo.date
	#Populate article form fields
	form.title.data = todo.title
	form.body.data = todo.body
	if todo.complete == True:
		form.complete.data = "True"
	else:
		form.complete.data = "False"

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']
		complete = request.form['complete']

		#Create Cursor
		# cur = mysql.connection.cursor()

		#Execute
		# cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))

		#Commit to DB
		# mysql.connection.commit()

		#Close connection
		# cur.close()

		todo.title = title
		todo.body = body
		if complete == "True":
			todo.complete = True
		else:
			todo.complete = False
		db.session.commit()

		flash('Item Update', 'success')

		return redirect(url_for('todolist'))

	return render_template('edit_item.html', form=form)

#Delete Article
@app.route('/delete_item/<string:id>', methods=['POST'])
@is_logged_in
def delete_item(id):

	#Create cursor
	# cur = mysql.connection.cursor()
	#
	# #Execute
	# cur.execute("DELETE FROM articles WHERE id = %s", [id])
	#
	# # Commit to DB
	# mysql.connection.commit()
	#
	# # Close connection
	# cur.close()

	todo = Todo.query.filter_by(id=id).first()
	db.session.delete(todo)
	db.session.commit()

	flash('Item Deleted', 'success')

	return redirect(url_for('todolist'))

# Done Item
@app.route('/done_item/<string:id>', methods=['POST'])
@is_logged_in
def done_item(id):
	todo = Todo.query.filter_by(id=id).first()
	todo.complete = True
	db.session.commit()

	flash('Item Finished', 'success')

	return redirect(url_for('incomplete'))

if __name__ == '__main__':
	app.secret_key = 'secret123'
	app.run(debug=True)

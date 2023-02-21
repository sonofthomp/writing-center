from . import db, conn, c
from flask_login import UserMixin

class User(UserMixin, db.Model):
	email = db.Column(db.String(100), unique=True, primary_key=True)
	password = db.Column(db.String(100), unique=False)
	fname = db.Column(db.String(100), unique=False)
	lname = db.Column(db.String(100), unique=False)
	grade = db.Column(db.Integer, unique=False)
	hours = db.Column(db.Float, unique=False, default=0)
	months = db.Column(db.String(1000), unique=False, default='{}')
	usertype = db.Column(db.String(6), unique=False)
	pronouns = db.Column(db.String(100), unique=False)
	verified = db.Column(db.Boolean, default=False, unique=False)

	def __repr__(self):
		return f'Email: {self.email}\nPassword: {self.password}\nFirst Name: {self.fname}\nLast Name: {self.lname}\nGrade: {self.grade}\nUser Type: {self.usertype}\nPronouns: {self.pronouns}\nVerified: {self.verified}\nMonths: {self.months}'

	def get_id(self):
		return self.email

class OrderedQueue:
	def __init__(self):
		c.execute("SELECT * FROM queue")
		self.values = c.fetchone()[0].split(',')
		if self.values == ['']:
			self.values = []

		for index, i in enumerate(self.values):
			self.values[index] = int(i)

		c.execute("SELECT rowid, * FROM requests")
		data = c.fetchall()
		self.data = {i[0]: i[15] for i in data}
		print('-'*100)
		print(self.data)
		print('-'*100)

	def __repr__(self):
		return str(self.values)[1:-1]

	def insert(self, new_entry, timestamp):
		if not self.values:
			self.values.append(new_entry)
			return

		for index, item in enumerate(self.values):
			if timestamp > self.values[index]:
				self.values.insert(index, new_entry)
				return

	def remove(self, remove_id):
		self.values.remove(remove_id)

	def pop(self):
		return self.values.pop(0)

	def write(self):
		c.execute("DELETE FROM queue;")
		c.execute(f"INSERT INTO queue VALUES ('{self.__repr__()}')")
		conn.commit()

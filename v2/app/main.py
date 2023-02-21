from flask import Blueprint, render_template, url_for, flash, get_flashed_messages, request, redirect
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from time import mktime
from dotenv import load_dotenv
from emails import *
from json import loads
import os
from .models import OrderedQueue, User
from . import db, c, conn

COURSES = sorted([
	'European Literature',
	'Acting',
	'American Literature',
	'Creative Nonfiction',
	'Asian American Literature',
	'Writing to Make Change',
	'Poetry',
	'Writers Workshop',
	'AP English – American Literary History',
	'AP English – Defining American Voices',
	'AP English – Contemporaries & Classics',
	'AP English – American Places & Perspectives',
	'AP English – Great Books',
	'AP English – Society & Self',
	'Freshman Composition',
	'Existentionalism',
	'Science Fiction',
	'Shakespearean Literature',
	'Writing in the World',
	'Women\'s Voices in Literature',
	'Leadership and Decision Making'
])

TEACHERS = {
	'Maura Dwyer': 'dwyer',
	'Eric Ferencz': 'eferencz2',
	'Katherine Fletcher': 'msfletcher',
	'Hugh Francis': 'hfrancis',
	'Kerry Garfinkel': 'kgarfin',
	'Eric Grossman': 'mr.grossman',
	'Dermot Hannon': 'hannon',
	'Mark Henderson': 'mhenderson',
	'Minkyu Kim': 'mkim24',
	'Katherine Kincaid': 'kkincaid',
	'David Mandler': 'dmandler',
	'Kim Manning': 'kmanning',
	'Rosa Mazzurco': 'ms.mazzurco',
	'Emily Moore': 'emoore',
	'Emilio Nieves': 'enieves',
	'Sophie Oberfield': 'oberfield',
	'Alicia Pohan': 'apohan',
	'Julie Sheinman': 'jsheinman',
	'Ellis Staley': 'estaley',
	'Lauren Stuzin': 'lstuzin',
	'Annie Thoms': 'athoms',
	'Megan Weller': 'mweller',
	'Alice Yang': 'ayang'
}

main = Blueprint('main', __name__)
load_dotenv()
gmail_pwd = os.getenv('EMAIL_PWD')

@main.route('/')
def index():
	loggedin = False
	if current_user.is_authenticated:
		loggedin = True
	return render_template('static_pages/landing.html', loggedin=loggedin)

@main.route('/about')
def about():
	all_editors = User.query.filter_by(usertype='editor').order_by(User.hours.desc()).all()
	return render_template('static_pages/about.html', editors=all_editors)

@main.route('/dashboard', methods=["GET", "POST"])
@login_required
def profile():
	if current_user.verified == False:
		flash('You have not verified your email! Check your email for an email verification link.', 'danger')
		return redirect('/')

	c.execute('SELECT rowid, * FROM requests')
	requests = c.fetchall()

	if current_user.usertype.lower() == 'editor':
		ordered_requests = []

		c.execute("SELECT rowid, * FROM requests WHERE editor_matched = 2")
		finished = c.fetchall()

		c.execute(f"SELECT rowid, * FROM requests WHERE editor_matched = 1 AND editor_email = '{current_user.email}'")
		pending = c.fetchall()

		c.execute("SELECT rowid, * FROM requests WHERE editor_matched = 0")
		unselected = c.fetchall()

		no_selected = True
		no_current = True

		num_unfulfilled = len(unselected)
		no_selected = (len(pending) == 0)
		no_current = (len(unselected) == 0)

		print(f'Pending: {pending}')

		return render_template('editor/dashboard.html',
							   fname=current_user.fname,
							   lname=current_user.lname,
							   pending=pending,
							   unselected=unselected,
							   no_current=no_current,
							   no_selected=no_selected,
							   num_unfulfilled=num_unfulfilled)
	else:
		num_active = 0
		requests = [request for request in requests if request[4] == current_user.email]

		for request in requests:
			if request[13] < 2:
				num_active += 1

		print(requests)

		return render_template('mentee/dashboard.html',
							   fname=current_user.fname,
							   lname=current_user.lname,
							   requests=requests,
							   num_active=num_active)

@main.route('/unaccept_piece', methods=['GET'])
@login_required
def unaccept_piece():
	if 'id' not in request.args:
		return redirect('/dashboard')

	c.execute(f"SELECT * FROM editor WHERE email = '{current_user.email}'")
	user = c.fetchone()
	user = list(user)
	user[2] = eval(user[2])

	user[2].remove(int(request.args['id']))
	user[2] = str(user[2])
	user = tuple(user)
	c.execute(f"DELETE FROM editor WHERE email = '{current_user.email}'")
	c.execute(f"INSERT INTO editor VALUES {user}")
	c.execute(f"UPDATE requests SET editor_matched = 0 WHERE rowid = '{request.args['id']}'")
	c.execute(f"UPDATE requests SET editor_email = '' WHERE rowid = '{request.args['id']}'")
	c.execute(f"UPDATE requests SET editor_name = 'Prodip Goldman' WHERE rowid = {request.args['id']}")
	conn.commit()

	c.execute(f"SELECT * FROM editor WHERE email = '{current_user.email}'")
	return redirect('/dashboard')

@main.route('/events', methods=['GET'])
def events():
	c.execute("SELECT * FROM events")
	events = c.fetchall()
	events = [list(event) for event in events]

	for index in range(len(events)):
		events[index][0] = events[index][0].replace('"', "'")
		events[index][1] = events[index][1].replace('"', "'")

	return render_template('static_pages/events.html', events=events)

@main.route('/create_piece', methods=['GET'])
@login_required
def create_piece_get():
	if current_user.usertype.lower() == 'mentee':
		return render_template('mentee/make_request.html', teachers=TEACHERS, courses=COURSES)
	return 'you cant be here'

@main.route('/create_piece', methods=['POST'])
@login_required
def create_piece_post():
	fname = request.form.get('fname')
	lname = request.form.get('lname')
	grade = int(request.form.get('grade'))
	email = request.form.get('email')
	pronouns = request.form.get('pronouns')
	teacher = request.form.get('teacher')
	course = request.form.get('course')
	period = int(request.form.get('period'))
	help_ = request.form.get('help').replace('"', '""')
	assignment_sheet = request.form.get('assignment_sheet')
	google_doc = request.form.get('google_doc')
	in_person = 1#request.form.get('in_person')

	if in_person == 'on':
		in_person = 1
	elif in_person == 'off':
		in_person = 0

	due_date = request.form.get('due_date')
	due_time = request.form.get('due_time')
	if not due_time:
		due_time = '12:00'

	year, month, day = map(int, due_date.split('-'))
	hour, minute = map(int, due_time.split(':'))
	date_time = datetime(year, month, day, hour, minute) - timedelta(hours=4)
	timestamp = mktime(date_time.timetuple())

	months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	timestamp_text = datetime.utcfromtimestamp(timestamp).strftime(f"%A, %b %d %Y %I:%M %p") #.replace(' 0', ' ')
	now = datetime.now().strftime(f"%A, %b %d 2022 %Y %H:%M")[:-2]

	c.execute(f'''
		INSERT INTO requests VALUES ("{fname}",
									 "{lname}",
									  {grade},
									 "{email}",
									 "{pronouns}",
									 "{teacher}",
									 "{course}",
									  {period},
									 "{help_}",
									 "{assignment_sheet}",
									 "{google_doc}",
									 "{now}",
									  0,
									 "",
									 "",
									  {timestamp},
									 "{timestamp_text}",
									 0,
									 "",
									 "",
									 {in_person}
									 )
	''')

	#e = Emailer(gmail_pwd)
	#editors = ','.join([i.email.replace('@stuy.edu', '')+'@stuy.edu' for i in User.query.filter_by(usertype='editor')])
	#e.send(editors, ['Editor'], type='newrequest')

	conn.commit()
	oq = OrderedQueue()
	oq.insert(c.lastrowid, timestamp)
	oq.write()

	return redirect('/dashboard')

@main.route('/delete_entry', methods=['GET'])
@login_required
def delete_entry():
	if 'id' not in request.args:
		return redirect('/dashboard')

	c.execute(f"DELETE FROM requests WHERE rowid = {request.args['id']}")
	conn.commit()

	#oq = OrderedQueue()
	#oq.remove(int(request.args['id']))
	#oq.write()
	return redirect('/dashboard')

@main.route('/select_entry', methods=['GET'])
@login_required
def select_entry():
	if 'id' not in request.args:
		return redirect('/dashboard')

	c.execute(f"SELECT * FROM editor WHERE email = '{current_user.email}'")
	user = c.fetchone()
	user = list(user)
	user[2] = eval(user[2])

	if int(request.args['id']) in user[2]:
		return "Already been added!"

	user[2].append(int(request.args['id']))
	user[2] = str(user[2])
	user = tuple(user)

	c.execute(f"SELECT requester_fname, requester_lname, requester_email FROM requests where rowid = '{request.args['id']}'")
	fname, lname, email = c.fetchone()
	e = Emailer(gmail_pwd)
	e.send(email, [fname + ' ' + lname, current_user.fname + ' ' + current_user.lname, current_user.email], type='matched')

	c.execute(f"DELETE FROM editor WHERE email = '{current_user.email}'")
	c.execute(f"INSERT INTO editor VALUES {user}")
	c.execute(f"UPDATE requests SET editor_matched = 1 WHERE rowid = '{request.args['id']}'")
	c.execute(f"UPDATE requests SET editor_email = '{current_user.email}' WHERE rowid = '{request.args['id']}'")
	c.execute(f"UPDATE requests SET editor_name = '{current_user.fname} {current_user.lname}' WHERE rowid = {request.args['id']}")
	conn.commit()

	c.execute(f"SELECT * FROM editor WHERE email = '{current_user.email}'")
	print(c.fetchone())
	return redirect('/dashboard')

@main.route('/complete_entry', methods=['GET'])
@login_required
def complete_entry_get():
	return render_template('editor/complete_entry.html')

@main.route('/complete_entry', methods=['POST'])
@login_required
def complete_entry_post():
	if current_user.usertype.lower() == 'editor':
		tags = request.form.get('tags')
		_id = request.form.get('id')
		hours = request.form.get('hours')
		_help = request.form.get('help').replace("'", '"')
		c.execute(f"UPDATE requests SET hours = {hours} WHERE rowid = '{_id}'")
		c.execute(f"UPDATE requests SET helped = '{_help}' WHERE rowid = '{_id}'")
		c.execute(f"UPDATE requests SET tags = '{tags}' WHERE rowid = '{_id}'")
		c.execute(f"UPDATE requests SET editor_matched = 1 WHERE rowid = '{_id}'")
		conn.commit()

		c.execute(f"SELECT * FROM requests WHERE rowid = '{_id}'")
		r = c.fetchone()

		e = Emailer(gmail_pwd)
		frist, lsat = r[14].split(' ')
		e.send(r[3], [r[0], frist, lsat, _id], type='completed')

		flash(f'Sent email to {r[0]} {r[1]} confirm your description', 'info')
		return redirect('/dashboard')
	else:
		return f'''
		<h1>git away noobz!</h1>
		'''

@main.route('/add_editors', methods=['POST'])
def add_editors():
	add_whitelist = request.form.get('add_whitelist')
	print(request.form)
	names = open('whitelist.csv', 'r').read().strip()
	names = names.split(',')[1:]
	names += [i.strip() for i in add_whitelist.split(',')]
	f = open('whitelist.csv', 'w')
	f.write(','.join(names))
	return redirect('/admin')

@main.route('/delete_editor', methods=["GET"])
def delete_editor():
	editor = request.args['editor']
	User.query.filter_by(email=editor).delete()
	db.session.commit()
	return redirect('/admin')

@main.route('/add_entry', methods=["POST"])
def add_entry():
	entry = request.form.get("add_entry").replace("'", '"')
	date = request.form.get("date")
	time = request.form.get("time")
	title = request.form.get("title").replace("'", '"')
	c.execute(f"INSERT INTO events VALUES ('{title}', '{entry}', '{date}, {time}')")
	conn.commit()
	return redirect('/admin')

@main.route('/feedback', methods=["GET"])
def feedback():
	_id = int(request.args['id'])
	c.execute(f"SELECT * FROM requests WHERE rowid = '{_id}'")
	r = c.fetchone()
	return render_template('mentee/feedback.html', tags=r[18].split(','), hours=r[17], helped=r[19], editor=r[14])

@main.route('/finish', methods=['POST'])
def finish():
	communicative = request.form.get('quality')
	edits = request.form.get('edits')
	overall = request.form.get('overall')
	comments = request.form.get('comments')
	_id = request.form.get('id')

	c.execute(f"SELECT * FROM requests WHERE rowid = '{_id}'")
	row = c.fetchone()
	r = list(row)
	r.append(datetime.now().strftime("%m/%d/%Y"))
	r[18] = ', '.join(r[18].split(','))

	c.execute(f"UPDATE requests SET editor_matched = 2 WHERE rowid = '{_id}'")
	c.execute(f"SELECT * FROM requests WHERE rowid = '{_id}'")
	row = c.fetchone()
	conn.commit()

	editor = User.query.filter_by(email=r[13]).first()
	editor.hours += float(r[17])
	db.session.commit()

	month = str(datetime.now().year * 12 + datetime.now().month)
	history = loads(current_user.months)
	if month in history:
		history[month] += r[17]
	else:
		history[month] = r[17]

	current_user.months = str(history).replace("'", '"')
	db.session.commit()

	e = Emailer(gmail_pwd)
	#e.send('gthompson30', r, type='finish')
	e.send(TEACHERS[row[5]], r, type='finish')
	e.send('gthompson30', [editor.fname + ' ' + editor.lname, communicative, edits, overall, comments], type='editorfeedback')
	return redirect('/dashboard')

@main.route('/credits', methods=['GET'])
def view_hours():
	all_editors = User.query.filter_by(usertype='editor').order_by(User.hours.desc()).all()
	current_month = str(datetime.now().year * 12 + datetime.now().month)

	for index, editor in enumerate(all_editors):
		months = loads(editor.months)
		if current_month in months:
			all_editors[index].months = months[current_month]
		else:
			all_editors[index].months = 0

	all_editors = sorted(all_editors, key=lambda x: x.months)
	print("All editors:")
	print(all_editors)

	if current_user.hours == 0:
		credits = "0"
	else:
		credits = "1"

	return render_template('editor/hours.html', hours=current_user.hours, editors=all_editors, latest=current_user.months, credits=credits)

@main.route('/edit_entry', methods=['GET'])
@login_required
def edit_entry():
	return 'Has not been implemented yet'

@main.route('/stats', methods=['GET'])
def stats():
	out = '<h1>Requests</h1><ul>'
	c.execute("SELECT * FROM requests")
	for i in c.fetchall():
		out += f'<li>{i}</li>'
	out += "</ul>"

	out += '<h1>Editors</h1>'
	for i in User.query.filter_by(usertype='editor').all():
		out += f'<li>{i}</li>'
	out += "</ul>"

	out += '<h1>Mentees</h1>'
	for i in User.query.filter_by(usertype='mentee').all():
		out += f'<li>{i}</li>'
	out += "</ul>"

	return out



@main.route('/editor_tutorial', methods=["GET"])
def editor_tutorial():
	return render_template('editor/editor_tutorial.html')

@main.route('/mentee_tutorial', methods=["GET"])
def mentee_tutorial():
	return render_template('mentee/mentee_tutorial.html')

@main.route('/faq', methods=["GET"])
def faq():
	return render_template('static_pages/faq.html')

@main.route('/leadership', methods=["GET"])
def leadership():
	return render_template('static_pages/leadership.html')

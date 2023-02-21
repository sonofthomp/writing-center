import sqlite3
import os

with open('~/writing-center/v3/log.txt', 'w') as f:
	f.write('')

with open('app/db.sqlite', 'w') as f:
	f.write('')

os.system('python3 -c "from app import db, create_app, models ; db.create_all(app=create_app())"')

open('whitelist.csv', 'w').write('')

conn = sqlite3.connect('requests.db')
c = conn.cursor()

try:
	c.execute('DROP TABLE requests')
except:
	pass

try:
	c.execute('DROP TABLE editor')
except:
	pass

try:
	c.execute('DROP TABLE queue')
except:
	pass

try:
	c.execute('DROP TABLE events')
except:
	pass

c.execute("""
	CREATE TABLE requests (
		requester_fname text,
		requester_lname text,
		requester_grade integer,
		requester_email text,
		requester_pronouns text,
		teacher text,
		course text,
		period integer,
		help text,
		assignment_link text,
		essay_link text,
		timestamp text,
		editor_matched integer,
		editor_email text,
		editor_name text,
		due real,
		due_text text,
		hours real,
		tags text,
		helped text,
		in_person integer
	)""")

c.execute("""
	CREATE TABLE editor (
		email text,
		hours real,
		selected text,
		quality real,
		edits real,
		overall real
	)""")

c.execute("""
	CREATE TABLE queue (
		queue text
	)""")

c.execute("""
	CREATE TABLE events (
		title text,
		content text,
		date_ text
	)""")

c.execute("INSERT INTO queue VALUES ('')")

conn.commit()
conn.close()

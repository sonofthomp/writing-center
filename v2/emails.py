import smtplib as smtp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

templates = {
	'signup': {
		'subject': '[Writing Center] Confirm your email address',
		'plain': '''
			Dear {params[1]},

			Thanks for signing up for a Writing Center {params[2]} account!

			To confirm your sign-up, please click the link below:

			https://wc.stuy.edu/confirm?email={params[0]}&usertype={params[2]}

			Sincerely,
			Gabriel Thompson, IT Director
		''',
		'html': '''
			<p>Dear <b>{params[1]}</b>,</p>
			<p>Thanks for signing up for a Writing Center {params[2]} account!</p>
			<p>To confirm your registration, please click the button below:</p>
			<p>
				<a href="http://wc.stuy.edu/confirm?email={params[0]}&usertype={params[2]}">
					<button>Confirm account</button>
				</a>
			</p>
			<p>Sincerely,
			<br>
			Gabriel Thompson, IT Director</p>
		'''
	},
	'completed': {
		'subject': '''[Writing Center] {params[1]} {params[2]} has finished editing your essay!''',
		'plain': '''
			Dear {params[0]},

			Your editor ({params[1]} {params[2]}) has finished editing your essay!

			Please fill click the link below to verify the edits made by the editor, and to complete a feedback form!

			http://wc.stuy.edu/feedback?id={params[3]}

			Sincerely,
			Gabriel Thompson, IT Director
		''',
		'html': '''
			<p>Dear {params[0]},</p>
			<p>Your editor, <b>{params[1]} {params[2]}</b>, has finished editing your essay!</p>
			<p>Please fill click the button below to verify the edits made by the editor, and to complete a feedback form!</p>
			<p>
				<a href="http://wc.stuy.edu/feedback?id={params[3]}">
					<button>Give Feedback</button>
				</a>
			</p>
			<p>Sincerely,
			<br>
			Gabriel Thompson, IT Director</p>
		'''
	},
	'matched': {
		'subject': '''[Writing Center] You've been paired''',
		'plain': '''
			Hi yeet chunguser,

			You've been yeet chungused
		''',
		'html': '''
			<p>Hi {params[0]},</p>
			<p>You've been paired with <b>{params[1]}</b>! Their email is {params[2]}@stuy.edu. If your editor does not editor your essay via Google Docs in a timely manner, or does not reach out to you to meet in-person, feel free to contact them or execswritingcenter@gmail.com.</p>
			<br>
			<p>Sincerely,
			<br>
			Gabriel Thompson, IT Director</p>
		'''
	},
	'newrequest': {
		'subject': '''[Writing Center] New Edit Request''',
		'html': '''
			<p>Hi {params[0]},</p>
			<p>A mentee just created a new edit request!</p>
			<p>You can find it on the Writing Center website <a href="http://wc.stuy.edu/dashboard">here</a></p>
			<br>
			<p>Sincerely,
			<br>
			Gabriel Thompson, IT Director</p>
		''',
		'plain': 'Oh sneaky youre reading the little text next to the subject huh?'
	},
	'editorfeedback': {
		'subject': 'editor feedback for {params[0]}',
		'plain': 'yeet chungus',
		'html': '<p>There was a chungus attack at ground zero for {params[0]}. but in other news, the communicative was {params[1]}, the edits was {params[2]} the overall was {params[3]} the comments was {params[4]}</p>'
	},
	'finish': {
		'subject': '''[Writing Center] Edit receipt for {params[0]} {params[1]} in pd{params[7]} {params[6]}''',
		'plain': '''
			Hi {params[5]},

			This is a feedback form from 
		''',
		'html': '''
			<p>Hi {params[5]},</p>

			<p>Here is the feedback form for {params[0]} {params[1]}'s essay for your {params[6]} class</p>

			<center>
				<table>
					<tr>
						<td style="text-align: right; background-color: rgb(170, 193, 240)">
							<b>Student:</b>
						</td>
						<td style="background-color: rgb(204, 217, 245); width: 35vw;">{params[0]} {params[1]}</td>
					</tr>
					<tr>
						<td style="text-align: right; background-color: rgb(189, 214, 172)">
							<b>Teacher, Class, Period:</b>
						</td>
						<td style="background-color: rgb(220, 233, 213)">{params[6]}, Period {params[7]}</td>
					</tr>
					<tr>
						<td style="text-align: right; background-color: rgb(170, 193, 240)">
							<b>Editor:</b>
						</td>
						<td style="background-color: rgb(204, 217, 245)">{params[14]}</td>
					</tr>
					<tr>
						<td style="text-align: right; background-color: rgb(189, 214, 172)">
							<b>Date:</b>
						</td>
						<td style="background-color: rgb(220, 233, 213)">{params[21]}</td>
					</tr>
					<tr>
						<td style="text-align: right; background-color: rgb(170, 193, 240)">
							<b>Tags:</b>
						</td>
						<td style="background-color: rgb(204, 217, 245)">{params[18]}</td>
					</tr>
					<tr>
						<td style="text-align: right; background-color: rgb(189, 214, 172)">
							<b>Comments:</b>
						</td>
						<td style="background-color: rgb(220, 233, 213)">{params[19]}</td>
					</tr>
				</table>
			</center>
		'''
	}
}

class Emailer:

	def __init__(self, password):
		self.password = password
		self.from_addr = 'stuywcwebsite@gmail.com'

	def send(self, to_email, params, type='signup'):
		conn = smtp.SMTP_SSL('smtp.gmail.com', 465)
		print(self.from_addr, self.password)
		conn.login(self.from_addr, self.password)
		template = templates[type]

		msg = MIMEMultipart('alternative')

		msg['Subject'] = template['subject'].format(
			params=params
		)
		msg['From'] = self.from_addr
		msg['To'] = to_email

		plain_text = MIMEText(template['plain'].format(params=params), 'plain')
		html = MIMEText(template['html'].format(params=params), 'html')
		msg.attach(plain_text)
		msg.attach(html)

		conn.sendmail(self.from_addr,
					  to_email + '@stuy.edu',
					  msg.as_string())
		conn.close()

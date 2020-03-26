from utils import process_query, parse_page
from flask import Flask, render_template, request
from flask_mail import Mail, Message


app = Flask(__name__)
app.config.update(DEBUG = True)
	#EMAIL SETTINGS
settings = {
	"MAIL_SERVER":'smtp.gmail.com',
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	"MAIL_USERNAME": 'azat.nuriakhmetov@gmail.com',
	"MAIL_PASSWORD": 'upgerqzbewknjndm'
	}
app.config.update(settings)
mail = Mail(app)


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/process", methods=["POST"])
def process():
	query = request.form.get("query")
	email = request.form.get("email")
	login = request.form.get("login")
	password = request.form.get("password")
	file_path = process_query(query, login, password)
	try:
		msg = Message("Test-Shmest",
			sender='azat.nuriakhmetov@gmail.com',
			recipients = ['azatn@sabanciuniv.edu'])
		msg.body = "Parsing was successful, file created!"
		with app.open_resource(file_path) as fo:
			msg.attach("test_list.xlsx", "text/csv", fo.read())
		mail.send(msg)
		print("Mail sent")
	except Exception as e:
		print(str(e))

	return render_template("results.html", query = query, email = email, file_path=file_path)


if __name__ == "__main__":
	app.run(port=5000, debug=True)
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'whitebear7720@gmail.com',
    MAIL_PASSWORD = 'tathuylinh',
    MAIL_DEFAULT_SENDER = ("IPT", "whitebear7720@gmail.com")
))


mail = Mail(app)

body = "Hi {},\n"

with app.app_context():
    with mail.connect() as conn:
        msg = Message(recipients=['thuylinh7720@gmail.com'],
                        body='...',
                        subject="Confirmation Email")
        conn.send(msg)
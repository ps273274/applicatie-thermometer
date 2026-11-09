#Importeert libraries
from flask import Flask
FROM flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app) #Bevestigt dat de mail word gebruikt in de app

#Configuratie van de mail
class Config:
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = TRUE
    MAIL_USE_SSL = FALSE
    MAIL_USERNAME = "your_email@gmail.com"
    MAIL_PASSWORD = "your_password"
    SECRET_KEY = "your_secret_key"

@app.route("/")
def index():
    msg = Message(
        'Hello, flask test mail',
        sender ='your_email@gmail.com',
        recipients = ['receiver’sid@gmail.com']
        )
    msg.body = 'Flask message sent from Flask-Mail'
    mail.send(msg)
    return "Sent"

    if __name__ == "__main__":
        app.run(debug=True)
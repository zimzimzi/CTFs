from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = open("secret.key", "rb").read()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://hackchan:hackchan@postgres:5432/hackchan'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = '/'
login_manager.init_app(app)

from views import *


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80,debug=False)

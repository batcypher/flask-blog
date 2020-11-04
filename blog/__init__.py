import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_mail import Mail
from blog.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# using config here for testing only 
app.config['SECRET_KEY'] = '64529050a317171fa534714b75b55b03'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# otherwise use config.from_object to get environment vars
# set env vars for email_user and email_pass

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
markdown = Markdown(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
mail = Mail(app)


# registering blueprints
from blog.auth.routes import auth
from blog.posts.routes import posts
from blog.main.routes import main


app.register_blueprint(auth)
app.register_blueprint(posts)
app.register_blueprint(main)
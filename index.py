from flask import Flask
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from connector.mysql_connector import connection
from controllers.user import user_routes
from controllers.account import account_routes
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from models.user import User
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(user_routes)
app.register_blueprint(account_routes)


jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(User).get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)



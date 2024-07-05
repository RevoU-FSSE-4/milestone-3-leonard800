from flask import Blueprint, request, jsonify
from connector.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.user import User
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
import secrets

user_routes = Blueprint("user_routes", __name__)

@user_routes.route('/register', methods=['POST'])
def register_user():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        NewUser = User(
            username=request.form['username'],
            email=request.form['email']
        )

        NewUser.set_password(request.form['password'])

        s.add(NewUser)
        s.commit()
        return {"message": "Registration success"}, 200
    except Exception as e:
        s.rollback()
        print(e)
        return {"message": "Registration failed"}, 500

@user_routes.route('/login', methods=['POST'])
def check_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        password = request.form['password']  
        user = s.query(User).filter(User.email == email).first()

        if user is None:
            return {"message": "User not found"}, 403
        
        if not user.check_password(password):
            return {"message": "Invalid password"}, 403
        
        login_user(user)

        session_id = secrets.token_hex(16)  # Generate a random session ID
        return {
            "session_id": session_id,
            "message": "You are now logged in"
        }, 200

    except Exception as e:
        s.rollback()
        return {"message": "Failed to log in, please try again"}, 500

@user_routes.route('/loginjwt', methods=['POST'])
def check_login_jwt():
    Session = sessionmaker(connection)
    s = Session()

    try:
        email = request.form['email']
        password = request.form['password']  
        user = s.query(User).filter(User.email == email).first()

        if user is None:
            return {"message": "User not found"}, 403
        
        if not user.check_password(password):
            return {"message": "Invalid password"}, 403
        
        access_token = create_access_token(identity=user.id, additional_claims={"token_type": "randomized"})  # Create a JWT with randomized claims

        return {
            "access_token": access_token,
            "message": "You are now logged in"
        }, 200

    except Exception as e:
        s.rollback()
        print(e)
        return {"message": "Failed to log in, please try again"}, 500
    
@user_routes.route('/logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return {"message": "Successfully logged out"}, 200

@user_routes.route('/user/me', methods=['GET'])
@jwt_required()  
def get_profile():
    user_id = get_jwt_identity()
    Session = sessionmaker(connection)
    s = Session()
    user = s.query(User).get(user_id)
    if user:
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        return jsonify(user_info), 200
    else:
        return {"message": "User not found"}, 404

@user_routes.route('/user/me', methods=['PUT'])
@jwt_required()  
def update_profile():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        user_id = get_jwt_identity()  
        user = s.query(User).get(user_id)

        if 'username' in request.form:
            user.username = request.form['username']
        if 'email' in request.form:
            user.email = request.form['email']
        if 'password' in request.form:
            user.set_password(request.form['password'])

        s.commit()
        return {"message": "Profile updated successfully"}, 200
    except Exception as e:
        s.rollback()
        return {"message": "Profile update failed"}, 500

from flask import Blueprint, request, jsonify
from connector.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.user import User
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


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

        print(NewUser)

        s.add(NewUser)
        s.commit()
        return { "message": "Registration success" }, 200 
    except Exception as e:
        s.rollback()
        print(e)
        return { "message": "Registration failed"}, 500


@user_routes.route('/login', methods=['POST'])
def check_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return { "message": "User not found" }, 403
        
        if not user.check_password(request.form['password']):
            return { "message": "Invalid password" }, 403
        
        login_user(user)

        session_id = request.cookies.get('session')

        return {
            "session_id": session_id,
            "message": "You are now logged in"
        }, 200

    except Exception as e:
        s.rollback()
        return { "message": "Failed to log in, please try again" }, 500
    
@user_routes.route('/loginjwt', methods=['POST'])
def check_login_jwt():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return { "message": "User not found" }, 403
        
        if not user.check_password(request.form['password']):
            return { "message": "Invalid password" }, 403
        
        access_token = create_access_token(identity=user.id, additional_claims= {"name": user.name, "id": user.id})

        return {
            "access_token": access_token,
            "message": "You are no logged in"
        }, 200

    except Exception as e:
        s.rollback()
        return { "message": "Gagal login" }, 500
    
@user_routes.route('/logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return { "message": "Success logout" }

@user_routes.route('/user/me', methods=['GET'])
@login_required
def get_profile():
    user = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
    return jsonify(user), 200

@user_routes.route('/user/me', methods=['PUT'])
@login_required
def update_profile():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        user = s.query(User).get(current_user.id)

        if 'username' in request.form:
            user.username = request.form['username']
        if 'email' in request.form:
            user.email = request.form['email']
        if 'password' in request.form:
            user.set_password(request.form['password'])

        s.commit()
        return { "message": "Profile updated successfully" }, 200
    except Exception as e:
        s.rollback()
        return { "message": "Profile update failed" }, 500

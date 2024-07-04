from flask import Blueprint, request, jsonify
from connector.mysql_connector import connection
from models.account import Account
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required

account_routes = Blueprint("account_routes", __name__)

@account_routes.route('/account', methods=['POST'])
@jwt_required()
def create_account():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        new_account = Account(
            user_id=current_user.id,
            account_type=request.form['account_type'],
            account_number=request.form['account_number'],
            balance=request.form['balance']
        )

        print(new_account)

        s.add(new_account)
        s.commit()
        return {"message": "Account Successfully Created"}, 200 
    except Exception as e:
        s.rollback()
        print(e)
        return {"message": "Failed to Create Account"}, 500
    finally:
        s.close()

@account_routes.route('/account', methods=['GET'])
@jwt_required()
def account_list():
    Session = sessionmaker(connection)
    s = Session()

    try:
        accounts = current_user.accounts

        account_list = []
        for account in accounts:
            account_list.append({
                "id": account.id,
                "user_id": account.user_id,
                "account_type": account.account_type,
                "account_number": account.account_number,
                "balance": account.balance,
                "created_at": account.created_at,
                "updated_at": account.updated_at
            })

        return {
            'accounts': account_list,
            'message': "Successfully fetched account data"
        }, 200

    except Exception as e:
        print(e)
        return {'message': 'Unexpected Error'}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['GET'])
@jwt_required()
def get_account(id):
    Session = sessionmaker(connection)
    s = Session()

    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            return {"message": "Account not found or unauthorized"}, 404

        account_data = {
            "id": account.id,
            "user_id": account.user_id,
            "account_type": account.account_type,
            "account_number": account.account_number,
            "balance": account.balance,
            "created_at": account.created_at,
            "updated_at": account.updated_at
        }
        return jsonify(account_data), 200

    except Exception as e:
        print(e)
        return {"message": "Unexpected Error"}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['PUT'])
@jwt_required()
def update_account(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            return {"message": "Account not found or unauthorized"}, 404

        if 'account_type' in request.form:
            account.account_type = request.form['account_type']
        if 'account_number' in request.form:
            account.account_number = request.form['account_number']
        if 'balance' in request.form:
            account.balance = request.form['balance']

        s.commit()
        return {"message": "Account successfully updated"}, 200

    except Exception as e:
        s.rollback()
        print(e)
        return {"message": "Failed to update account"}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['DELETE'])
@jwt_required()
def account_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            return {"message": "Account not found or unauthorized"}, 404
        
        s.delete(account)
        s.commit()
        return {'message': 'Account deleted'}, 200

    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Can't delete account, please try again"}, 500
    finally:
        s.close()

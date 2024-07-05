from flask import Blueprint, request, jsonify
from connector.mysql_connector import connection
from models.account import Account
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user  
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import time

account_routes = Blueprint("account_routes", __name__)

@account_routes.route('/account', methods=['POST'])
@jwt_required()
def create_account():
    user_id = get_jwt_identity()

    required_fields = ['account_type', 'account_number']
    if not all(k in request.form for k in required_fields):
        logging.error("Missing required form data")
        return {"message": "Missing required form data"}, 400

    Session = sessionmaker(connection)
    s = Session()

    try:
        new_account = Account(
            user_id=user_id,
            account_type=request.form['account_type'],
            account_number=request.form['account_number'],
            balance=float(request.form.get('balance', 0.0))
        )

        s.add(new_account)
        s.commit()

        return {"message": "Account Successfully Created", "account_id": new_account.id}, 200 

    except Exception as e:
        s.rollback()
        logging.error(f"Failed to create account: {str(e)}")
        return {"message": "Failed to Create Account"}, 500

    finally:
        s.close()

@account_routes.route('/account', methods=['GET'])
@jwt_required()
@login_required
def account_list():
    Session = sessionmaker(bind=connection)
    s = Session()

    try:
        account_query = select(Account)
        
        result = s.execute(account_query)
        account_list = []

        for row in result.scalars():
            account_list.append({
                "id": row.id,
                "user_id": row.user_id,
                "account_type": row.account_type,
                "account_number": row.account_number,
                "balance": row.balance,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            })

        logging.info("Successfully fetched account data for user: %s", current_user.id)
        return {
            'accounts': account_list,
            'message': "Successfully fetched account data"
        }, 200

    except Exception as e:
        logging.error("Failed to fetch account data: %s", str(e))
        return {'message': 'Unexpected Error'}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['GET'])
@jwt_required()
@login_required
def get_account(id):
    Session = sessionmaker(bind=connection)
    s = Session()

    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            logging.warning("Account not found or unauthorized for user: %s", current_user.id)
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
        logging.info("Account data retrieved for account ID: %s", id)
        return jsonify(account_data), 200

    except Exception as e:
        logging.error("Failed to retrieve account data: %s", str(e))
        return {"message": "Unexpected Error"}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['PUT'])
@jwt_required()
@login_required
def update_account(id):
    Session = sessionmaker(bind=connection)
    s = Session()
    s.begin()

    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            logging.warning("Account not found or unauthorized for update, account ID: %s", id)
            return {"message": "Account not found or unauthorized"}, 404

        if 'account_type' in request.form:
            account.account_type = request.form.get('account_type')
        if 'account_number' in request.form:
            account.account_number = request.form.get('account_number')
        if 'balance' in request.form:
            account.balance = request.form.get('balance')

        s.commit()
        logging.info("Account successfully updated: %s", account)
        return {"message": "Account successfully updated"}, 200

    except Exception as e:
        s.rollback()
        logging.error("Failed to update account: %s", str(e))
        return {"message": "Failed to update account"}, 500
    finally:
        s.close()

@account_routes.route('/account/<id>', methods=['DELETE'])
@jwt_required()
@login_required
def account_delete(id):
    Session = sessionmaker(bind=connection)
    s = Session()
    s.begin()
    try:
        account = s.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if account is None:
            logging.warning("Account not found or unauthorized for delete, account ID: %s", id)
            return {"message": "Account not found or unauthorized"}, 404
        
        s.delete(account)
        s.commit()
        logging.info("Account deleted, account ID: %s", id)
        return {'message': 'Account deleted'}, 200

    except Exception as e:
        s.rollback()
        logging.error("Failed to delete account: %s", str(e))
        return {"message": "Can't delete account, please try again"}, 500
    finally:
        s.close()

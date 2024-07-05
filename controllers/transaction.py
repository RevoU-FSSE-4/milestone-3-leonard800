from flask import Blueprint, request, jsonify
from connector.mysql_connector import connection
from models.transaction import Transaction
from models.account import Account
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

transaction_routes = Blueprint("transaction_routes", __name__)

@transaction_routes.route('/transaction', methods=['POST'])
@jwt_required()
def new_transaction():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    try:
        amount = request.form.get('amount')
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        transaction_type = request.form.get('type')
        description = request.form.get('description')

        if not all(['amount', 'transaction_type', 'description']):
            return { "message": "Missing required fields" }, 400

        if from_account_id:
            from_account = s.query(Account).filter(
                Account.id == from_account_id,
                Account.user_id == get_jwt_identity()
            ).first()
            if not from_account:
                return { "message": "Invalid or unauthorized from_account" }, 403

        if to_account_id:
            to_account = s.query(Account).filter(Account.id == to_account_id).first()
            if not to_account:
                return { "message": "Invalid to_account" }, 403

        new_transaction = Transaction(
            amount=amount,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            transaction_type=transaction_type,
            description=description
        )

        s.add(new_transaction)
        s.commit()
        return { "message": "Transaction successfully created" }, 200 

    except Exception as e:
        s.rollback()
        logging.error("Failed to create transaction: %s", str(e))
        return { "message": "Failed to create transaction" }, 500
    finally:
        s.close()


@transaction_routes.route('/transaction', methods=['GET'])
@jwt_required()
def list_transaction():
    Session = sessionmaker(connection)
    s = Session()

    try:
        account_id = request.args.get('account_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        transactions_query = select(Transaction).join(Account, Transaction.from_account_id == Account.id).filter(Account.user_id == current_user.id)

        if account_id:
            transactions_query = transactions_query.where((Transaction.from_account_id == account_id) | (Transaction.to_account_id == account_id))
        
        if start_date and end_date:
            transactions_query = transactions_query.where(Transaction.created_at.between(start_date, end_date))

        result = s.execute(transactions_query)
        transactions = []

        for row in result.scalars():
            transactions.append({
                "id": row.id,
                "amount": row.amount,
                "from_account_id": row.from_account_id,
                "to_account_id": row.to_account_id,
                "transaction_type": row.transaction_type,
                "description": row.description,
                "created_at": row.created_at
            })

        return { 'transactions': transactions }, 200

    except Exception as e:
        print(e)
        return { 'message': 'Unexpected Error' }, 500
    finally:
        s.close()


@transaction_routes.route('/transaction/<id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    Session = sessionmaker(connection)
    s = Session()

    try:
        transaction = s.query(Transaction).join(Account, Transaction.from_account_id == Account.id).filter(Transaction.id == id, Account.user_id == current_user.id).first()

        if transaction is None:
            return { "message": "Transaction not found or unauthorized" }, 404

        transaction_detail = {
            "id": transaction.id,
            "amount": transaction.amount,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "transaction_type": transaction.transaction_type,
            "description": transaction.description,
            "created_at": transaction.created_at
        }

        return { 'transaction': transaction_detail }, 200

    except Exception as e:
        print(e)
        return { 'message': 'Unexpected Error' }, 500
    finally:
        s.close()

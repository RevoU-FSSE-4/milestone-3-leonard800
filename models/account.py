from models.base import Base
from sqlalchemy import Integer, String, Enum, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

class Account(Base):
    __tablename__ = 'account'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    account_type = mapped_column(Enum('gold', 'silver', 'platinum', name='account_type_enum'), nullable=False)
    account_number = mapped_column(String(255), nullable=False)
    balance = mapped_column(DECIMAL(10, 2))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Account {self.name}>'


    transactions_from = relationship('Transaction', foreign_keys='Transaction.from_account_id', backref='from_account', cascade='all, delete-orphan')
    transactions_to = relationship('Transaction', foreign_keys='Transaction.to_account_id', backref='to_account', cascade='all, delete-orphan')

from models.base import Base
from sqlalchemy import Integer, String, Enum, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, backref  
from sqlalchemy.sql import func

class Transaction(Base):
    __tablename__ = 'transaction'

    id = mapped_column(Integer, primary_key=True)
    amount = mapped_column(DECIMAL(10, 2))
    from_account_id = mapped_column(Integer, ForeignKey("account.id", ondelete="CASCADE"))
    to_account_id = mapped_column(Integer, ForeignKey("account.id", ondelete="CASCADE"))
    type = mapped_column(Enum('transfer', 'deposit', 'withdraw', 'topup', name='transaction_type_enum'), nullable=False)
    description = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    # from_account = relationship('Account', foreign_keys=[from_account_id], backref=backref('transactions_from', cascade='all, delete-orphan'))
    # to_account = relationship('Account', foreign_keys=[to_account_id], backref=backref('transactions_to', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Transaction {self.id}>'

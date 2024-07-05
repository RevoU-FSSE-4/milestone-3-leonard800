from models.base import Base
from sqlalchemy import Integer, String, Enum, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

class Transaction(Base):
    __tablename__ = 'transaction'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_account_id = mapped_column(Integer, ForeignKey("account.id"))
    to_account_id = mapped_column(Integer, ForeignKey("account.id"))
    amount = mapped_column(DECIMAL(10, 2))
    transaction_type = mapped_column(Enum('transfer', 'deposit', 'withdraw', 'topup', name='transaction_type_enum'), nullable=False)
    description = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

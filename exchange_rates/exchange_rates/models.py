from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from exchange_rates.db import Base


class CurrencyModel(Base):
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))
    converter = Column(Integer)
    currency_code = Column(String(8))
    avg_exchange_rate = Column(Numeric(10, 4))
    exchange_rates_id = Column(
        "exchange_rates_id",
        Integer,
        ForeignKey("exchange_rates.id", ondelete="CASCADE"),
        nullable=False,
        unique=False,
    )
    exchange_rates = relationship("ExchangeRatesModel", back_populates="currencies")


class ExchangeRatesModel(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    created_date = Column(DateTime)
    currencies = relationship("CurrencyModel", back_populates="exchange_rates")

    def __init__(self, name: str) -> None:
        self.name = name
        self.created_date = datetime.now()

    def update_name(self, name):
        self.name = name

    def get_currency(self, currency_code):
        for currency in self.currencies:
            if currency.currency_code == currency_code:
                return currency

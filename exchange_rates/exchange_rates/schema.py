from datetime import datetime
from typing import List, Optional, Union

from fastapi import HTTPException, status
from pydantic import BaseModel, constr, root_validator

SUPPORTED_CURRENCIES = [
    "PLN",
    "THB",
    "USD",
    "AUD",
    "HKD",
    "CAD",
    "NZD",
    "SGD",
    "EUR",
    "HUF",
    "CHF",
    "GBP",
    "UAH",
    "JPY",
    "CZK",
    "DKK",
    "ISK",
    "NOK",
    "SEK",
    "RON",
    "BGN",
    "TRY",
    "ILS",
    "CLP",
    "PHP",
    "MXN",
    "ZAR",
    "BRL",
    "MYR",
    "IDR",
    "INR",
    "KRW",
    "CNY",
    "XDR",
]


class Currency(BaseModel):
    name: constr(min_length=2, max_length=64)
    currency_code: constr(min_length=2, max_length=64)
    converter: int
    avg_exchange_rate: float


class DisplayCurrency(Currency):
    id: int
    exchange_rates_id: int

    class Config:
        orm_mode = True


class ExchangeRates(BaseModel):
    name: constr(min_length=2, max_length=128)
    currencies: Optional[List[Currency]] = []


class DisplayExchangeRates(ExchangeRates):
    id: int
    created_date: datetime
    currencies: Optional[List[DisplayCurrency]] = []

    class Config:
        orm_mode = True


class RequestConvertCurrencies(BaseModel):
    from_cur: str
    to: str
    amount: int
    when: Union[datetime, None] = datetime.now()

    @root_validator(pre=True)
    def check_code_currencies(cls, values):
        values["from_cur"] = values["from_cur"].upper()
        values["to"] = values["to"].upper()
        if (
            values["from_cur"] not in SUPPORTED_CURRENCIES
            or values["to"] not in SUPPORTED_CURRENCIES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not supported currencies",
            )
        return values


class DisplayConvertCurrencies(BaseModel):
    result: float

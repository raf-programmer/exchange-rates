from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from starlette.responses import Response
from typing_extensions import Annotated

from exchange_rates import db

from . import schema, services
from .schema import RequestConvertCurrencies

router = APIRouter(tags=["ExchangeRatesModel"], prefix="/exchange_rates")


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.DisplayExchangeRates
)
async def create_exchange_rates(
    exchange_rates: schema.ExchangeRates, database: Session = Depends(db.get_db)
):
    new_exchange_rates = await services.create_exchange_rates(exchange_rates, database)
    return new_exchange_rates


@router.get("/", response_model=List[schema.DisplayExchangeRates])
async def get_all_exchange_rates(database: Session = Depends(db.get_db)):
    return await services.get_all_exchange_rates(database)


@router.get("/convert_currencies", response_model=schema.DisplayConvertCurrencies)
async def get_convert_currencies(
    _from: str,
    to: str,
    amount: Annotated[int, Query(gt=0)],
    when: datetime = datetime.now(),
    database: Session = Depends(db.get_db),
):
    request_data = RequestConvertCurrencies(
        from_cur=_from, to=to, amount=amount, when=when
    )
    result = await services.convert_currencies(
        request_data.from_cur,
        request_data.to,
        request_data.amount,
        request_data.when,
        database,
    )
    return {"result": result}


@router.get("/{exchange_rates_id}", response_model=schema.DisplayExchangeRates)
async def get_exchange_rates_by_id(
    exchange_rates_id: int, database: Session = Depends(db.get_db)
):
    return await services.get_exchange_rates_by_id(exchange_rates_id, database)


@router.put(
    "/{exchange_rates_id}",
    status_code=status.HTTP_200_OK,
    response_model=schema.DisplayExchangeRates,
)
async def update_exchange_rates_by_id(
    exchange_rates_id: int,
    exchange_rates: schema.ExchangeRates,
    database: Session = Depends(db.get_db),
):
    new_exchange_rates = await services.update_exchange_rates_by_id(
        exchange_rates_id, exchange_rates, database
    )
    return new_exchange_rates


@router.delete(
    "/{exchange_rates_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_exchange_rates_by_id(
    exchange_rates_id: int, database: Session = Depends(db.get_db)
):
    return await services.delete_exchange_rates_by_id(exchange_rates_id, database)


@router.post(
    "/save_current",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.DisplayExchangeRates,
)
async def save_current_exchange_rates(database: Session = Depends(db.get_db)):
    new_exchange_rates = await services.save_current_exchange_rates(database)
    return new_exchange_rates

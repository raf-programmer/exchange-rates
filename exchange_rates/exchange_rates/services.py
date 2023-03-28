import math
from typing import List, Optional

from fastapi import HTTPException, status

from . import models, schema
from .currencies_converter import CurrenciesConverter
from .models import ExchangeRatesModel
from .xml_parser import XMLParser


async def create_exchange_rates(
    exchange_rates: schema.ExchangeRates, database
) -> models.ExchangeRatesModel:
    new_exchange_rates = await _process_saving_exchange_rates(exchange_rates, database)
    return new_exchange_rates


async def save_current_exchange_rates(database):
    xml_parser = XMLParser()
    exchange_rates = await xml_parser.extract_data_from_xml()
    new_exchange_rates = await _process_saving_exchange_rates(exchange_rates, database)
    return new_exchange_rates


async def _process_saving_exchange_rates(exchange_rates, database):
    new_exchange_rates: ExchangeRatesModel = models.ExchangeRatesModel(
        name=exchange_rates.name
    )
    database.add(new_exchange_rates)
    database.flush()

    for currency in exchange_rates.currencies:
        db_currency = models.CurrencyModel(
            name=currency.name,
            converter=currency.converter,
            currency_code=currency.currency_code,
            avg_exchange_rate=currency.avg_exchange_rate,
            exchange_rates_id=new_exchange_rates.id,
        )
        database.add(db_currency)

    database.commit()
    database.refresh(new_exchange_rates)
    return new_exchange_rates


async def get_all_exchange_rates(database) -> List[models.ExchangeRatesModel]:
    all_exchange_rates = database.query(models.ExchangeRatesModel).all()
    return all_exchange_rates


async def get_exchange_rates_by_id(
    exchange_rates_id, database
) -> Optional[models.ExchangeRatesModel]:
    exchange_rates = database.query(models.ExchangeRatesModel).get(exchange_rates_id)
    if not exchange_rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found!"
        )
    return exchange_rates


async def update_exchange_rates_by_id(exchange_rates_id, exchange_rates_data, database):
    exchange_rates = database.query(models.ExchangeRatesModel).get(exchange_rates_id)
    if not exchange_rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found!"
        )
    exchange_rates.update_name(exchange_rates_data.name)
    database.query(models.CurrencyModel).filter(
        models.CurrencyModel.exchange_rates_id == exchange_rates_id
    ).delete()
    for currency in exchange_rates_data.currencies:
        db_currency = models.CurrencyModel(
            name=currency.name,
            converter=currency.converter,
            currency_code=currency.currency_code,
            avg_exchange_rate=currency.avg_exchange_rate,
            exchange_rates_id=exchange_rates_id,
        )
        database.add(db_currency)
    database.commit()
    database.refresh(exchange_rates)
    return exchange_rates


async def delete_exchange_rates_by_id(exchange_rates_id, database):
    database.query(models.ExchangeRatesModel).filter(
        models.ExchangeRatesModel.id == exchange_rates_id
    ).delete()
    database.commit()


async def convert_currencies(_from, to, amount, when, database):
    closest_time_exchange_rates = await _get_closest_time_exchange_rates(when, database)
    if not closest_time_exchange_rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no exchange_rates!"
        )
    currencies_converter = CurrenciesConverter()
    result = currencies_converter(_from, to, amount, closest_time_exchange_rates)
    return result


async def _get_closest_time_exchange_rates(when, databases):
    gt_or_equal_exchange_rates = (
        databases.query(models.ExchangeRatesModel)
        .filter(models.ExchangeRatesModel.created_date >= when)
        .order_by(models.ExchangeRatesModel.created_date.asc())
        .first()
    )

    lt_or_equal_exchange_rates = (
        databases.query(models.ExchangeRatesModel)
        .filter(models.ExchangeRatesModel.created_date <= when)
        .order_by(models.ExchangeRatesModel.created_date.desc())
        .first()
    )

    gt_diff = (
        (gt_or_equal_exchange_rates.created_date - when).total_seconds()
        if gt_or_equal_exchange_rates
        else math.inf
    )
    lt_diff = (
        (when - lt_or_equal_exchange_rates.created_date).total_seconds()
        if lt_or_equal_exchange_rates
        else math.inf
    )

    return (
        gt_or_equal_exchange_rates if gt_diff < lt_diff else lt_or_equal_exchange_rates
    )

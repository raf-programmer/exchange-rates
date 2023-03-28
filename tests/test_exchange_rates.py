import urllib.parse
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from conf_test_db import app, override_get_db
from exchange_rates.exchange_rates.models import (CurrencyModel,
                                                  ExchangeRatesModel)
from tests.fixture_factories import ExchangeRatesDictFactory


@pytest.mark.asyncio
class TestExchangeRates:
    async def test_new_exchange_rates(self):
        # given
        test_name = "test exchange rates"
        exchange_rates_data = ExchangeRatesDictFactory.build(
            name=test_name, currencies=[]
        )
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/exchange_rates/", json=exchange_rates_data)
        # then
        assert response.status_code == 201
        assert response.json()["name"] == test_name

    async def test_new_exchange_rates_with_currencies(self):
        # given
        exchange_rates_data = ExchangeRatesDictFactory.build()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/exchange_rates/", json=exchange_rates_data)
        # then
        assert response.status_code == 201
        assert response.json()["name"] == exchange_rates_data["name"]
        self.__assert_currencies(
            response.json()["currencies"], exchange_rates_data["currencies"]
        )

    async def test_get_exchange_rates_with_currencies(self):
        # given
        (
            exchange_rates_data,
            new_exchange_rates_id,
        ) = self.__given_exchange_rates_with_currencies()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/exchange_rates/{new_exchange_rates_id}")
        # then
        assert response.status_code == 200
        assert response.json()["name"] == exchange_rates_data["name"]
        self.__assert_currencies(
            response.json()["currencies"], exchange_rates_data["currencies"]
        )

    async def test_get_list_exchange_rates_with_currencies(self, clean_db):
        # given
        list_exchange_rates_data = self.__given_list_exchange_rates_with_currencies()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/exchange_rates/")
        # then
        assert response.status_code == 200
        for i in range(3):
            assert response.json()[i]["name"] == list_exchange_rates_data[i]["name"]
            self.__assert_currencies(
                response.json()[i]["currencies"],
                list_exchange_rates_data[i]["currencies"],
            )

    async def test_put_exchange_rates_with_currencies(self):
        # given
        (
            exchange_rates_data,
            new_exchange_rates_id,
        ) = self.__given_exchange_rates_with_currencies()
        new_exchange_rates_data = ExchangeRatesDictFactory.build()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/exchange_rates/{new_exchange_rates_id}", json=new_exchange_rates_data
            )
        # then
        assert response.status_code == 200
        assert response.json()["name"] == new_exchange_rates_data["name"]
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/exchange_rates/{new_exchange_rates_id}")
        assert response.json()["name"] == new_exchange_rates_data["name"]
        self.__assert_currencies(
            response.json()["currencies"], new_exchange_rates_data["currencies"]
        )

    async def test_delete_exchange_rates_with_currencies(self):
        # given
        (
            exchange_rates_data,
            new_exchange_rates_id,
        ) = self.__given_exchange_rates_with_currencies()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/exchange_rates/{new_exchange_rates_id}")
        # then
        assert response.status_code == 204
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/exchange_rates/{new_exchange_rates_id}")
        assert response.status_code == 404

    @patch("exchange_rates.exchange_rates.xml_parser.requests")
    async def test_save_current_exchange_rates(self, requests_mock):
        # given
        requests_mock.get.return_value.status_code = 200
        xml_content = open("tests/data/example.xml")
        requests_mock.get.return_value.content = xml_content.read()
        xml_content.close()
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/exchange_rates/save_current")
        # then
        expected_data = {
            "name": "Tabela kursów walut 058/A/NBP/2023",
            "currencies": [
                {
                    "name": "bat (Tajlandia)",
                    "converter": 1,
                    "currency_code": "THB",
                    "avg_exchange_rate": 0.1262,
                },
                {
                    "name": "forint (Wêgry)",
                    "converter": 100,
                    "currency_code": "HUF",
                    "avg_exchange_rate": 1.2132,
                },
                {
                    "name": "rand (Republika Po³udniowej Afryki)",
                    "converter": 1,
                    "currency_code": "ZAR",
                    "avg_exchange_rate": 0.2375,
                },
            ],
        }
        assert response.status_code == 201
        assert response.json()["name"] == expected_data["name"]
        self.__assert_currencies(
            response.json()["currencies"], expected_data["currencies"]
        )

    async def test_convert_currencies_based_on_latest_exchange_with_basic_pln_currency(
        self, clean_db
    ):
        # given
        exchange_rates_data, _ = self.__given_exchange_rates_with_currencies()
        converted_from_currency = exchange_rates_data["currencies"][0]
        code_converted_from_currency = converted_from_currency["currency_code"]
        converter_from_value = converted_from_currency["converter"]
        avg_exchange_rate_value = converted_from_currency["avg_exchange_rate"]
        amount_to_convert = 50
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/exchange_rates/convert_currencies?_from={code_converted_from_currency}&to=pln&amount={amount_to_convert}"
            )
        # then
        assert response.status_code == 200
        assert int(response.json()["result"]) == int(
            amount_to_convert * avg_exchange_rate_value / converter_from_value
        )

    async def test_convert_currencies_based_on_nearest_time_exchange(self, clean_db):
        # given
        self.__given_exchange_rates_with_currencies()
        past_datetime = datetime.now() - timedelta(days=7)
        exchange_rates_data, _ = self.__given_exchange_rates_with_currencies(
            created_date=past_datetime
        )
        converted_from_currency = exchange_rates_data["currencies"][0]
        code_converted_from_currency = converted_from_currency["currency_code"]
        converter_from_value = converted_from_currency["converter"]
        avg_exchange_rate_from = converted_from_currency["avg_exchange_rate"]
        amount_to_convert = 325
        converted_to_currency = exchange_rates_data["currencies"][1]
        code_converted_to_currency = converted_to_currency["currency_code"]
        converter_to_value = converted_to_currency["converter"]
        avg_exchange_rate_to = converted_to_currency["avg_exchange_rate"]
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/exchange_rates/convert_currencies?_from={code_converted_from_currency.lower()}&to={code_converted_to_currency.lower()}&amount={amount_to_convert}&when={urllib.parse.quote(str(past_datetime))}"
            )
        # then
        assert response.status_code == 200
        expected_result = (
            amount_to_convert
            * avg_exchange_rate_from
            / converter_from_value
            * converter_to_value
            / avg_exchange_rate_to
        )
        assert int(response.json()["result"]) == int(expected_result)

    async def test_convert_currencies_should_return_400_when_unsupported_currencies(
        self, clean_db
    ):
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/exchange_rates/convert_currencies?_from=ves&to=pln&amount=50"
            )
        # then
        assert response.status_code == 400

    async def test_convert_currencies_should_return_404_when_there_is_no_exchange_rates(
        self, clean_db
    ):
        # when
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/exchange_rates/convert_currencies?_from=usd&to=pln&amount=50"
            )
        # then
        assert response.status_code == 404

    def __given_exchange_rates_with_currencies(self, created_date=None):
        exchange_rates_data = ExchangeRatesDictFactory.build()
        db = next(override_get_db())
        new_exchange_rates = ExchangeRatesModel(name=exchange_rates_data["name"])
        if created_date:
            new_exchange_rates.created_date = created_date
        db.add(new_exchange_rates)
        db.flush()
        for currency_data in exchange_rates_data["currencies"]:
            new_currency = CurrencyModel(
                exchange_rates_id=new_exchange_rates.id, **currency_data
            )
            db.add(new_currency)
        db.commit()
        db.refresh(new_exchange_rates)
        return exchange_rates_data, new_exchange_rates.id

    def __given_list_exchange_rates_with_currencies(self):
        list_exchange_rates_with_currencies = []
        for i in range(3):
            exchange_rates_data, _ = self.__given_exchange_rates_with_currencies()
            list_exchange_rates_with_currencies.append(exchange_rates_data)
        return list_exchange_rates_with_currencies

    def __assert_currencies(self, returned_data, expected_data):
        checked_keys = ("name", "currency_code", "converter", "avg_exchange_rate")
        for element in range(3):
            filtered_returned_data_to_check = {
                key: returned_data[element][key]
                for key in returned_data[element]
                if key in checked_keys
            }
            assert filtered_returned_data_to_check == expected_data[element]

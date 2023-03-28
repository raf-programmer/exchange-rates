import pytest

from conf_test_db import override_get_db
from exchange_rates.exchange_rates.models import ExchangeRatesModel


@pytest.fixture(scope="function")
def clean_db():
    db = next(override_get_db())
    db.query(ExchangeRatesModel).delete()
    db.commit()

import factory
from factory.fuzzy import FuzzyChoice


class CurrencyDictFactory(factory.DictFactory):
    name = factory.Faker("currency_name")
    converter = 1
    currency_code = factory.fuzzy.FuzzyChoice(
        [
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
        ]
    )
    avg_exchange_rate = factory.Faker(
        "pyfloat", positive=True, max_value=100, right_digits=4
    )


class ExchangeRatesDictFactory(factory.DictFactory):
    name = factory.Faker("text", max_nb_chars=32)
    currencies = factory.List(
        [factory.SubFactory(CurrencyDictFactory) for _ in range(3)]
    )

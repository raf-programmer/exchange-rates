from exchange_rates.exchange_rates.models import ExchangeRatesModel

BASE_CURRENCY_CODE = "PLN"


class CurrenciesConverter:
    def __call__(
        self, _from: str, to: str, amount: int, exchange_rates: ExchangeRatesModel
    ):
        if _from == BASE_CURRENCY_CODE or to == BASE_CURRENCY_CODE:
            result = self.__calculate_with_basic_currency(
                _from, to, amount, exchange_rates
            )
        else:
            result = self.__calculate_without_basic_currency(
                _from, to, amount, exchange_rates
            )
        return round(result, 2)

    def __calculate_with_basic_currency(self, _from, to, amount, exchange_rates):
        if _from == BASE_CURRENCY_CODE:
            currency = exchange_rates.get_currency(to)
            result = currency.converter * amount / currency.avg_exchange_rate
        else:
            currency = exchange_rates.get_currency(_from)
            result = currency.avg_exchange_rate * amount / currency.converter
        return result

    def __calculate_without_basic_currency(self, _from, to, amount, exchange_rates):
        from_currency = exchange_rates.get_currency(_from)
        to_currency = exchange_rates.get_currency(to)
        result = (
            from_currency.avg_exchange_rate
            / from_currency.converter
            * to_currency.converter
            / to_currency.avg_exchange_rate
            * amount
        )
        return result

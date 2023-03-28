import xml.etree.ElementTree as ET

import requests

from exchange_rates.exchange_rates.schema import ExchangeRates

CURRENT_EXCHANGE_RATES_URL = "https://static.nbp.pl/dane/kursy/xml/LastA.xml"


class XMLParser:
    async def extract_data_from_xml(self):
        response = requests.get(CURRENT_EXCHANGE_RATES_URL)
        if response.status_code == 200:
            xml_content = response.content
            root = ET.fromstring(xml_content)
            exchange_rates_name = "Tabela kursów walut "
            currencies_data = []
            for child in root:
                data_type, data = self.__extract_data_from_element(child)
                if data_type == "pozycja":
                    currencies_data.append(data)
                if data_type == "numer_tabeli":
                    exchange_rates_name += data
            return ExchangeRates.parse_obj(
                {"name": exchange_rates_name, "currencies": currencies_data}
            )

    def __extract_data_from_element(self, child):
        if child.tag == "pozycja":
            data = {
                self.__map_field_name(c.tag): self.__prepare_number_data(
                    (c.tag, c.text)
                )
                for c in child.getchildren()
            }
        elif child.tag == "numer_tabeli":
            data = child.text
        else:
            data = None
        return child.tag, data

    def __map_field_name(self, key):
        mapping = {
            "nazwa_waluty": "name",
            "przelicznik": "converter",
            "kod_waluty": "currency_code",
            "kurs_sredni": "avg_exchange_rate",
        }
        return mapping[key]

    def __prepare_number_data(self, data):
        data_type, value = data
        if data_type == "przelicznik":
            value = int(value)
        if data_type == "kurs_sredni":
            value = float(value.replace(",", "."))
        return value

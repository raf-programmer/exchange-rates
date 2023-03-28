from fastapi import FastAPI

from exchange_rates.exchange_rates import router as exchange_rates_router

app = FastAPI(title="ExchangeRatesApp", version="0.0.1")

app.include_router(exchange_rates_router.router)

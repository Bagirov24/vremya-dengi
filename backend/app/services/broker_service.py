from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
from datetime import datetime


class BrokerBase(ABC):
    @abstractmethod
    async def get_portfolio(self, api_key: str) -> list:
        pass

    @abstractmethod
    async def get_trades(self, api_key: str, from_date: Optional[datetime] = None) -> list:
        pass

    @abstractmethod
    async def get_dividends(self, api_key: str) -> list:
        pass

    @abstractmethod
    async def validate_key(self, api_key: str) -> bool:
        pass


class TinkoffBroker(BrokerBase):
    BASE_URL = "https://invest-public-api.tinkoff.ru/rest"

    def _headers(self, api_key: str):
        return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async def validate_key(self, api_key: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(
                    f"{self.BASE_URL}/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts",
                    headers=self._headers(api_key), json={}
                )
                return r.status_code == 200
            except Exception:
                return False

    async def get_portfolio(self, api_key: str) -> list:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts",
                headers=self._headers(api_key), json={}
            )
            accounts = r.json().get("accounts", [])
            if not accounts:
                return []
            account_id = accounts[0]["id"]
            r2 = await client.post(
                f"{self.BASE_URL}/tinkoff.public.invest.api.contract.v1.OperationsService/GetPortfolio",
                headers=self._headers(api_key),
                json={"accountId": account_id, "currency": "RUB"}
            )
            return r2.json().get("positions", [])

    async def get_trades(self, api_key: str, from_date=None) -> list:
        return []

    async def get_dividends(self, api_key: str) -> list:
        return []


class FinamBroker(BrokerBase):
    BASE_URL = "https://trade-api.finam.ru/api/v1"

    def _headers(self, api_key: str):
        return {"X-Api-Key": api_key}

    async def validate_key(self, api_key: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{self.BASE_URL}/accounts",
                    headers=self._headers(api_key)
                )
                return r.status_code == 200
            except Exception:
                return False

    async def get_portfolio(self, api_key: str) -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/portfolio",
                headers=self._headers(api_key)
            )
            return r.json().get("positions", []) if r.status_code == 200 else []

    async def get_trades(self, api_key: str, from_date=None) -> list:
        return []

    async def get_dividends(self, api_key: str) -> list:
        return []


def get_broker(name: str) -> BrokerBase:
    brokers = {
        "tinkoff": TinkoffBroker(),
        "finam": FinamBroker(),
    }
    broker = brokers.get(name.lower())
    if not broker:
        raise ValueError(f"Unknown broker: {name}")
    return broker

"""Dummy parser implementations for prototype development/testing."""

from __future__ import annotations

import random

from app.core.models import CarParams, Offer
from app.parsers.base import BaseSiteParser


class _DummyBaseParser(BaseSiteParser):
    """Base helper class that creates deterministic synthetic offers."""

    price_shift: float = 0.0

    def __init__(self) -> None:
        self._rng = random.Random(self.source_name)

    def search_offers(self, params: CarParams) -> list[Offer]:
        base_price = self._estimate_base_price(params)
        offers: list[Offer] = []

        for idx in range(self._rng.randint(10, 20)):
            price_factor = self._rng.uniform(0.8, 1.2) + self.price_shift
            year_delta = self._rng.randint(-2, 2)
            mileage_delta = self._rng.randint(-60_000, 60_000)

            offer = Offer(
                source=self.source_name,
                title=f"{params.brand} {params.model} • предложение {idx + 1}",
                price=max(int(base_price * price_factor), 120_000),
                year=max(params.year + year_delta, 1990),
                mileage=max(params.mileage + mileage_delta, 10_000),
                region=params.region,
                url=f"https://{self.source_name.lower()}.example.com/{params.brand.lower()}-{params.model.lower()}-{idx}",
            )
            offers.append(offer)

        return offers

    def _estimate_base_price(self, params: CarParams) -> int:
        age = max(2026 - params.year, 0)
        depreciation = age * 45_000 + int(params.mileage * 0.35)
        condition_coef = {
            "Нормальное": 1.0,
            "После ДТП": 0.8,
            "Требует ремонта": 0.7,
            "Отличное": 1.1,
        }.get(params.condition, 1.0)
        base = int((1_800_000 - depreciation) * condition_coef)
        return max(base, 250_000)


class DummySiteParser1(_DummyBaseParser):
    """First test source parser implementation."""

    source_name = "Сайт1"
    price_shift = -0.02


class DummySiteParser2(_DummyBaseParser):
    """Second test source parser implementation."""

    source_name = "Сайт2"
    price_shift = 0.03

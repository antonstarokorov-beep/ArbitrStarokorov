"""Valuation logic based on comparable offers."""

from __future__ import annotations

from statistics import median

from app.core.models import Offer, ValuationResult, ValuationStats
from app.core.settings import OUTLIER_THRESHOLD, RANGE_HIGH_COEF, RANGE_LOW_COEF


class ValuationEngine:
    """Applies filtering and calculates final market value/statistics."""

    def deduplicate_by_url(self, offers: list[Offer]) -> list[Offer]:
        unique: dict[str, Offer] = {}
        for offer in offers:
            unique.setdefault(offer.url.strip(), offer)
        return list(unique.values())

    def remove_price_outliers(self, offers: list[Offer]) -> list[Offer]:
        if not offers:
            return []
        median_price = median(offer.price for offer in offers)
        filtered: list[Offer] = []
        for offer in offers:
            diff_ratio = abs(offer.price - median_price) / median_price
            if diff_ratio <= OUTLIER_THRESHOLD:
                filtered.append(offer)
        return filtered

    def preprocess_offers(self, offers: list[Offer]) -> list[Offer]:
        """Apply mandatory cleanup pipeline before presenting/calculating."""
        deduped = self.deduplicate_by_url(offers)
        return self.remove_price_outliers(deduped)

    def calculate(self, offers: list[Offer]) -> ValuationResult:
        if not offers:
            raise ValueError("Нет объявлений для расчёта")

        prices = [offer.price for offer in offers]
        median_price = int(median(prices))
        stats = ValuationStats(
            min_price=min(prices),
            max_price=max(prices),
            average_price=int(sum(prices) / len(prices)),
            median_price=median_price,
            comparable_count=len(offers),
        )

        range_min = int(median_price * RANGE_LOW_COEF)
        range_max = int(median_price * RANGE_HIGH_COEF)

        return ValuationResult(
            market_value=median_price,
            range_min=range_min,
            range_max=range_max,
            stats=stats,
        )

"""Domain models used across the valuation application."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CarParams:
    """Input parameters that describe the car under valuation."""

    brand: str
    model: str
    year: int
    mileage: int
    region: str
    condition: str


@dataclass(slots=True)
class Offer:
    """Comparable offer collected from a marketplace source."""

    source: str
    title: str
    price: int
    year: int
    mileage: int
    region: str
    url: str


@dataclass(slots=True)
class ValuationStats:
    """Descriptive statistics over the comparable offers sample."""

    min_price: int
    max_price: int
    average_price: int
    median_price: int
    comparable_count: int


@dataclass(slots=True)
class ValuationResult:
    """Output of valuation engine with market value and price range."""

    market_value: int
    range_min: int
    range_max: int
    stats: ValuationStats


@dataclass(slots=True)
class EvaluationRecord:
    """Persisted evaluation row from SQLite history."""

    id: int
    created_at: datetime
    brand: str
    model: str
    year: int
    mileage: int
    region: str
    condition: str
    final_value: int
    range_min: int
    range_max: int

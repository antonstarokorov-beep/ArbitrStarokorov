"""Parser abstraction for different offer sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.models import CarParams, Offer


class BaseSiteParser(ABC):
    """Abstract parser interface used by GUI/business logic."""

    source_name: str

    @abstractmethod
    def search_offers(self, params: CarParams) -> list[Offer]:
        """Return a list of offers that match given car parameters."""

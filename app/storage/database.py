"""SQLite storage for evaluations and related offers."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from app.core.models import CarParams, EvaluationRecord, Offer, ValuationResult


class Database:
    """Thin database access layer used by GUI actions."""

    def __init__(self, db_path: str = "valuation_history.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    mileage INTEGER NOT NULL,
                    region TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    final_value INTEGER NOT NULL,
                    range_min INTEGER NOT NULL,
                    range_max INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    mileage INTEGER NOT NULL,
                    region TEXT NOT NULL,
                    url TEXT NOT NULL,
                    used_in_calculation INTEGER NOT NULL,
                    FOREIGN KEY(evaluation_id) REFERENCES evaluations(id)
                )
                """
            )

    def save_evaluation(
        self,
        params: CarParams,
        result: ValuationResult,
        offers_with_flags: list[tuple[Offer, bool]],
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO evaluations (
                    created_at, brand, model, year, mileage, region, condition,
                    final_value, range_min, range_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    params.brand,
                    params.model,
                    params.year,
                    params.mileage,
                    params.region,
                    params.condition,
                    result.market_value,
                    result.range_min,
                    result.range_max,
                ),
            )
            evaluation_id = cursor.lastrowid

            conn.executemany(
                """
                INSERT INTO offers (
                    evaluation_id, source, title, price, year, mileage, region, url, used_in_calculation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        evaluation_id,
                        offer.source,
                        offer.title,
                        offer.price,
                        offer.year,
                        offer.mileage,
                        offer.region,
                        offer.url,
                        1 if used else 0,
                    )
                    for offer, used in offers_with_flags
                ],
            )

        return int(evaluation_id)

    def get_evaluations(self) -> list[EvaluationRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM evaluations ORDER BY created_at DESC"
            ).fetchall()

        return [
            EvaluationRecord(
                id=row["id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                brand=row["brand"],
                model=row["model"],
                year=row["year"],
                mileage=row["mileage"],
                region=row["region"],
                condition=row["condition"],
                final_value=row["final_value"],
                range_min=row["range_min"],
                range_max=row["range_max"],
            )
            for row in rows
        ]

    def get_offers_for_evaluation(self, evaluation_id: int) -> list[tuple[Offer, bool]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM offers WHERE evaluation_id = ? ORDER BY id ASC",
                (evaluation_id,),
            ).fetchall()

        return [
            (
                Offer(
                    source=row["source"],
                    title=row["title"],
                    price=row["price"],
                    year=row["year"],
                    mileage=row["mileage"],
                    region=row["region"],
                    url=row["url"],
                ),
                bool(row["used_in_calculation"]),
            )
            for row in rows
        ]

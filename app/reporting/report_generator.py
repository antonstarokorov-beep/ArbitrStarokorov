"""HTML and PDF report generation."""

from __future__ import annotations

from html import escape
from pathlib import Path

from xhtml2pdf import pisa

from app.core.models import CarParams, Offer, ValuationResult


class ReportGenerator:
    """Builds an HTML report and converts it to PDF."""

    def build_html(
        self,
        params: CarParams,
        result: ValuationResult,
        offers: list[Offer],
    ) -> str:
        rows = "\n".join(
            (
                "<tr>"
                f"<td>{escape(offer.source)}</td>"
                f"<td>{escape(offer.title)}</td>"
                f"<td>{offer.price:,} ₽</td>"
                f"<td>{offer.year}</td>"
                f"<td>{offer.mileage:,}</td>"
                f"<td>{escape(offer.region)}</td>"
                f"<td><a href='{escape(offer.url)}'>{escape(offer.url)}</a></td>"
                "</tr>"
            )
            for offer in offers
        )

        return f"""
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <style>
    body {{ font-family: DejaVu Sans, Arial, sans-serif; font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
    th, td {{ border: 1px solid #bbb; padding: 6px; vertical-align: top; }}
    h1 {{ font-size: 20px; }}
    h2 {{ margin-top: 20px; font-size: 16px; }}
    .summary {{ background: #f6f6f6; padding: 10px; border: 1px solid #bbb; }}
  </style>
</head>
<body>
  <h1>Отчёт об оценке рыночной стоимости автомобиля</h1>

  <h2>Данные оцениваемого автомобиля</h2>
  <ul>
    <li>Марка/модель: {escape(params.brand)} {escape(params.model)}</li>
    <li>Год выпуска: {params.year}</li>
    <li>Пробег: {params.mileage:,} км</li>
    <li>Регион: {escape(params.region)}</li>
    <li>Состояние: {escape(params.condition)}</li>
  </ul>

  <h2>Описание методики</h2>
  <p>
    Оценка выполнена сравнительным подходом на основании предложений о продаже аналогичных автомобилей.
    Из выборки удалены дубли и ценовые выбросы, затем рассчитаны статистические показатели.
    Итоговая рыночная стоимость определена по медиане цен аналогов.
  </p>

  <h2>Таблица аналогов</h2>
  <table>
    <thead>
      <tr>
        <th>Источник</th>
        <th>Название</th>
        <th>Цена</th>
        <th>Год</th>
        <th>Пробег</th>
        <th>Регион</th>
        <th>URL</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <h2>Результат</h2>
  <div class="summary">
    <p><strong>Итоговая рыночная стоимость:</strong> {result.market_value:,} ₽</p>
    <p><strong>Диапазон стоимости:</strong> {result.range_min:,} ₽ — {result.range_max:,} ₽</p>
    <p><strong>Количество учтённых аналогов:</strong> {result.stats.comparable_count}</p>
  </div>
</body>
</html>
""".strip()

    def save_pdf(self, html: str, output_path: str) -> None:
        target = Path(output_path)
        with target.open("wb") as f:
            status = pisa.CreatePDF(src=html, dest=f, encoding="utf-8")
        if status.err:
            raise RuntimeError("Не удалось сформировать PDF")

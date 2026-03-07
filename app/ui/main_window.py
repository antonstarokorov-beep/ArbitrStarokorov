"""PyQt6 GUI for the car valuation prototype."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.models import CarParams, Offer, ValuationResult
from app.core.settings import CONDITIONS, DEFAULT_BRANDS, DEFAULT_MODELS
from app.core.valuation import ValuationEngine
from app.parsers.base import BaseSiteParser
from app.parsers.dummy import DummySiteParser1, DummySiteParser2
from app.reporting.report_generator import ReportGenerator
from app.storage.database import Database


class MainWindow(QMainWindow):
    """Main application window and UI event handlers."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Оценка автомобиля (сравнительный подход)")
        self.resize(1300, 780)

        self.engine = ValuationEngine()
        self.database = Database()
        self.report_generator = ReportGenerator()
        self.parsers: dict[str, BaseSiteParser] = {
            "Сайт1": DummySiteParser1(),
            "Сайт2": DummySiteParser2(),
        }

        self.current_offers: list[Offer] = []
        self.current_result: ValuationResult | None = None
        self.current_params: CarParams | None = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.valuation_tab = self._build_valuation_tab()
        self.history_tab = self._build_history_tab()

        self.tabs.addTab(self.valuation_tab, "Оценка")
        self.tabs.addTab(self.history_tab, "История оценок")

        self._refresh_history()

    def _build_valuation_tab(self) -> QWidget:
        root = QWidget()
        layout = QVBoxLayout(root)

        form_group = QGroupBox("Параметры автомобиля")
        form_layout = QFormLayout(form_group)

        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText("Например: Toyota")
        self.brand_edit.setCompleter(QCompleter(DEFAULT_BRANDS))

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Например: Camry")
        self.model_edit.setCompleter(QCompleter(DEFAULT_MODELS))

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1980, 2030)
        self.year_spin.setValue(2018)

        self.mileage_spin = QSpinBox()
        self.mileage_spin.setRange(0, 1_000_000)
        self.mileage_spin.setSingleStep(5_000)
        self.mileage_spin.setValue(90_000)

        self.region_edit = QLineEdit()
        self.region_edit.setPlaceholderText("Город / регион")

        self.condition_combo = QComboBox()
        self.condition_combo.addItems(CONDITIONS)

        form_layout.addRow("Марка", self.brand_edit)
        form_layout.addRow("Модель", self.model_edit)
        form_layout.addRow("Год выпуска", self.year_spin)
        form_layout.addRow("Пробег (км)", self.mileage_spin)
        form_layout.addRow("Регион", self.region_edit)
        form_layout.addRow("Состояние", self.condition_combo)

        parser_group = QGroupBox("Сайты-источники")
        parser_layout = QHBoxLayout(parser_group)
        self.site_checkboxes: dict[str, QCheckBox] = {}
        for site_name in self.parsers:
            checkbox = QCheckBox(site_name)
            checkbox.setChecked(True)
            self.site_checkboxes[site_name] = checkbox
            parser_layout.addWidget(checkbox)

        actions_layout = QHBoxLayout()
        self.find_button = QPushButton("Найти аналоги")
        self.find_button.clicked.connect(self._search_offers)
        self.calculate_button = QPushButton("Рассчитать стоимость")
        self.calculate_button.clicked.connect(self._calculate_value)
        self.report_button = QPushButton("Сформировать отчёт (PDF)")
        self.report_button.clicked.connect(self._generate_report)

        actions_layout.addWidget(self.find_button)
        actions_layout.addWidget(self.calculate_button)
        actions_layout.addWidget(self.report_button)

        self.offers_table = QTableWidget(0, 8)
        self.offers_table.setHorizontalHeaderLabels(
            [
                "Источник",
                "Название",
                "Цена",
                "Год",
                "Пробег",
                "Регион",
                "URL",
                "Учитывать",
            ]
        )
        self.offers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.offers_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        result_group = QGroupBox("Результат расчёта")
        result_layout = QFormLayout(result_group)
        self.value_label = QLabel("—")
        self.range_label = QLabel("—")
        self.stats_label = QLabel("—")
        result_layout.addRow("Итоговая стоимость", self.value_label)
        result_layout.addRow("Диапазон", self.range_label)
        result_layout.addRow("Статистика", self.stats_label)

        layout.addWidget(form_group)
        layout.addWidget(parser_group)
        layout.addLayout(actions_layout)
        layout.addWidget(self.offers_table)
        layout.addWidget(result_group)

        return root

    def _build_history_tab(self) -> QWidget:
        root = QWidget()
        layout = QVBoxLayout(root)

        self.history_table = QTableWidget(0, 10)
        self.history_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Дата/время",
                "Марка",
                "Модель",
                "Год",
                "Пробег",
                "Регион",
                "Стоимость",
                "Диапазон min",
                "Диапазон max",
            ]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self._refresh_history)
        details_btn = QPushButton("Открыть объявления")
        details_btn.clicked.connect(self._open_history_offers)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(details_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.history_table)
        return root

    def _read_params(self) -> CarParams:
        brand = self.brand_edit.text().strip()
        model = self.model_edit.text().strip()
        region = self.region_edit.text().strip()

        if not brand or not model or not region:
            raise ValueError("Заполните поля: марка, модель и регион")

        return CarParams(
            brand=brand,
            model=model,
            year=int(self.year_spin.value()),
            mileage=int(self.mileage_spin.value()),
            region=region,
            condition=self.condition_combo.currentText(),
        )

    def _selected_parsers(self) -> list[BaseSiteParser]:
        return [
            parser
            for name, parser in self.parsers.items()
            if self.site_checkboxes[name].isChecked()
        ]

    def _search_offers(self) -> None:
        try:
            params = self._read_params()
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        selected_parsers = self._selected_parsers()
        if not selected_parsers:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один сайт-источник")
            return

        offers: list[Offer] = []
        for parser in selected_parsers:
            offers.extend(parser.search_offers(params))

        offers = self.engine.preprocess_offers(offers)
        self.current_params = params
        self.current_offers = offers
        self.current_result = None
        self._fill_offers_table(offers)
        self.value_label.setText("—")
        self.range_label.setText("—")
        self.stats_label.setText(f"Найдено объявлений после фильтрации: {len(offers)}")

        if not offers:
            QMessageBox.information(
                self,
                "Нет данных",
                "После фильтрации не осталось объявлений. Измените параметры поиска.",
            )

    def _fill_offers_table(self, offers: list[Offer], usage_flags: list[bool] | None = None) -> None:
        self.offers_table.setRowCount(len(offers))
        if usage_flags is None:
            usage_flags = [True] * len(offers)

        for row, (offer, is_used) in enumerate(zip(offers, usage_flags)):
            values = [
                offer.source,
                offer.title,
                f"{offer.price:,}",
                str(offer.year),
                f"{offer.mileage:,}",
                offer.region,
                offer.url,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col in (2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.offers_table.setItem(row, col, item)

            check_item = QTableWidgetItem()
            check_item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )
            check_item.setCheckState(Qt.CheckState.Checked if is_used else Qt.CheckState.Unchecked)
            self.offers_table.setItem(row, 7, check_item)

    def _selected_offers_for_calculation(self) -> list[Offer]:
        selected: list[Offer] = []
        for row, offer in enumerate(self.current_offers):
            item = self.offers_table.item(row, 7)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected.append(offer)
        return selected

    def _calculate_value(self) -> None:
        if not self.current_offers:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните поиск аналогов")
            return

        selected_offers = self._selected_offers_for_calculation()
        if not selected_offers:
            QMessageBox.warning(self, "Ошибка", "Нет выбранных объявлений для расчёта")
            return

        try:
            result = self.engine.calculate(selected_offers)
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        self.current_result = result
        self.value_label.setText(f"{result.market_value:,} ₽")
        self.range_label.setText(f"{result.range_min:,} ₽ — {result.range_max:,} ₽")
        self.stats_label.setText(
            " | ".join(
                [
                    f"min: {result.stats.min_price:,}",
                    f"max: {result.stats.max_price:,}",
                    f"avg: {result.stats.average_price:,}",
                    f"median: {result.stats.median_price:,}",
                    f"n: {result.stats.comparable_count}",
                ]
            )
        )

        try:
            params = self.current_params or self._read_params()
            offers_with_flags = [
                (offer, offer in selected_offers)
                for offer in self.current_offers
            ]
            self.database.save_evaluation(params, result, offers_with_flags)
            self._refresh_history()
        except Exception as exc:  # pragma: no cover
            QMessageBox.warning(self, "Ошибка БД", f"Не удалось сохранить оценку: {exc}")

    def _generate_report(self) -> None:
        if not self.current_result or not self.current_params:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните расчёт стоимости")
            return

        offers_for_report = self._selected_offers_for_calculation()
        if not offers_for_report:
            QMessageBox.warning(self, "Ошибка", "Нет выбранных объявлений для отчёта")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            "report.pdf",
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return

        try:
            html = self.report_generator.build_html(
                self.current_params,
                self.current_result,
                offers_for_report,
            )
            self.report_generator.save_pdf(html, output_path)
            QMessageBox.information(self, "Готово", f"PDF сохранён:\n{output_path}")
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сформировать отчёт: {exc}")

    def _refresh_history(self) -> None:
        records = self.database.get_evaluations()
        self.history_table.setRowCount(len(records))

        for row, record in enumerate(records):
            values = [
                str(record.id),
                record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                record.brand,
                record.model,
                str(record.year),
                f"{record.mileage:,}",
                record.region,
                f"{record.final_value:,}",
                f"{record.range_min:,}",
                f"{record.range_max:,}",
            ]
            for col, value in enumerate(values):
                self.history_table.setItem(row, col, QTableWidgetItem(value))

    def _open_history_offers(self) -> None:
        selected = self.history_table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "История", "Выберите строку в таблице истории")
            return

        evaluation_id_item = self.history_table.item(selected, 0)
        if not evaluation_id_item:
            return

        evaluation_id = int(evaluation_id_item.text())
        offers_with_flags = self.database.get_offers_for_evaluation(evaluation_id)
        if not offers_with_flags:
            QMessageBox.information(self, "История", "Для оценки нет сохранённых объявлений")
            return

        offers = [item[0] for item in offers_with_flags]
        flags = [item[1] for item in offers_with_flags]

        self.tabs.setCurrentWidget(self.valuation_tab)
        self.current_offers = offers
        self._fill_offers_table(offers, flags)
        QMessageBox.information(
            self,
            "История",
            f"Загружено {len(offers)} объявлений для оценки #{evaluation_id}",
        )

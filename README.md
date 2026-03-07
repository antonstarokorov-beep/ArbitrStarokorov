# ArbitrStarokorov — прототип оценки автомобиля

Настольное приложение на **Python + PyQt6** для арбитражного управляющего, которое помогает оценивать рыночную стоимость автомобиля сравнительным подходом по аналогам из объявлений.

## Возможности прототипа

- ввод параметров оцениваемого авто (марка, модель, год, пробег, регион, состояние);
- выбор сайтов-источников (заглушки `Сайт1` и `Сайт2`);
- поиск и показ аналогов в таблице;
- исключение отдельных объявлений из расчёта через чекбоксы;
- расчёт итоговой стоимости (по медиане), диапазона и статистики;
- сохранение результатов и объявлений в SQLite (`valuation_history.db`);
- просмотр истории оценок и загрузка объявлений из истории;
- формирование отчёта в PDF (HTML -> PDF через `xhtml2pdf`).

## Структура проекта

```text
.
├── app/
│   ├── core/         # модели и расчёт
│   ├── parsers/      # интерфейс парсера и dummy-реализации
│   ├── reporting/    # генерация HTML/PDF отчёта
│   ├── storage/      # SQLite слой
│   └── ui/           # PyQt6 интерфейс
├── main.py           # точка входа
└── requirements.txt
```

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```


## Быстрый запуск на Windows (в 1 клик)

В репозитории добавлены готовые bat-скрипты:

- `run_windows.bat` — создаёт `.venv`, ставит зависимости и запускает приложение;
- `build_windows.bat` — создаёт `.venv`, ставит зависимости и собирает `dist\CarValuationApp.exe`.

Запуск:

1. Откройте папку проекта в Проводнике.
2. Дважды кликните `run_windows.bat`.
3. Дождитесь установки зависимостей и запуска окна программы.

Сборка EXE:

1. Дважды кликните `build_windows.bat`.
2. После успешной сборки используйте `dist\CarValuationApp.exe`.

## Сборка в один EXE (Windows)

```bash
pyinstaller --noconfirm --onefile --windowed --name CarValuationApp main.py
```

Готовый исполняемый файл будет в папке `dist/CarValuationApp.exe`.

## Примечания

- Парсеры в `app/parsers/dummy.py` не делают реальных HTTP-запросов и генерируют тестовые данные.
- Для интеграции с реальными сайтами достаточно добавить новые классы-парсеры, наследующие `BaseSiteParser`, и подключить их в UI.


## Если не работает

1. Проверьте Python:

```bash
py -3 --version
```

2. Переустановите зависимости в виртуальном окружении:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Запустите приложение:

```bash
python main.py
```

4. Если не формируется PDF, установите модуль отдельно:

```bash
pip install xhtml2pdf
```

5. Если `pip` не может скачать пакеты (прокси/корпоративная сеть), укажите прокси:

```bash
pip install -r requirements.txt --proxy http://USER:PASS@HOST:PORT
```

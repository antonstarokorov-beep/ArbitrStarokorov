import logging
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Stage(Enum):
    WAIT_DEBT = auto()
    WAIT_PROPERTY = auto()
    WAIT_INCOME = auto()
    WAIT_CHILDREN = auto()
    WAIT_DECISION = auto()
    WAIT_PASSPORT = auto()
    WAIT_PHONE = auto()
    DONE = auto()


@dataclass
class ClientState:
    stage: Stage = Stage.WAIT_DEBT
    debt: Optional[str] = None
    property_info: Optional[str] = None
    income_info: Optional[str] = None
    children_info: Optional[str] = None
    decision_info: Optional[str] = None
    passport_photos_count: int = 0
    phone: Optional[str] = None
    notes: Dict[str, str] = field(default_factory=dict)


clients: Dict[int, ClientState] = {}


START_TEXT = (
    "Здравствуйте! Я помощник Антона Старокорова.\n"
    "Помогу понять, подходит ли банкротство в вашей ситуации.\n\n"
    "Подскажите, пожалуйста, какая у вас сейчас общая сумма долга?"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.message is None:
        return

    clients[update.effective_user.id] = ClientState()
    await update.message.reply_text(START_TEXT)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    state = clients.setdefault(user_id, ClientState())

    if update.message.photo:
        await handle_photo(update, state)
        return

    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Напишите, пожалуйста, ответ текстом. 🙏")
        return

    if state.stage == Stage.WAIT_DEBT:
        state.debt = text
        debt_number = extract_number(text)

        if debt_number and 250_000 <= debt_number <= 380_000:
            await update.message.reply_text(
                "Формально с таким долгом банкротство возможно.\n"
                "Важно: услуги стоят 240 000 ₽.\n"
                "Но помните — платежи банкам часто уходят в штрафы и пени, и долг растет.\n"
                "Банкротство — это точка в этом процессе."
            )
        else:
            await update.message.reply_text(
                "Понял вас. Спасибо, что поделились.\n"
                "Чем раньше разберемся, тем меньше переплатите на штрафах и пенях."
            )

        state.stage = Stage.WAIT_PROPERTY
        await update.message.reply_text(
            "Подскажите, есть ли у вас имущество: недвижимость, авто, доли?\n"
            "И есть ли совместно нажитое имущество в браке?"
        )
        return

    if state.stage == Stage.WAIT_PROPERTY:
        state.property_info = text
        state.stage = Stage.WAIT_INCOME
        await update.message.reply_text(
            "Спасибо. Теперь подскажите ваш ежемесячный доход (примерно) и регион проживания.\n"
            "Нужно сравнить с прожиточным минимумом."
        )
        return

    if state.stage == Stage.WAIT_INCOME:
        state.income_info = text
        state.stage = Stage.WAIT_CHILDREN
        await update.message.reply_text(
            "Есть ли у вас несовершеннолетние дети? Если да — сколько?"
        )
        return

    if state.stage == Stage.WAIT_CHILDREN:
        state.children_info = text
        state.stage = Stage.WAIT_DECISION

        await update.message.reply_text(
            "По вашему описанию объясню честно:\n"
            "— если есть ликвидное имущество, его нужно заранее оценить по рискам;\n"
            "— при доходе выше прожиточного минимума возможны удержания части суммы.\n\n"
            "Но альтернатива обычно хуже: бесконечные проценты, штрафы и рост долга."
        )
        await update.message.reply_text(
            "По условиям работы:\n"
            "• Стоимость сопровождения: 245 000 ₽\n"
            "• Скидка здесь в чате: 5 000 ₽\n"
            "• Рассрочка: 20 000 ₽/мес на 12 месяцев\n"
            "(часто это меньше одного платежа по кредиту).\n\n"
            "Если готовы, напишите: «Готов(а) оформить»."
        )
        return

    if state.stage == Stage.WAIT_DECISION:
        state.decision_info = text
        if "готов" in text.lower() or "оформ" in text.lower() or "да" == text.lower():
            state.stage = Stage.WAIT_PASSPORT
            await update.message.reply_text(
                "Отлично 🤝\n"
                "Пришлите, пожалуйста, фото паспорта:\n"
                "1) главный разворот\n"
                "2) страница с пропиской"
            )
            return

        await update.message.reply_text(
            "Понимаю ваши сомнения.\n"
            "Обычно в ожидании долг растет из-за штрафов и пеней, а платежи уходят «в пустоту».\n"
            "Когда будете готовы — напишите «Готов(а) оформить», и начнем."
        )
        return

    if state.stage == Stage.WAIT_PASSPORT:
        await update.message.reply_text(
            "Жду фото паспорта (главный разворот + прописка)."
        )
        return

    if state.stage == Stage.WAIT_PHONE:
        state.phone = text
        state.stage = Stage.DONE
        await update.message.reply_text(
            "Данные принял! Я закрепил за вашим делом опытного юриста из моей компании «Иджис». "
            "Он свяжется с вами в ближайшее время для сбора документов и подготовки заявления в суд."
        )
        await update.message.reply_text(
            "Если возникнут срочные вопросы, вы всегда можете позвонить мне лично: 89235031985"
        )
        return

    if state.stage == Stage.DONE:
        await update.message.reply_text(
            "Мы уже получили данные. Если хотите, можете написать дополнительный вопрос здесь."
        )


async def handle_photo(update: Update, state: ClientState) -> None:
    if update.message is None:
        return

    if state.stage != Stage.WAIT_PASSPORT:
        await update.message.reply_text("Фото получил. Если нужно, продолжим по анкете текстом 🙂")
        return

    state.passport_photos_count += 1

    if state.passport_photos_count < 2:
        await update.message.reply_text("Фото получил. Пришлите, пожалуйста, вторую страницу (прописка).")
        return

    state.stage = Stage.WAIT_PHONE
    await update.message.reply_text("Отлично, фото получил. Теперь отправьте ваш номер телефона для договора.")


def extract_number(text: str) -> Optional[int]:
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден TELEGRAM_BOT_TOKEN. Укажите токен в переменной окружения и перезапустите бота."
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

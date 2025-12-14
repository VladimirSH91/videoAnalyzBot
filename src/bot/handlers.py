import logging
from typing import cast

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from db import async_database_session_maker
from nlq.schemas import QueryIntent
from nlq.rule_based_intent import parse_intent_rule_based
from nlq.service import execute_intent

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a video analysis bot!")

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    """
    await message.answer(help_text)


@router.message()
async def nlq_message_handler(message: Message) -> None:
    if not message.text:
        await message.answer("Пожалуйста, пришли текстовый запрос.")
        return

    try:
        intent = QueryIntent.model_validate_json(message.text)
    except ValueError:
        try:
            intent = parse_intent_rule_based(message.text)
        except ValueError:
            logger.exception("NLQ parse error")
            await message.answer(
                "Не смог распознать запрос. "
                "Попробуй переформулировать или пришли JSON-intent по схеме. "
                "Поддерживаемые примеры: 'сколько видео в системе', 'просмотры за 7 дней', 'лайки вчера', 'комментарии 01.11.2025-28.11.2025'."
            )
            return

    async with async_database_session_maker() as session:
        value = await execute_intent(cast(AsyncSession, session), intent)

    await message.answer(str(value))

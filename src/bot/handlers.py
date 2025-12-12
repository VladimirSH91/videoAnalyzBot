from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

router = Router()

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

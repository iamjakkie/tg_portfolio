import asyncio
import telebot.async_telebot
import os

from bot import handlers

async def check(tb, am):
    await asyncio.sleep(5)
    while True:
        try:
            
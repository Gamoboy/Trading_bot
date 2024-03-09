import os
from dotenv import load_dotenv

from telethon import events
from telethon.sync import TelegramClient

import asyncio
from aiogram import Bot, Dispatcher, types, executor


load_dotenv()


class Listener:
    def __init__(self):
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.group = os.getenv('TELEGRAM_GROUP')
        self.full_info = None

        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        self.client.start()

    def start_listening(self, func):
        print(f"Listening on {self.group} : ")

        @self.client.on(events.NewMessage(chats=self.group))
        async def new_message_listener(event):
            sender = event.sender
            sender = f"First_name: {sender.first_name}, Last_name: {sender.last_name}, Username: {sender.username}, Phone: {sender.phone}"
            msg = event.raw_text
            date = event.date
            reply_to = event.reply_to

            msg = msg.replace("\n", ' ')
            self.full_info = f"Text: {msg}\nBy: \n{sender}\nDate: {date}\nReply_to: {reply_to}"
            print("Message received")
            print(f"Bot : {await func(self.full_info)}")

        self.client.run_until_disconnected()

    def get_conv_list(self):
        conv_list = []
        for dialog in self.client.iter_dialogs():
            conv_list.append({
                "id": dialog.id,
                "name": dialog.name,
                "type": type(dialog.entity).__name__
            })
        return conv_list


class TradingBot:
    def __init__(self):
        self.chat_id = int(os.getenv("CHAT_ID"))
        self.token = os.getenv("BOT_API_TOKEN")
        self.bot = Bot(self.token)
        self.dp = Dispatcher(self.bot)

    async def send_message(self, msg):
        await self.bot.send_message(self.chat_id, msg)

    async def start_command(self, message: types.Message):
        await message.reply("Bonjour! Je suis votre bot de trading.")

    async def help_command(self, message: types.Message):
        await message.reply("Voici comment vous pouvez utiliser ce bot...")

    def register_handlers(self):
        self.dp.register_message_handler(self.start_command, commands=["start"])
        self.dp.register_message_handler(self.help_command, commands=["help"])

    def start_listening(self):
        self.register_handlers()
        executor.start_polling(self.dp, skip_updates=True)



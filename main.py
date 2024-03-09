from Telegram import *
from Processing import *

import asyncio


if __name__ == '__main__':
    listener = Listener()
    processing = Processing()
    bot = TradingBot()

    asyncio.run(listener.start_listening(processing.request))
    bot.start_listening()
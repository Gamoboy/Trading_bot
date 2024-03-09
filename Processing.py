import os
from dotenv import load_dotenv
from time import *
import json
import asyncio

from openai import OpenAI
import openai

from Broker import Broker
from Telegram import TradingBot

load_dotenv()


class Processing:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")

        openai.api_key = self.api_key
        self.client = OpenAI()
        self.thread = self.client.beta.threads.create()

        self.messages = None
        self.message = None
        self.run = None

        self.broker = Broker()
        self.place_order = self.broker.place_order

        self.bot = TradingBot()

    def add_message(self, msg):
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=msg
        )
        return self.message

    async def request(self, msg):
        self.add_message(msg)
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id,
        )
        self.run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )

        print("Request sent")

        while True:
            if not self.run.status == "in_progress":
                if self.run.status == "failed":
                    print(self.run.last_error)
                    break
                elif self.run.status == "requires_action":
                    function = self.run.required_action.submit_tool_outputs.tool_calls[0].function
                    tool_call_id = self.run.required_action.submit_tool_outputs.tool_calls[0].id
                    return await self.call_function(function, tool_call_id, msg)
                else:
                    print(self.run.status)
                    self.update_messages()
                    last_msg = self.get_last_message()
                    self.messages.data[0].content[0] = []
                    return last_msg
            else:
                self.run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )
                sleep(3)

    def update_messages(self):
        self.messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

    def get_last_message(self):
        return self.messages.data[0].content[0].text.value

    async def call_function(self, function, tool_call_id, full_info):
        function_call = {
            "name": function.name,
            "arguments": function.arguments
        }
        args = json.loads(function_call["arguments"])
        func_to_call = getattr(self, function_call["name"])
        result = func_to_call(**args)

        self.run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call_id,
                    "output": result,
                }
            ]
        )
        self.update_messages()

        while True:
            self.run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=self.run.id
            )

            if not self.run.status == "in_progress":
                self.update_messages()
                last_msg = self.get_last_message()
                self.messages.data[0].content[0] = []
                await self.bot.send_message \
                    (f"MESSAGE : \n"
                     "\n"
                     f"{full_info}\n"
                     "\n"
                     f"OUTPUT: \n"
                     "\n"
                     f"{json.loads(result)['data']['output']}\n"
                     "\n"
                     f"BOT: \n"
                     "\n"
                     f"{last_msg}")
                return last_msg
            else:
                sleep(3)

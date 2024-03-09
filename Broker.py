import json
import asyncio

from Telegram import TradingBot


class Broker:
    def __init__(self):
        None

    def place_order(self, pair, direction, entry, tps, sl):
        if direction == "sell":
            if not sl > entry:
                return json.dumps({
                    "success": "false",
                    "data": {
                        "output": "ERROR: the stop loss is not above the entry point"
                    }
                })
            for tp in tps:
                if not tp < entry:
                    return json.dumps({
                        "status": "false",
                        "data": {
                            "output": "ERROR: One of the take profit is not below the entry point"
                        }
                    })
        else:
            if not sl < entry:
                return json.dumps({
                    "status": "false",
                    "data": {
                        "output": "ERROR: the stop loss is not below the entry point"
                    }
                })
            for tp in tps:
                if not tp > entry:
                    return json.dumps({
                        "status": "false",
                        "data": {
                            "output": "ERROR: One of the take profit is not above the entry point"
                        }
                    })

        print(f"{direction} placed on {pair} | ENTRY: {entry} TPs: {tps} SL: {sl}")
        return json.dumps({
            "status": "success",
            "data": {
                "output": f"{direction} placed on {pair} | ENTRY: {entry} TPs: {tps} SL: {sl}"
            }
        })
import asyncio
import websockets
import json
import pandas as pd


instruments_msg = \
{
  "jsonrpc": "2.0",
  "id": 7617,
  "method": "public/get_instruments",
  "params": {
    "currency": "ETH",
    "kind": "option",
    "expired": False
  }
}

lastTrades = \
{
  "jsonrpc": "2.0",
  "id": 9267,
  "method": "public/get_last_trades_by_instrument",
  "params": {
    "instrument_name": "a",
    "count": 1000,
    "include_old": True,
    "sorting": "desc"
  }
}


async def call_api(msg, lastTrades):
    async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        response = json.loads(response)

        instruments = []

        for i in range(len(response["result"])):
           instruments.append(response["result"][i]["instrument_name"])

        history = []
        for i in range(len(instruments)):
            a = json.loads(lastTrades)
            a["params"]["instrument_name"] = instruments[i]
            a = json.dumps(a)
            await websocket.send(a)
            response = await websocket.recv()
            response = json.loads(response)
            buy = 0
            sell = 0
            for j in range(len(response["result"]["trades"])):
                if response["result"]["trades"][j]["direction"] == "sell":
                    sell += int(response["result"]["trades"][j]["amount"])

                elif response["result"]["trades"][j]["direction"] == "buy":
                    buy += int(response["result"]["trades"][j]["amount"])

            temp = [instruments[i], buy, sell]
            history.append(temp)
            print("{0} : {1}".format(i, len(instruments)))
        df = pd.DataFrame(history,  columns=["Instrument", "Buys", "Sells"])
        df.to_csv("deribitETH.csv", index=False, header=True)


asyncio.get_event_loop().run_until_complete(call_api(json.dumps(instruments_msg), json.dumps(lastTrades)))
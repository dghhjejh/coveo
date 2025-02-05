#!/usr/bin/env python

import asyncio
import dataclasses
import json
import os
import traceback

import websockets

from bot import Bot
from game_message import TeamGameState


async def run():
    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri, max_size=None) as websocket:
        bot = Bot()
        if "TOKEN" in os.environ:
            await websocket.send(
                json.dumps({"type": "REGISTER", "token": os.environ["TOKEN"]})
            )
        else:
            await websocket.send(
                json.dumps({"type": "REGISTER", "teamName": "MyPythonicBot"})
            )

        await game_loop(websocket=websocket, bot=bot)


async def game_loop(websocket: websockets.WebSocketServerProtocol, bot: Bot):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            # Connection is closed, the game is probably over
            print("Websocket was closed.")
            break
        print(f"Received message: {message}")
        game_message: TeamGameState = TeamGameState.from_json(message)
        print(f"Playing tick {game_message.tick}")

        if game_message.lastTickErrors:
            print(f"Errors during last tick : {game_message.lastTickErrors}")

        actions = []

        # Just so your bot doesn't completely crash. ;)
        try:
            actions = bot.get_next_move(game_message)
        except Exception:
            print("Exception while getting next moves:")
            print(traceback.format_exc())

        payload = {
            "type": "COMMAND",
            "tick": game_message.tick,
            "actions": [dataclasses.asdict(action) for action in actions],
        }

        print(json.dumps(payload))

        await websocket.send(json.dumps(payload))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())

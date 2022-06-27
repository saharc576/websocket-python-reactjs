import asyncio
import json
import logging

import websockets
import scraper
import redis
logging.basicConfig(format='[%(levelname)s] %(message)s', datefmt='%H:%M:%S', level="INFO")
logger = logging.getLogger()
r = redis.Redis(host="localhost", port=6379, db=0)


def change_sport_handler(sport):
    # verify that this sport exist in redis.
    key = f"{sport}_live_data"
    value = r.get(key)
    if not value:
        scraper_by_sport = scraper.LiveScoresParser(sport_name=sport)
        scraper_by_sport.run()


def dispatcher(message, sport):
    scraper_by_sport = scraper.LiveScoresParser(sport_name=sport)
    request_handler_map = {
        "refresh data": scraper_by_sport.run,
        "change to": lambda: change_sport_handler(sport=sport)
    }
    # load the data to redis
    func = request_handler_map.get(message)
    if func:
        func()
        key = f"{sport}_live_data"
        value = r.get(key)
        if value:
            return value.decode()
    return "ERROR"


async def echo(websocket):
    async for message in websocket:
        req, sport = message.split("@")
        logger.info(f"message from client: request={req}, sport={sport}")
        result = dispatcher(message=req, sport=sport)
        await websocket.send(result)


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())

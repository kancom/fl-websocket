import asyncio
import concurrent.futures
import json
import os
from typing import Dict

import aiohttp
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY

from auth import CypherRSA
from models.main_model import Base, ExchRsp

CMD_EXIT = "exit"
DB_NAME = os.getenv("POSTGRES_DB", "prop_db")
DB_USER = os.getenv("POSTGRES_USER", "prop_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postpass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_DSN = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
WS_URL = "wss://38.65.23.109:8081"
HB_ITVL = 5
VRF_SSL = False
WS_TIMEOUT = None

# logger.add(sys.stderr, level="DEBUG")
AUTH_DATA = {"login": "WEBSOCKET", "password": "Trellus1", "firm": "TREL"}
CANNED_MSGS = {
    "auth": {"type": "challenge"},
    "login": {
        "type": "login",
        "userid": AUTH_DATA["login"],
        "firm": AUTH_DATA["firm"],
        "pass": None,
    },
}
cypher_obj = CypherRSA()


def serialize(msg: Dict) -> str:
    s = json.dumps(msg)
    logger.debug(s)
    return s


def deserialize(msg: str) -> Dict:
    s = json.loads(msg)
    logger.debug(s)
    return s


async def ws_receive(ws: aiohttp.ClientWebSocketResponse, db):
    rsp = await ws.receive(WS_TIMEOUT)
    await write_data_db(deserialize(rsp.data), db)
    return rsp


async def authenticate(ws: aiohttp.ClientWebSocketResponse, db) -> bool:
    await ws.send_json(CANNED_MSGS["auth"])
    rsp = await ws_receive(ws, db)
    s: Dict = deserialize(rsp.data)
    assert s.get("result", "nOK") == "OK"
    cypher_obj.set_pubkey(s.get("key"))
    enc_pass = cypher_obj.encrypt(AUTH_DATA["password"])
    msg = CANNED_MSGS["login"]
    msg["pass"] = enc_pass
    await ws.send_json(msg)
    rsp = await ws_receive(ws, db)
    s: Dict = deserialize(rsp.data)
    result = s.get("result", "nOK") == "OK"
    return result


async def write_data_db(data: str, db):
    await db.execute(ExchRsp.__table__.insert().values(data=data))


async def connect_ws():
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(WS_URL, heartbeat=HB_ITVL, verify_ssl=VRF_SSL)
    return ws


async def connect_db():
    engine = create_engine(DB_DSN, strategy=ASYNCIO_STRATEGY)
    await engine.run_in_thread(Base.metadata.create_all, engine.sync_engine)
    connection = await engine.connect()

    # result = await connection.execute(ExchRsp.__table__.select())
    # d_records = await result.fetchall()
    # print(d_records)

    return connection


def get_cmd():
    cmd = input("Enter cmd> ")
    return cmd


async def send_cmd(cmd: str, ws: aiohttp.ClientWebSocketResponse):
    await ws.send_json(cmd)


async def main(*args):
    loop = asyncio.get_running_loop()
    connection_db = await connect_db()
    if not connection_db:
        raise Exception("Failed to connect to DB!")
    logger.debug(f"Connected to DB {DB_DSN}")
    connection_ws = await connect_ws()
    if not connection_ws:
        raise Exception("Failed to connect to ws!")
    logger.debug(f"Connected to ws {WS_URL}")
    isauthed = await authenticate(connection_ws, connection_db)
    if not isauthed:
        raise Exception("Failed to authenticate")
    cmd = None
    while True:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            cmd = await loop.run_in_executor(pool, get_cmd)
            # cmd = await loop.run_in_executor(None, get_cmd)
            if cmd and cmd == CMD_EXIT:
                await connection_ws.close()
                break
            if cmd:
                await send_cmd(cmd, connection_ws)
        await ws_receive(connection_ws, connection_db)
    logger.debug("Leaving...")
    if not connection_ws.closed:
        await connection_ws.close()
    await connection_db.close()


if __name__ == "__main__":
    asyncio.run(main())

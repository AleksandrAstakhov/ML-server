import aiohttp
import asyncio
from common_data import base_url, predict_data

model_names = ["rf_long", "svc_long", "rf_async", "svc_async"]


async def load_model(session, name):
    r = await session.post(f"{base_url}/load", json={"name": name})
    if r.status == 200:
        print(f"{name} loaded.")
        return True
    print(f"Failed to load {name}: {await r.text()}")
    return False


async def predict_model(session, name):
    r = await session.post(
        f"{base_url}/predict",
        json={"name": name, **predict_data},
    )
    if r.status == 200:
        result = await r.json()
        print(f"{name} predictions:", result["predictions"])
    else:
        print(f"{name} prediction error:", await r.text())


async def handle(name):
    async with aiohttp.ClientSession() as session:
        if await load_model(session, name):
            await predict_model(session, name)


async def main():
    await asyncio.gather(*(handle(name) for name in model_names))


asyncio.run(main())

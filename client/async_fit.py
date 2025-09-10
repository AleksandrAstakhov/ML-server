import aiohttp
import asyncio
import time
from data import URL, data

models = [
    {"name": "rf_async", "kind": "rf", "params": {"n_estimators": 100}},
    {"name": "svc_async", "kind": "svc", "params": {"kernel": "rbf", "C": 1.0}},
]


async def train_model(session, model):
    url = f"{URL}/fit"
    async with session.post(url, json={**model, **data}) as response:
        text = await response.text()
        print(f"{model['name']} => {response.status} | {text}")


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [train_model(session, model) for model in models]
        await asyncio.gather(*tasks)


start = time.time()
asyncio.run(main())

print("Async training finished in:", time.time() - start, "seconds")

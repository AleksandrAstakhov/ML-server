from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Literal, Union, Any
from dotenv import load_dotenv
import asyncio
import joblib
import os
import multiprocessing as mp
import traceback

load_dotenv()
app = FastAPI()

MODELS_DIR = os.environ.get("MODELS_DIR", "./models")
MAX_CORES = int(os.environ.get("MAX_CORES", "4"))
MAX_LOADED = int(os.environ.get("MAX_LOADED", "3"))

# ---------------- Pydantic Schemas ---------------- #


class FitRequest(BaseModel):
    name: str
    kind: Literal["logreg", "rf", "svc"]
    params: Dict[str, Any]
    X: List[List[float]]
    y: List[Union[int, float]]


class ModelNameRequest(BaseModel):
    name: str


class PredictRequest(ModelNameRequest):
    X: List[List[float]]


# ---------------- Async Model Registry ---------------- #


class AsyncModelsRegistry:
    def __init__(self, path: str, max_loaded: int):
        self.path = path
        self.max_loaded = max_loaded
        self.loaded_count = 0
        self.models: Dict[str, object] = {}
        self.lock = asyncio.Lock()
        self.pool = asyncio.Semaphore(MAX_CORES - 1)

    async def load_model(self, name: str):
        async with self.lock:
            if name in self.models:
                return
            if self.loaded_count >= self.max_loaded:
                raise ValueError("Model limit reached")

            model_path = os.path.join(self.path, f"{name}.joblib")
            if not os.path.exists(model_path):
                raise ValueError("Model not found")

            self.models[name] = joblib.load(model_path)
            self.loaded_count += 1

    async def save_model(self, name: str, model):
        async with self.lock:
            os.makedirs(self.path, exist_ok=True)

            model_path = os.path.join(self.path, f"{name}.joblib")

            if os.path.exists(model_path):
                raise ValueError("Model already exists")

            joblib.dump(model, model_path)

    async def unload_model(self, name: str):
        async with self.lock:
            if name in self.models:
                del self.models[name]
                self.loaded_count -= 1

    def model_exist(self, name: str) -> bool:
        return name in self.models or os.path.exists(
            os.path.join(self.path, f"{name}.joblib")
        )

    async def is_loaded(self, name: str) -> bool:
        async with self.lock:
            return name in self.models

    async def remove_model(self, name: str):
        async with self.lock:
            model_path = os.path.join(self.path, f"{name}.joblib")
            if os.path.exists(model_path):
                os.remove(model_path)

    async def remove_all(self):
        async with self.lock:
            for fname in os.listdir(self.path):
                if fname.endswith(".joblib"):
                    os.remove(os.path.join(self.path, fname))
            self.models.clear()
            self.loaded_count = 0

    async def get_model(self, name):
        async with self.lock:
            return self.models[name]


registry = AsyncModelsRegistry(MODELS_DIR, MAX_LOADED)

# ---------------- Worker Function ---------------- #


def worker(req_dict: dict, conn):
    try:
        kind = req_dict["kind"]
        if kind == "logreg":
            from sklearn.linear_model import LogisticRegression

            model = LogisticRegression(**req_dict["params"])
        elif kind == "rf":
            from sklearn.ensemble import RandomForestClassifier

            model = RandomForestClassifier(**req_dict["params"])
        elif kind == "svc":
            from sklearn.svm import SVC

            model = SVC(**req_dict["params"])
        else:
            raise ValueError(f"Unsupported kind: {kind}")

        model.fit(req_dict["X"], req_dict["y"])

        model_path = os.path.join(MODELS_DIR, f"{req_dict['name']}.joblib")
        joblib.dump(model, model_path)

        conn.send("ok")
    except Exception as ex:
        conn.send(f"error: {ex}\n{traceback.format_exc()}")
    finally:
        conn.close()


# ----- Fit Endpoint ----- #
@app.post("/fit")
def fit(req: FitRequest):
    if os.path.exists(os.path.join(MODELS_DIR, f"{req.name}.joblib")):
        raise HTTPException(
            status_code=400, detail="Model with this name already exists"
        )

    parent_conn, child_conn = mp.Pipe()
    p = mp.Process(target=worker, args=(req.dict(), child_conn))
    p.start()
    p.join()

    result = parent_conn.recv()
    if result != "ok":
        raise HTTPException(status_code=500, detail=result)

    return {"status": "success", "message": f"Model '{req.name}' trained and saved"}


@app.post("/load")
async def load(req: ModelNameRequest):
    try:
        await registry.load_model(req.name)
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"loaded": True}


@app.post("/unload")
async def unload(req: ModelNameRequest):
    await registry.unload_model(req.name)
    return {"unloaded": True}


@app.post("/predict")
async def predict(req: PredictRequest):
    if not await registry.is_loaded(req.name):
        raise HTTPException(404, "Model not loaded")
    model = await registry.get_model(req.name)
    preds = model.predict(req.X).tolist()
    return {"predictions": preds}


@app.delete("/remove")
async def remove(req: ModelNameRequest):
    if await registry.is_loaded(req.name):
        raise HTTPException(400, "Unload model first")
    if not registry.model_exist(req.name):
        raise HTTPException(404, "No such model on disk")
    await registry.remove_model(req.name)
    return {"removed": req.name}


@app.delete("/remove_all")
async def remove_all():
    await registry.remove_all()
    return {"status": "all removed"}

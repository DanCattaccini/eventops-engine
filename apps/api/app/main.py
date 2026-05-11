from fastapi import FastAPI

from app.routers.v1 import events as events_v1

app = FastAPI(title="EventOps API", version="1.0.0")

app.include_router(events_v1.router)


@app.get("/")
def root():
    return {"service": "eventops-api", "status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

from fastapi import FastAPI

app = FastAPI(title ="EventOps API", version="0.1.0")

@app.get("/")
def root():
    return {"service": "eventops-api", "status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

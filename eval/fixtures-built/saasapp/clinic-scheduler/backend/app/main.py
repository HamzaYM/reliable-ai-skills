from fastapi import FastAPI

app = FastAPI(title="clinic-scheduler")


@app.get("/health")
def health():
    return {"ok": True}

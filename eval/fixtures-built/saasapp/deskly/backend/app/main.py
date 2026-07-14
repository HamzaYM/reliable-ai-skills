from fastapi import FastAPI

app = FastAPI(title="deskly")


@app.get("/health")
def health():
    return {"ok": True}

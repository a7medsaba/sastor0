# main.py
from fastapi import FastAPI
import os
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port)

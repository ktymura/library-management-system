from fastapi import FastAPI

app = FastAPI(title="MTO App")


@app.get("/health")
def health():
    return {"status": "ok"}

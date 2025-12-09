from fastapi import FastAPI

app = FastAPI(title="Library Management System App")


@app.get("/health")
def health():
    return {"status": "ok"}

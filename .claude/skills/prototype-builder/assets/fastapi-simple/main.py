from fastapi import FastAPI

app = FastAPI(title="API Server")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Hello World"}


# Add your endpoints below

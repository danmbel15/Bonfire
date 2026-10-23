from fastapi import FastAPI

app = FastAPI(title="Bonfire")


@app.get("/")
def read_root():
    return {
        "project": "Bonfire",
        "version": "0.1.0",
        "message": "Bonfire is running!"  
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

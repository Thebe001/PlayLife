from fastapi import FastAPI

app = FastAPI(title="LifeForge OS API")


@app.get("/")
def root():
    return {"message": "LifeForge OS backend running"}